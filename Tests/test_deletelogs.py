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
# def kol_vo_strok():
#     kol_vo = 0
#     with open(files.HistoryFile, "r", encoding="UTF-8") as file_h:
#         hist_all = file_h.readlines()
#     for hist_line in hist_all:
#         hist_line = hist_line.split('\t')
#         hist_time = hist_line[-2].replace('time:', '')
#         hist_time = datetime.strptime(hist_time, "%Y-%m-%d %H.%M")
#         now = datetime.now()
#         period = now - hist_time
#         if period.days < 7:
#             break
#         kol_vo += 1
#     return(kol_vo)
#
#
# class TestDeleteLogs(unittest.TestCase):
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
#
#     @mock.patch('Shushushu.files.HistoryFile',
#                 new=r'C:\Users\Nani\PycharmProjects\team-number-two-\tests\data_files\Test_history.txt')
#     def test_exist_file(self):
#         self.assertTrue(os.path.exists(self.file.HistoryFile))
#
#     @mock.patch('Shushushu.files.HistoryFile',
#                 new=r'C:\Users\Nani\PycharmProjects\team-number-two-\tests\data_files\Test_history.txt')
#     def test_count_lines(self):
#         write_test_file()
#         self.file.DeleteLogs()
#         self.assertEqual(kol_vo_strok(), 0)
#         # path = os.path.join(os.path.abspath(os.path.dirname(__file__)), self.file.HistoryFile)
#         # os.remove(path)
#
#
#
# if __name__ == '__main__':
#     unittest.main()
