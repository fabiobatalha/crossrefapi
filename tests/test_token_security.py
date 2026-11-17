from http import HTTPStatus

import pytest
import requests
from requests.adapters import BaseAdapter

from crossref import restful


@pytest.fixture
def transport(monkeypatch):
    class RecordingAdapter(BaseAdapter):
        def __init__(self):
            self.sent = []
            self.redirect = None

        def send(self, request, **_kwargs):
            self.sent.append(request)
            response = requests.Response()
            response.request = request
            response.url = request.url
            response._content = b"{}"
            response.status_code = 200
            if len(self.sent) == 1 and self.redirect:
                response.status_code = 302
                response.headers["Location"] = self.redirect
            return response

        def close(self):
            pass

    adapter = RecordingAdapter()
    with requests.Session() as session:
        session.trust_env = False
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        monkeypatch.setattr(restful.requests, "get", session.get)
        monkeypatch.setattr(restful.requests, "post", session.post)
        yield adapter


@pytest.mark.parametrize("method", ["get", "post"])
@pytest.mark.parametrize("origin", ["https://api.crossref.org", "https://api.crossref.org:443"])
def test_token_reaches_trusted_origin(transport, method, origin):
    response = restful.HTTPRequest(throttle=False).do_http_request(
        method,
        f"{origin}/works",
        custom_header={"Crossref-Plus-API-Token": "dummy-token"},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(transport.sent) == 1
    assert transport.sent[0].headers["Crossref-Plus-API-Token"] == "dummy-token"


@pytest.mark.parametrize("method", ["get", "post"])
@pytest.mark.parametrize(
    "endpoint",
    [
        "https://attacker.example/works",
        "http://api.crossref.org/works",
        "https://api.crossref.org:444/works",
        "https://api.crossref.org.attacker.example/works",
        "https://api.crossref.org@attacker.example/works",
        "https://user:password@api.crossref.org/works",
    ],
)
def test_token_rejected_before_network_request(transport, method, endpoint):
    with pytest.raises(restful.CrossrefAPIError, match="trusted Crossref HTTPS endpoint"):
        restful.HTTPRequest(throttle=False).do_http_request(
            method,
            endpoint,
            custom_header={"crossref-plus-api-token": "dummy-token"},
        )
    assert transport.sent == []


@pytest.mark.parametrize("method", ["get", "post"])
@pytest.mark.parametrize(
    "destination",
    [
        "https://attacker.example/capture",
        "http://api.crossref.org/capture",
        "https://api.crossref.org/other",
    ],
)
def test_authenticated_redirect_never_sends_second_request(transport, method, destination):
    transport.redirect = destination
    with pytest.raises(restful.CrossrefAPIError, match="Redirect refused"):
        restful.HTTPRequest(throttle=False).do_http_request(
            method,
            "https://api.crossref.org/works",
            custom_header={"Crossref-Plus-API-Token": "dummy-token"},
        )
    assert len(transport.sent) == 1


def test_unauthenticated_redirect_still_works(transport):
    transport.redirect = "https://other.example/works"
    response = restful.HTTPRequest(throttle=False).do_http_request(
        "get", "https://api.crossref.org/works"
    )
    assert response.status_code == HTTPStatus.OK
    assert [request.url for request in transport.sent] == [
        "https://api.crossref.org/works",
        "https://other.example/works",
    ]
