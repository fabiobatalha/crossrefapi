import unittest

from crossref import validators


class ValidatorsTest(unittest.TestCase):

    def test_is_bool_1(self):

        result = validators.is_bool(False)

        self.assertTrue(result)

    def test_is_bool_2(self):

        result = validators.is_bool(True)

        self.assertTrue(result)

    def test_is_bool_3(self):

        result = validators.is_bool('true')

        self.assertTrue(result)

    def test_is_bool_4(self):

        result = validators.is_bool('false')

        self.assertTrue(result)

    def test_is_bool_5(self):

        result = validators.is_bool('1')

        self.assertTrue(result)

    def test_is_bool_5(self):

        result = validators.is_bool('jljlj')

        self.assertFalse(result)
