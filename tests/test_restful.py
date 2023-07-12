
import unittest

from crossref import VERSION, restful


class RestfulTest(unittest.TestCase):
    """
    These tests are testing the API live integration, the main purpouse of these
    testes is to validate the JSON structure of the API results.
    These tests may lead to connectivity erros if the Crossref API is temporary
    out of service.
    """

    def setUp(self):

        self.etiquette = restful.Etiquette(
            application_name="UnitTest CrossrefAPI",
            application_version=VERSION,
            application_url="https://github.com/fabiobatalha/crossrefapi",
            contact_email="undefined",
        )

    def test_work_agency_message(self):
        """
        Testing the base structure for the /works/{DOI}/agency endpoint.
        If all the base structure is present, this test may not lead to dict
        keyerror exceptions.
        """
        works = restful.Works(etiquette=self.etiquette)

        result = works.agency("10.1590/S0102-09352010000200002")

        assert result["agency"]["id"] == "crossref"

    def test_work_agency_header(self):
        """
        Testing the base structure for the /works/{DOI}/agency endpoint.
        If all the base structure is present, this test may not lead to dict
        keyerror exceptions.
        """
        works = restful.Works(etiquette=self.etiquette)

        result = works.agency("10.1590/S0102-09352010000200002", only_message=False)

        assert result["message-type"] == "work-agency"

    def test_work_select_fields(self):
        result = restful.Works(etiquette=self.etiquette).select("DOI").url

        assert result == "https://api.crossref.org/works?select=DOI"

    def test_work_select_fields_multiple_parameter_and_array(self):
        result = restful.Works(etiquette=self.etiquette) \
            .select("DOI", "title").select("subject").select(["relation", "editor"]) \
            .select("relation, editor").url

        assert result == "https://api.crossref.org/works?select=DOI%2Ceditor%2Crelation%2Csubject%2Ctitle"

    def test_work_with_sample(self):
        result = restful.Works(etiquette=self.etiquette).sample(5).url

        assert result == "https://api.crossref.org/works?sample=5"

    def test_work_with_sample_and_filters(self):
        result = restful.Works(
            etiquette=self.etiquette).filter(type="journal-article").sample(5).url

        assert result == "https://api.crossref.org/works?filter=type%3Ajournal-article&sample=5"

    def test_members_filters(self):
        result = restful.Members(
            etiquette=self.etiquette).filter(has_public_references="true").url

        assert result == "https://api.crossref.org/members?filter=has-public-references%3Atrue"

    def test_funders_filters(self):
        result = restful.Funders(etiquette=self.etiquette).filter(location="Japan").url

        assert result == "https://api.crossref.org/funders?filter=location%3AJapan"


class HTTPRequestTest(unittest.TestCase):

    def setUp(self):

        self.httprequest = restful.HTTPRequest()

    def test_default_rate_limits(self):

        expected = {"x-rate-limit-interval": 1, "x-rate-limit-limit": 50}

        assert self.httprequest.rate_limits == expected

    def test_update_rate_limits_seconds(self):

        headers = {"x-rate-limit-interval": "2s", "x-rate-limit-limit": 50}

        self.httprequest._update_rate_limits(headers)

        expected = {"x-rate-limit-interval": 2, "x-rate-limit-limit": 50}

        assert self.httprequest.rate_limits == expected

    def test_update_rate_limits_minutes(self):

        headers = {"x-rate-limit-interval": "2m", "x-rate-limit-limit": 50}

        self.httprequest._update_rate_limits(headers)

        expected = {"x-rate-limit-interval": 120, "x-rate-limit-limit": 50}

        assert self.httprequest.rate_limits == expected

    def test_update_rate_limits_hours(self):

        headers = {"x-rate-limit-interval": "2h", "x-rate-limit-limit": 50}

        self.httprequest._update_rate_limits(headers)

        expected = {"x-rate-limit-interval": 7200, "x-rate-limit-limit": 50}

        assert self.httprequest.rate_limits == expected
