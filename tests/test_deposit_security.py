from http import HTTPStatus
from urllib.parse import parse_qs, urlsplit

import pytest
import requests

from crossref.restful import Depositor


@pytest.mark.parametrize(
    ("method", "identifier_key"),
    [
        ("request_doi_status_by_filename", "file_name"),
        ("request_doi_status_by_batch_id", "doi_batch_id"),
    ],
)
@pytest.mark.parametrize("data_type", ["result", "contents"])
@pytest.mark.parametrize("use_test_server", [False, True])
def test_deposit_status_credentials_stay_in_body(
    monkeypatch, method, identifier_key, data_type, use_test_server
):
    sent = []
    identifier = "example submission"

    def send(_session, request, **_kwargs):
        sent.append(request)
        response = requests.Response()
        response.status_code = HTTPStatus.OK
        response.request = request
        response.url = request.url
        response._content = b"submission result"
        return response

    monkeypatch.setattr(requests.Session, "send", send)
    depositor = Depositor(
        "10.example",
        "dummy-user/role",
        "dummy-password&+=",
        use_test_server=use_test_server,
    )

    response = getattr(depositor, method)(identifier, data_type=data_type)

    assert response.content == b"submission result"
    assert sent == [response.request]
    request = response.request
    subdomain = "test" if use_test_server else "doi"
    assert request.url == f"https://{subdomain}.crossref.org/servlet/submissionDownload"
    assert request.method == "POST"
    assert urlsplit(request.url).query == ""
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert parse_qs(request.body) == {
        "usr": ["dummy-user/role"],
        "pwd": ["dummy-password&+="],
        identifier_key: [identifier],
        "type": [data_type],
    }
