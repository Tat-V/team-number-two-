# import unittest
# import os
# from datetime import datetime, timedelta
# from Shushushu import files
# from unittest import mock
#
#
# def write_test_file():
#     test_file = r'C:\Users\Nani\PycharmProjects\team-number-two-\tests\data_files\Test_history.txt'
#     with open(test_file, 'w') as file_h:
#         for i in range(5):
#             time = (datetime.now()-timedelta(days=7)).strftime("%Y-%m-%d %H.%M")
#             stroka = f'user:meaningless name	user id:some long integer	function:useless_function	message:something important	time:{time}'
#             file_h.write(stroka + '\t' + '\n')
#
#
# class TestHistory(unittest.TestCase):
#     def setUp(self):
#         self.file = files()
#         write_test_file()
#
#     @mock.patch('Shushushu.files.HistoryFile',
#                 new=r'C:\Users\Nani\PycharmProjects\team-number-two-\tests\data_files\Test_history.txt')
#     def tearDown(self):
#         path = os.path.join(os.path.abspath(os.path.dirname(__file__)), self.file.HistoryFile)
#         os.remove(path)
#         self.file = None
#
#     @mock.patch('Shushushu.files.HistoryFile',
#                 new=r'C:\Users\Nani\PycharmProjects\team-number-two-\tests\data_files\Test_history.txt')
#     def test_exist_file(self):
#         self.assertTrue(os.path.exists(self.file.HistoryFile))
#
#     @mock.patch('Shushushu.files.HistoryFile',
#                 new=r'C:\Users\Nani\PycharmProjects\team-number-two-\tests\data_files\Test_history.txt')
#     def test_count_lines(self):
#         self.assertEqual(self.file.history().count('\n'), 5)
#
#     @mock.patch('Shushushu.files.HistoryFile',
#                 new=r'C:\Users\Nani\PycharmProjects\team-number-two-\tests\data_files\Test_history.txt')
#     def test_return_values(self):
#         self.assertEqual(type(self.file.history()), str)
#
#
# if __name__ == '__main__':
#     unittest.main()
