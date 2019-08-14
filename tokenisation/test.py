import os
import json
import pickle
import unittest
import logging
import sys


class TestTokenisation(unittest.TestCase):

    LOGGING_INTERVAL = 500

    @classmethod
    def setUp(cls):
        data_folder = os.path.join(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), '..')), 'data')
        cls.INPUT_FILE = os.path.join(data_folder, 'preprocessing.out')
        cls.TOKENISATION_FILE = os.path.join(data_folder, 'tokenisation.out')
        cls.PAGE_COUNT = 50000

    def test_correct_data(self):
        pages_id = [1, 1000, 10000, 30000, 40000]
        logging.debug("Start testing tokenisation stage")
        random_pages = None
        random_tokens = None
        with open(self.INPUT_FILE, encoding='utf-8') as in_:
            pages = json.load(in_)
            random_pages = {pages[i - 1]["id"]: pages[i - 1] for i in pages_id}
        with open(self.TOKENISATION_FILE, 'rb') as in_:
            tokens = pickle.load(in_)
            random_tokens = {key: value
                             for key, value in tokens.items()
                             if value["id"] in pages_id}
        for title, page in random_tokens.items():
            token_count = 0
            logging.debug(f"Testing with page {page['id']}")
            for token in page["tokens"]:
                if token_count % self.LOGGING_INTERVAL == 0:
                    logging.debug(f"Process {token_count} token")
                with self.subTest(
                        token=sys.intern(token[0]), page_title=title):
                    self.assertEqual(
                        page["id"], random_pages[page["id"]]["id"])
                    self.assertEqual(
                        title, random_pages[page["id"]]["title"])
                    text = random_pages[page["id"]]["text"]
                    self.assertIn(sys.intern(token[0]), text)
                token_count += 1


if __name__ == "__main__":
    unittest.main()
