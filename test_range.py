import unittest
from data_Range import DataRange


class TestRange(unittest.TestCase):
    def setUp(self):
        self.data = DataRange()

    def tearDown(self):
        self.data.my_range = None

    def test_range_equal_int(self):
        self.data.generate(2)
        self.assertEqual(self.data.my_range, range(0, 2))

    def test_range_true(self):
        self.data.generate(4)
        self.assertTrue(list(self.data.my_range) == [0, 1, 2, 3])

    def test_range_is(self):
        self.data.generate(2)
        self.assertIsNot(self.data.generate(2), range(0, 2))

    def test_range_not_instance(self):
        self.data.generate(2)
        self.assertNotIsInstance(self.data.my_range, list)

    def test_range_in(self):
        self.data.generate(2)
        self.assertIn(1, self.data.my_range)

    def test_range_not_in(self):
        self.data.generate(2)
        self.assertNotIn(2, self.data.my_range)

    def test_range_none(self):
        with self.assertRaises(TypeError):
            self.data.generate(None)
            self.assertIsNone(self.data.my_range)

    def test_range_not_none(self):
        self.data.generate(2)
        self.assertIsNotNone(self.data.my_range)

    def test_range_err_float(self):
        with self.assertRaises(TypeError):
            self.data.generate(2.5)

    def test_range_err_missing(self):
        with self.assertRaises(TypeError):
            self.data.generate()

    if __name__ == '__main__':
        unittest.main()
