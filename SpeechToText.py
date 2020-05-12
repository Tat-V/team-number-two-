import os
import io
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./path-to-json-file.json"


class SpeechToText:
    def __init__(self, local_file_path):
        self.local_file_path = local_file_path

    def sample_recognize(self):
        transcript = ''
        client = speech_v1.SpeechClient()
        language_code = "ru-RU"
        sample_rate_hertz = 48000
        encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
        config = {
            "language_code": language_code,
            "sample_rate_hertz": sample_rate_hertz,
            "encoding": encoding,
        }
        with io.open(self.local_file_path, "rb") as f:
            content = f.read()
        audio = {"content": content}
        response = client.recognize(config, audio)
        for result in response.results:
            alternative = result.alternatives[0]
            transcript = alternative.transcript
        if transcript == '':
            transcript = 'Не удалось перевести.'
        return transcript
