import unittest
import requests
from UrlRequests import UrlRequests


class TestWeather(unittest.TestCase):
    def setUp(self):
        self.weather = UrlRequests()

    def test_return_value(self):
        self.assertTrue(type(self.weather.get_weather()) == str)

    def test_url_200(self):
        r = requests.get(self.weather.request_url_weather)
        self.assertEqual(r.status_code, 200)

    def test_return(self):
        self.assertNotEqual(self.weather.get_weather(), '')

    # @mock.patch('Shushushu.Weather.TOKEN', new='123')
    # def test_bad_url(self):
    #     self.assertEqual(self.weather.get_weather(), 'Не удалось перевести.')


if __name__ == '__main__':
    unittest.main()
