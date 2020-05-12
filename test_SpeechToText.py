import unittest
import os
from Shushushu import SpeechToText

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'path_to_your_.json_credential_file'

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


if __name__ == '__main__':
    unittest.main()
