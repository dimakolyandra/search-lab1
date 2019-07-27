import os
import random
import json
import pickle
import unittest


class TestTokenisation(unittest.TestCase):

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
        pages_id = random.choices(range(self.PAGE_COUNT), k=5)
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
            for token in page["tokens"]:
                with self.subTest(token=token, page_title=title):
                    self.assertEqual(
                        page["id"], random_pages[page["id"]]["id"])
                    self.assertEqual(
                        title, random_pages[page["id"]]["title"])
                    text = random_pages[page["id"]]["text"]
                    self.assertIn(token[0], text)


if __name__ == "__main__":
    unittest.main()
