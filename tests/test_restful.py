import unittest

from crossref import restful


class RestfulTest(unittest.TestCase):
    """
    These tests are testing the API live integration, the main purpouse of these
    testes is to validate the JSON structure of the API results.
    These tests may lead to connectivity erros if the Crossref API is temporary
    out of service.
    """

    def test_work_agency_message(self):
        """
        Testing the base structure for the /works/{DOI}/agency endpoint.
        If all the base structure is present, this test may not lead to dict
        keyerror exceptions.
        """
        works = restful.Works()

        result = works.agency('10.1590/S0102-09352010000200002')

        self.assertEqual(result['agency']['id'], 'crossref')

    def test_work_agency_header(self):
        """
        Testing the base structure for the /works/{DOI}/agency endpoint.
        If all the base structure is present, this test may not lead to dict
        keyerror exceptions.
        """
        works = restful.Works()

        result = works.agency('10.1590/S0102-09352010000200002', only_message=False)

        self.assertEqual(result['message-type'], 'work-agency')


