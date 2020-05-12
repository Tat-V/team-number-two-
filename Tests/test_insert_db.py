import unittest
from unittest import mock
import mongomock
from datetime import datetime
from mongomock import MongoClient
from Shushushu import log_action, LOG_ACTIONS
from Files import Files


@log_action
def uselles_function(update):
    return None

def new_log(self, update, funcname):
    client = MongoClient("mongodb://localhost")
    database = client.get_database("test-db")
    database.create_collection("unittest")
    database["unittest"].insert_one({
        'user': update.effective_user.first_name,
        'user id': update.message.chat.id,
        'function': funcname.name,
        'message': update.message.text,
        'time': datetime.now().strftime("%Y-%m-%d %H.%M")})
    result = database["unittest"].find_one()
    del result['_id']
    # print(result)

    return result

class MyTestCase(unittest.TestCase):
    @mock.patch('Files.Files.new_log', side_effect=new_log)
    def test_something(self, mock_new_log):
        # self.client = MongoClient("mongodb://localhost")
        self.update = mock.MagicMock()
        self.funcname = mock.MagicMock()
        self.update.message.text = 'something important'
        self.update.effective_user.first_name = 'meaningless name'
        self.update.message.chat.id = 'some long integer'
        self.funcname.name ='some function'
        # database = self.client.get_database("test-db")
        # database.create_collection("unittest")
        # uselles_function(self.update)
        Files.new_log(self, self.update, self.funcname)
        # print(mock_new_log(self, self.update, self.funcname))
        self.assertEqual(mock_new_log(self, self.update, self.funcname), {'user': 'meaningless name',
                                                                         'user id': 'some long integer',
                                                                         'function': 'some function',
                                                                         'message': 'something important',
                                                                    'time': datetime.now().strftime("%Y-%m-%d %H.%M")})


if __name__ == '__main__':
    unittest.main()
