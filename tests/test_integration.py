"""
These tests perform live requests to the Crossref API aiming to test real use cases.
"""

from crossref.restful import Funders, Journals, Members, Works


def test_works_get_work():
    """
    Test the retrieval of a specific DOI.
    """
    doi = "10.1590/S0102-09352010000200002"
    works = Works(verify=False)
    sample = works.doi(doi)
    assert sample.get("DOI").upper() == doi


def test_works_sample():
    """
    Test the sample endpoint using a limit of 5 records.
    """
    sample_size = 5
    works = Works(verify=False)
    sample = works.sample(sample_size)
    itens = list(sample)
    assert len(itens) == sample_size


def test_funders_endpoint():
    funders = Funders(verify=False)
    assert (
        funders.query("ABBEY AWARDS").url == "https://api.crossref.org/funders?query=ABBEY+AWARDS"
    )
    result = list(funders.query("ABBEY AWARDS"))
    assert len(result) == 1
    assert result[0].get("id") == "501100000314"
    assert result[0].get("name") == "ABBEY AWARDS"


def test_funders_endpoint_funder():
    funders = Funders(verify=False)
    funder = funders.funder(funder_id="501100000314")
    assert funder.get("id") == "501100000314"


def test_funders_endpoint_works():
    funders = Funders(verify=False)
    record = next(
        iter(funders.works(funder_id="501100000314").filter(doi="10.3897/folmed.62.e51230"))
    )
    assert record.get("funder")[0]["name"] == "ABBEY AWARDS"


def test_member_endpoint_query():
    members = Members(verify=False)
    assert (
        members.query("Érudit Consortium").url
        == "https://api.crossref.org/members?query=%C3%89rudit+Consortium"
    )
    result = list(members.query("Consortium Erudit"))
    assert len(result) == 1
    assert result[0].get("prefix")[0]["value"] == "10.7202"


def test_member_endpoint_filter():
    members = Members(verify=False)
    result = list(members.filter(prefix="10.7202"))
    assert len(result) == 1
    assert result[0].get("primary-name") == "Consortium Erudit"


def test_member_endpoint_member():
    members = Members(verify=False)
    member = members.member(member_id="4194")
    assert member.get("prefix")[0]["value"] == "10.7202"


def test_member_endpoint_works():
    members = Members(verify=False)
    record = next(iter(members.works(member_id="4194").filter(doi="10.7202/050998ar")))
    assert record.get("DOI") == "10.7202/050998ar"


def test_journal_endpoint_query():
    journals = Journals(verify=False)
    assert (
        journals.query("Cuizine The Journal of Canadian Food Cultures").url
        == "https://api.crossref.org/journals?query=Cuizine+The+Journal+of+Canadian+Food+Cultures"
    )
    result = list(journals.query("Cuizine The Journal of Canadian Food Cultures"))
    assert len(result) == 1
    assert result[0].get("title") == "Cuizine The Journal of Canadian Food Cultures"


def test_journals_endpoint_journal():
    journals = Journals(verify=False)
    journal = journals.journal(issn="1918-5480")
    assert journal.get("ISSN")[0] == "1918-5480"


def test_journals_endpoint_works():
    journals = Journals(verify=False)
    record = next(iter(journals.works(issn="1918-5480").filter(doi="10.7202/1038479ar")))
    assert record.get("DOI") == "10.7202/1038479ar"
