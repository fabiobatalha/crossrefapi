import pytest
from crossref import VERSION, restful


@pytest.fixture(autouse=True)
def etiquette():
    return restful.Etiquette(
        application_name="UnitTest CrossrefAPI",
        application_version=VERSION,
        application_url="https://github.com/fabiobatalha/crossrefapi",
        contact_email="undefined",
    )


def test_work_agency_message(etiquette):
    """
    Testing the base structure for the /works/{DOI}/agency endpoint.
    If all the base structure is present, this test may not lead to dict
    keyerror exceptions.
    """
    works = restful.Works(etiquette=etiquette, verify=False)
    result = works.agency("10.1590/S0102-09352010000200002")
    assert result["agency"]["id"] == "crossref"


def test_work_agency_header(etiquette):
    """
    Testing the base structure for the /works/{DOI}/agency endpoint.
    If all the base structure is present, this test may not lead to dict
    keyerror exceptions.
    """
    works = restful.Works(etiquette=etiquette, verify=False)
    result = works.agency("10.1590/S0102-09352010000200002", only_message=False)
    assert result["message-type"] == "work-agency"


def test_work_select_fields(etiquette):
    result = restful.Works(etiquette=etiquette, verify=False).select("DOI").url
    assert result == "https://api.crossref.org/works?select=DOI"


def test_work_select_fields_multiple_parameter_and_array(etiquette):
    result = restful.Works(etiquette=etiquette, verify=False) \
        .select("DOI", "title").select("subject").select(["relation", "editor"]) \
        .select("relation, editor").url
    assert result == "https://api.crossref.org/works?select=DOI%2Ceditor%2Crelation%2Csubject%2Ctitle"


def test_work_with_sample(etiquette):
    result = restful.Works(etiquette=etiquette, verify=False).sample(5).url
    assert result == "https://api.crossref.org/works?sample=5"


def test_work_with_sample_and_filters(etiquette):
    result = restful.Works(
        etiquette=etiquette, verify=False
    ).filter(type="journal-article").sample(5).url
    assert result == "https://api.crossref.org/works?filter=type%3Ajournal-article&sample=5"


def test_members_filters(etiquette):
    result = restful.Members(
        etiquette=etiquette, verify=False
    ).filter(has_public_references="true").url
    assert result == "https://api.crossref.org/members?filter=has-public-references%3Atrue"


def test_funders_filters(etiquette):
    result = restful.Funders(
        etiquette=etiquette, verify=False
    ).filter(location="Japan").url
    assert result == "https://api.crossref.org/funders?filter=location%3AJapan"


@pytest.fixture(autouse=True)
def httprequest():
    return restful.HTTPRequest()


def test_default_rate_limits(httprequest):
    expected = {"x-rate-limit-interval": 1, "x-rate-limit-limit": 50}
    assert httprequest.rate_limits == expected


def test_update_rate_limits_seconds(httprequest):
    headers = {"x-rate-limit-interval": "2s", "x-rate-limit-limit": 50}
    httprequest._update_rate_limits(headers)
    expected = {"x-rate-limit-interval": 2, "x-rate-limit-limit": 50}
    assert httprequest.rate_limits == expected


def test_update_rate_limits_minutes(httprequest):
    headers = {"x-rate-limit-interval": "2m", "x-rate-limit-limit": 50}
    httprequest._update_rate_limits(headers)
    expected = {"x-rate-limit-interval": 120, "x-rate-limit-limit": 50}
    assert httprequest.rate_limits == expected


def test_update_rate_limits_hours(httprequest):
    headers = {"x-rate-limit-interval": "2h", "x-rate-limit-limit": 50}
    httprequest._update_rate_limits(headers)
    expected = {"x-rate-limit-interval": 7200, "x-rate-limit-limit": 50}
    assert httprequest.rate_limits == expected
