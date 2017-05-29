# coding: utf-8

import unittest

from crossref import validators


class ValidatorsTest(unittest.TestCase):

    def test_directory_1(self):

        result = validators.directory('DOAJ')

        self.assertTrue(result)

    def test_directory_2(self):

        with self.assertRaises(ValueError):
            validators.directory('any invalid archive')

    def test_archive_1(self):

        result = validators.archive('CLOCKSS')

        self.assertTrue(result)

    def test_archive_2(self):

        with self.assertRaises(ValueError):
            validators.archive('any invalid archive')

    def test_document_type_1(self):

        result = validators.document_type('book-chapter')

        self.assertTrue(result)

    def test_document_type_2(self):

        with self.assertRaises(ValueError):
            validators.document_type('any invalid type')

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

        with self.assertRaises(ValueError):
            validators.is_bool('jljlj')

    def test_is_date_1(self):

        result = validators.is_date('2017')

        self.assertTrue(result)

    def test_is_date_2(self):

        result = validators.is_date('2017-12')

        self.assertTrue(result)

    def test_is_date_3(self):

        result = validators.is_date('2017-12-31')

        self.assertTrue(result)

    def test_is_date_4(self):

        with self.assertRaises(ValueError):
            validators.is_date('asas')

    def test_is_date_5(self):

        with self.assertRaises(ValueError):
            validators.is_date('2017-30')

    def test_is_date_6(self):

        with self.assertRaises(ValueError):
            validators.is_date('2017-12-00')

    def test_is_integer_1(self):

        result = validators.is_integer('10')

        self.assertTrue(result)

    def test_is_integer_1(self):

        with self.assertRaises(ValueError):
            validators.is_integer('-1')

    def test_is_integer_3(self):

        with self.assertRaises(ValueError):
            validators.is_integer('dd')
