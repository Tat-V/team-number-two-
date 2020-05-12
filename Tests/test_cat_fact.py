import unittest
import requests
from UrlRequests import UrlRequests


class TestCatFact(unittest.TestCase):
    def test_request(self):
        r = requests.get('https://cat-fact.herokuapp.com/facts')
        self.assertEqual(r.status_code, 200)

    def test_return_value(self):
        self.assertEqual(type(UrlRequests.get_cat_fact()), str)


if __name__ == '__main__':
    unittest.main()
