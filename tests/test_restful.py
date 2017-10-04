# coding: utf-8

import unittest

from crossref import restful
from crossref import VERSION


class RestfulTest(unittest.TestCase):
    """
    These tests are testing the API live integration, the main purpouse of these
    testes is to validate the JSON structure of the API results.
    These tests may lead to connectivity erros if the Crossref API is temporary
    out of service.
    """

    def setUp(self):

        self.etiquette = restful.Etiquette(
            application_name='UnitTest CrossrefAPI',
            application_version=VERSION,
            application_url='https://github.com/fabiobatalha/crossrefapi',
            contact_email='undefined'
        )

    def test_work_agency_message(self):
        """
        Testing the base structure for the /works/{DOI}/agency endpoint.
        If all the base structure is present, this test may not lead to dict
        keyerror exceptions.
        """
        works = restful.Works(etiquette=self.etiquette)

        result = works.agency('10.1590/S0102-09352010000200002')

        self.assertEqual(result['agency']['id'], 'crossref')

    def test_work_agency_header(self):
        """
        Testing the base structure for the /works/{DOI}/agency endpoint.
        If all the base structure is present, this test may not lead to dict
        keyerror exceptions.
        """
        works = restful.Works(etiquette=self.etiquette)

        result = works.agency('10.1590/S0102-09352010000200002', only_message=False)

        self.assertEqual(result['message-type'], 'work-agency')

    def test_work_select_fields(self):
        result = restful.Works(etiquette=self.etiquette).select('DOI').url

        self.assertEqual(result, 'https://api.crossref.org/works?select=DOI')

    def test_work_select_fields_multiple_parameter_and_array(self):
        result = restful.Works(etiquette=self.etiquette).select('DOI', 'title').select('subject').select(['relation', 'editor']).select('relation, editor').url

        self.assertEqual(result, 'https://api.crossref.org/works?select=DOI%2Ceditor%2Crelation%2Csubject%2Ctitle')

    def test_work_with_sample(self):
        result = restful.Works(etiquette=self.etiquette).sample(5).url

        self.assertEqual(result, 'https://api.crossref.org/works?sample=5')

    def test_work_with_sample_and_filters(self):
        result = restful.Works(etiquette=self.etiquette).filter(type='journal-article').sample(5).url

        self.assertEqual(result, 'https://api.crossref.org/works?filter=type%3Ajournal-article&sample=5')

    def test_members_filters(self):
        result = restful.Members(etiquette=self.etiquette).filter(has_public_references="true").url

        self.assertEqual(result, 'https://api.crossref.org/members?filter=has-public-references%3Atrue')

    def test_funders_filters(self):
        result = restful.Funders(etiquette=self.etiquette).filter(location="Japan").url

        self.assertEqual(result, 'https://api.crossref.org/funders?filter=location%3AJapan')