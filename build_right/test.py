import os
import hashlib
import logging
import unittest
import pickle


LOGGING_INTERVAL = 100


class TestBuildingIndex(unittest.TestCase):

    @classmethod
    def setUp(cls):
        data_folder = os.path.join(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), '..')), 'data')
        cls.INPUT_FILE = os.path.join(data_folder, 'tokenisation.out')
        cls.INVERSE_FILE = os.path.join(data_folder, 'inverse.out')
        cls.DICT_FILE = os.path.join(data_folder, 'dict.out')
        cls.SIZE_OF_RECORD = 40
        cls.PAGES_INDS = range(1, 50001, 2500)

    def read_dock_ids(self, dict_, offset, count):
        dict_.seek(offset)
        docks = dict_.read(count * 4)
        start = 0
        dock_ids = []
        for i in range(count):
            dock_ids.append(
                int.from_bytes(docks[start:start + 2], byteorder='big'))
            int.from_bytes(docks[start + 2: start + 4], byteorder='big')
            start += 4
        return dock_ids

    def check_token_in_page(
            self, tokens, page_id, title, index, dict_):
        found_counter = 0
        while True:
            data = index.read(self.SIZE_OF_RECORD)
            if not data:
                break
            token = data[:32].decode("utf-8")
            if token in tokens:
                offset = int.from_bytes(data[32:36], byteorder='big')
                count = int.from_bytes(data[36:40], byteorder='big')
                with self.subTest(
                        token=token, page_id=page_id, page_title=title):
                    self.assertIn(
                        page_id, self.read_dock_ids(dict_, offset, count))
                    found_counter += 1
        self.assertEqual(
            found_counter, len(tokens), msg="Not all tokens were found!")

    def test_make_inverse_index(self):
        logging.debug("Start testing inverse index")
        with open(self.INPUT_FILE, 'rb') as in_:
            logging.debug("Loading checked tokenised data ...")
            pages = pickle.load(in_)
            pages_keys = list(pages.keys())
            logging.debug(f"Loaded {len(pages_keys)} pages")
            keys = [pages_keys[page_ind]
                    for page_ind in range(len(pages))
                    if page_ind in self.PAGES_INDS]
            logging.debug(f"Choisen pages for testing: {keys}")
        tokens_count = len(
            [token[0] for title in keys for token in pages[title]["tokens"]])
        logging.debug(f"Total count of tokens: {tokens_count}")
        cur_token_count = 1
        page_cur_count = 1
        with open(self.INVERSE_FILE, 'rb') as index, \
                open(self.DICT_FILE, 'rb') as dict_:
            logging.debug("Start circle of testing")
            for key in keys:
                page_tokens = {hashlib.md5(
                               t[0].decode().lower().encode()).hexdigest()
                               for t in pages[key]["tokens"]}
                logging.debug(
                    f"Testing token with number {cur_token_count} "
                    f"from {tokens_count}. Page number "
                    f"{page_cur_count} from {len(self.PAGES_INDS)}")
                self.check_token_in_page(
                    page_tokens,
                    pages[key]["id"], key,
                    index, dict_)
                index.seek(0)
                dict_.seek(0)
                cur_token_count += len(page_tokens)
            page_cur_count += 1
