# -*- coding: utf-8 -*-
import datetime
import unittest
import os
import requests
from typing import List, Any
from unittest import mock
from unittest.mock import patch
from Shushushu import LOG_ACTIONS, log_action, decorator_error
from Shushushu import SpeechToText
from Shushushu import fact
from Shushushu import UrlRequests
from io import StringIO

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'path_to_your_.json_credential_file'



TOKEN = 'd081cc3b0aa6fbb8e8f24d1a8216be49'
CITY = 'Nizhny Novgorod'


@log_action
def useless_function(update):
    return None


class TestLogging(unittest.TestCase):
    def setUp(self) -> None:
        self.update = mock.MagicMock()

    def tearDown(self) -> None:
        global LOG_ACTIONS
        LOG_ACTIONS = []

    def test_log_action(self):
        self.update.message.text = 'something important'
        self.update.effective_user.first_name = 'meaningless name'
        self.update.message.chat.id = 'some long integer'
        useless_function(self.update)
        self.assertEqual(LOG_ACTIONS, [{'user': 'meaningless name', 'user id': 'some long integer',
                                        'function': 'useless_function',
                                        'message': 'something important',
                                        'time': datetime.datetime.now().strftime("%Y-%m-%d %H.%M")}])

    def test_if_none(self):
        self.update = None
        useless_function(self.update)
        self.assertEqual(LOG_ACTIONS, [])

    def test_if_no_message(self):
        self.update = mock.MagicMock(spec=['effective_user'])
        useless_function(self.update)
        self.assertEqual(LOG_ACTIONS, [])

    def test_if_no_user(self):
        self.update = mock.MagicMock(spec=['message'])
        useless_function(self.update)
        self.assertEqual(LOG_ACTIONS, [])

    def test_no_update(self):
        with self.assertRaises(IndexError):
            useless_function()


class TestSpeechToText(unittest.TestCase):
    def setUp(self):
        self.speechtotext = SpeechToText('.\data_files\Test_Sound.wav')

    def tearDown(self):
        self.speechtotext.local_file_path = None

    def test_translate_audio(self):
        transcription = self.speechtotext.sample_recognize()
        correct_transcription = 'Уважаемые пассажиры просьба соблюдать спокойствие поезд скоро отправится'
        self.assertEqual(transcription, correct_transcription)

    def test_empty_audio(self):
        self.speechtotext.local_file_path = '.\data_files\Test_Empty.wav'
        transcription = self.speechtotext.sample_recognize()
        self.assertNotEqual('', transcription)

class TestFilmRequest(unittest.TestCase):
    def setUp(self) -> None:
        self.update = mock.MagicMock()
    def test_bad_request(self):
        with patch('requests.request') as mock_get:
            mock_get.return_value.ok = False
            data = UrlRequests.get_film(UrlRequests, self.update)
        self.assertEqual(data, [])

    def test_good_request(self):
        with patch('requests.request') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {'title': 'a','rating':'b','length':'c', 'cast':[{'actor': 'd'}]}
            data = UrlRequests.get_film(UrlRequests, self.update)
        self.assertEqual(data, ['a', 'b', 'c', 'd'])



class TestWeather(unittest.TestCase):
    def setUp(self):
       self.weather = UrlRequests.get_weather(TOKEN, CITY)

    def test_return_value(self):
        self.assertTrue(type(self.weather == str))

    def test_url_200(self):
        r = requests.get(f'http://api.weatherstack.com/current?access_key={TOKEN}&query={CITY}')
        self.assertEqual(r.status_code, 200)
    def test_return(self):
        self.assertNotEqual(self.weather, '')


if __name__ == '__main__':
    unittest.main()
