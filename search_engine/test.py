import logging
import unittest

from search_engine.search_engine import SearchEngine


class TestSearchEngine(unittest.TestCase):

    def process_reques(self, request):
        response = SearchEngine.search(request)
        res_count = len(response.dock_ids)
        logging.info(f"Result count for request '{request}' is: {res_count}")
        return res_count

    def test_empty_result(self):
        res_count = self.process_reques("война")
        self.assertNotEqual(0, res_count)

        res_count = self.process_reques("война ! война")
        self.assertEquals(0, res_count)

    def test_fullness_result(self):
        res_count_full = self.process_reques("война || мир")
        self.assertNotEqual(0, res_count_full)

        res_count_intersect = self.process_reques("война мир")
        self.assertNotEqual(0, res_count_intersect)

        res_count_without_world = self.process_reques("война ! мир")
        self.assertNotEqual(0, res_count_without_world)

        res_count_without_war = self.process_reques("мир ! война")
        self.assertNotEqual(0, res_count_without_war)

        self.assertEquals(
            res_count_full,
            res_count_intersect + res_count_without_war +
            res_count_without_world)

    def test_without_repeat(self):
        res_count_one = self.process_reques("война")
        self.assertNotEqual(0, res_count_one)

        res_count_intersect = self.process_reques("война война")
        self.assertEquals(res_count_one, res_count_intersect)

        res_count_or = self.process_reques("война || война")
        self.assertEquals(res_count_one, res_count_or)
