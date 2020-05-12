import unittest
from SpeechToText import *

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../path-to-json-file.json"


class TestSpeechToText(unittest.TestCase):
    def setUp(self):
        self.speechtotext = SpeechToText("./data_files/Test_Sound.wav")

    def tearDown(self):
        self.speechtotext.local_file_path = None

    def test_path_exists(self):
        self.assertTrue(os.path.exists(self.speechtotext.local_file_path))

    def test_translate_audio(self):
        transcription = self.speechtotext.sample_recognize()
        correct_transcription = 'Уважаемые пассажиры просьба соблюдать спокойствие поезд скоро отправится'
        self.assertEqual(transcription, correct_transcription)

    def test_empty_audio(self):
        self.speechtotext.local_file_path = './data_files/Test_Empty.wav'
        transcription = self.speechtotext.sample_recognize()
        self.assertNotEqual('', transcription)


if __name__ == '__main__':
    unittest.main()
