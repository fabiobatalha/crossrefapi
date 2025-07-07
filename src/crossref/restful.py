import contextlib
import typing
from collections.abc import Iterable
from time import sleep
from typing import Any

import requests

from crossref import VERSION, validators

LIMIT: int = 100
MAX_OFFSET: int = 10000
MAX_SAMPLE_SIZE: int = 100
FACETS_MAX_LIMIT: int = 1000
NOT_FOUND_404: int = 404

API = "api.crossref.org"


class CrossrefAPIError(Exception):
    pass


class MaxOffsetError(CrossrefAPIError):
    pass


class UrlSyntaxError(CrossrefAPIError, ValueError):
    pass


class HTTPRequest:
    def __init__(self, throttle: bool = True, verify: bool = True):
        self.throttle = throttle
        self.rate_limits = {"x-rate-limit-limit": 50, "x-rate-limit-interval": 1}
        self.verify = verify  # Disable SSL verification by default

    def _update_rate_limits(self, headers):
        with contextlib.suppress(ValueError):
            self.rate_limits["x-rate-limit-limit"] = int(headers.get("x-rate-limit-limit", 50))

        with contextlib.suppress(ValueError):
            interval_value = int(headers.get("x-rate-limit-interval", "1s")[:-1])

        interval_scope = headers.get("x-rate-limit-interval", "1s")[-1]

        if interval_scope == "m":
            interval_value = interval_value * 60

        if interval_scope == "h":
            interval_value = interval_value * 60 * 60

        self.rate_limits["x-rate-limit-interval"] = interval_value

    @property
    def throttling_time(self):
        return self.rate_limits["x-rate-limit-interval"] / self.rate_limits["x-rate-limit-limit"]

    def do_http_request(  # noqa: PLR0913
        self,
        method: str,
        endpoint: str,
        data=None,
        files=None,
        timeout: int = 100,
        only_headers: bool = False,
        custom_header=None,
    ):
        if only_headers:
            return requests.head(endpoint, timeout=2)

        action = requests.post if method == "post" else requests.get

        headers = custom_header if custom_header else {"user-agent": str(Etiquette())}
        if method == "post":
            result = action(
                endpoint,
                data=data,
                files=files,
                timeout=timeout,
                headers=headers,
                verify=self.verify,
            )
        else:
            result = action(
                endpoint,
                params=data,
                timeout=timeout,
                headers=headers,
                verify=self.verify,
            )

        if self.throttle:
            self._update_rate_limits(result.headers)
            sleep(self.throttling_time)

        return result


def build_url_endpoint(endpoint: str, context: str | None = None) -> str:
    endpoint = "/".join([i for i in [context, endpoint] if i])

    return f"https://{API}/{endpoint}"


class Etiquette:
    def __init__(
        self,
        application_name="undefined",
        application_version="undefined",
        application_url="undefined",
        contact_email="anonymous",
    ):
        self.application_name = application_name
        self.application_version = application_version
        self.application_url = application_url
        self.contact_email = contact_email

    def __str__(self):
        return (
            f"{self.application_name}/{self.application_version} ({self.application_url};"
            f" mailto:{self.contact_email}) BasedOn: CrossrefAPI/{VERSION}"
        )


class Endpoint:
    CURSOR_AS_ITER_METHOD = False
    ENDPOINT = ""

    def __init__(  # noqa: PLR0913
        self,
        request_url=None,
        request_params=None,
        context=None,
        etiquette=None,
        throttle=True,
        crossref_plus_token=None,
        timeout=30,
        verify=True,
    ):
        self.throttle = throttle
        self.verify = verify
        self.http_request = HTTPRequest(throttle=throttle, verify=verify)
        self.do_http_request = self.http_request.do_http_request
        self.etiquette = etiquette or Etiquette()
        self.custom_header = {"user-agent": str(self.etiquette)}
        self.crossref_plus_token = crossref_plus_token
        if crossref_plus_token:
            self.custom_header["Crossref-Plus-API-Token"] = self.crossref_plus_token
        self.request_url = request_url or build_url_endpoint(self.ENDPOINT, context)
        self.request_params = request_params or {}
        self.context = context or ""
        self.timeout = timeout

    @property
    def _rate_limits(self):
        request_url = str(self.request_url)

        result = self.do_http_request(
            "get",
            request_url,
            only_headers=True,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        return {
            "x-rate-limit-limit": result.headers.get("x-rate-limit-limit", "undefined"),
            "x-rate-limit-interval": result.headers.get("x-rate-limit-interval", "undefined"),
        }

    def _escaped_pagging(self):
        escape_pagging = ["offset", "rows"]
        request_params = dict(self.request_params)

        for item in escape_pagging:
            with contextlib.suppress(KeyError):
                del request_params[item]

        return request_params

    @property
    def version(self):
        """
        Retrieve the version of the Crossref API being used.

        This property provides the API version to ensure compatibility
        and keep track of the specific API features and changes.

        Returns:
            str: The version of the Crossref API.
        """
        request_params = dict(self.request_params)
        request_url = str(self.request_url)

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        ).json()

        return result["message-version"]

    @property
    def x_rate_limit_limit(self):
        return self._rate_limits.get("x-rate-limit-limit", "undefined")

    @property
    def x_rate_limit_interval(self):
        return self._rate_limits.get("x-rate-limit-interval", "undefined")

    def count(self):
        """
        Retrieve the total number of records resulting from a query.

        This method calculates the total number of records matching the
        current query settings, which may include filters, sorting,
        ordering, and facets.

        Returns:
            int: The total count of records that satisfy the query criteria.

        Note:
            This method is typically used in combination with `query`,
            `filter`, `sort`, `order`, and `facet` methods to refine the
            search parameters and get accurate record counts.
        """
        request_params = dict(self.request_params)
        request_url = str(self.request_url)
        request_params["rows"] = 0

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        ).json()

        return int(result["message"]["total-results"])

    @property
    def url(self):
        """
        Retrieve the URL that will be used for making HTTP requests to the Crossref API.

        This property dynamically constructs and returns the request URL based on
        the current state of query parameters. It is typically used in conjunction
        with methods such as `query`, `filter`, `sort`, `order`, and `facet` to build
        specialized queries for fetching data from the API.

        Returns:
            str: The fully formed URL to be used in the HTTP request.
        """
        request_params = self._escaped_pagging()

        sorted_request_params = sorted([(k, v) for k, v in request_params.items()])
        req = requests.Request("get", self.request_url, params=sorted_request_params).prepare()

        return req.url

    def all(self, request_params: dict | None) -> Iterable[dict]:
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)

        if request_params is None:
            request_params = {}

        return iter(
            self.__class__(
                request_url=request_url,
                request_params=request_params,
                context=context,
                etiquette=self.etiquette,
                throttle=self.throttle,
                crossref_plus_token=self.crossref_plus_token,
                timeout=self.timeout,
                verify=self.verify,
            ),
        )

    def __iter__(self):  # noqa: C901, PLR0912 - To many branches is not a problem.
        request_url = str(self.request_url)

        if "sample" in self.request_params:
            request_params = self._escaped_pagging()
            result = self.do_http_request(
                "get",
                self.request_url,
                data=request_params,
                custom_header=self.custom_header,
                timeout=self.timeout,
            )

            if result.status_code == NOT_FOUND_404:
                return

            result = result.json()

            for item in result["message"]["items"]:
                yield item

            return

        if self.CURSOR_AS_ITER_METHOD:
            request_params = dict(self.request_params)
            request_params["cursor"] = "*"
            request_params["rows"] = LIMIT
            while True:
                result = self.do_http_request(
                    "get",
                    request_url,
                    data=request_params,
                    custom_header=self.custom_header,
                    timeout=self.timeout,
                )

                if result.status_code == NOT_FOUND_404:
                    return

                result = result.json()

                if len(result["message"]["items"]) == 0:
                    return

                for item in result["message"]["items"]:
                    yield item

                request_params["cursor"] = result["message"]["next-cursor"]
        else:
            request_params = dict(self.request_params)
            request_params["offset"] = 0
            request_params["rows"] = LIMIT
            while True:
                result = self.do_http_request(
                    "get",
                    request_url,
                    data=request_params,
                    custom_header=self.custom_header,
                    timeout=self.timeout,
                )

                if result.status_code == NOT_FOUND_404:
                    return

                result = result.json()

                if len(result["message"]["items"]) == 0:
                    return

                for item in result["message"]["items"]:
                    yield item

                request_params["offset"] += LIMIT

                if request_params["offset"] >= MAX_OFFSET:
                    msg = "Offset exceeded the max offset of %d"
                    raise MaxOffsetError(msg, MAX_OFFSET)


class Works(Endpoint):
    CURSOR_AS_ITER_METHOD = True

    ENDPOINT = "works"

    ORDER_VALUES = ("asc", "desc", "1", "-1")

    SORT_VALUES = (
        "created",
        "deposited",
        "indexed",
        "is-referenced-by-count",
        "issued",
        "published",
        "published-online",
        "published-print",
        "references-count",
        "relevance",
        "score",
        "submitted",
        "updated",
    )

    FIELDS_QUERY = (
        "affiliation",
        "author",
        "bibliographic",
        "chair",
        "container_title",
        "contributor",
        "editor",
        "event_acronym",
        "event_location",
        "event_name",
        "event_sponsor",
        "event_theme",
        "funder_name",
        "publisher_location",
        "publisher_name",
        "translator",
    )

    FIELDS_SELECT = (
        "DOI",
        "ISBN",
        "ISSN",
        "URL",
        "abstract",
        "accepted",
        "alternative-id",
        "approved",
        "archive",
        "article-number",
        "assertion",
        "author",
        "chair",
        "clinical-trial-number",
        "container-title",
        "content-created",
        "content-domain",
        "created",
        "degree",
        "deposited",
        "editor",
        "event",
        "funder",
        "group-title",
        "indexed",
        "is-referenced-by-count",
        "issn-type",
        "issue",
        "issued",
        "license",
        "link",
        "member",
        "original-title",
        "page",
        "posted",
        "prefix",
        "published",
        "published-online",
        "published-print",
        "publisher",
        "publisher-location",
        "reference",
        "references-count",
        "relation",
        "score",
        "short-container-title",
        "short-title",
        "standards-body",
        "subject",
        "subtitle",
        "title",
        "translator",
        "type",
        "update-policy",
        "update-to",
        "updated-by",
        "volume",
    )

    FILTER_VALIDATOR: typing.ClassVar[dict] = {
        "alternative_id": None,
        "archive": validators.archive,
        "article_number": None,
        "assertion": None,
        "assertion-group": None,
        "award.funder": None,
        "award.number": None,
        "category-name": None,
        "clinical-trial-number": None,
        "container-title": None,
        "content-domain": None,
        "directory": validators.directory,
        "doi": None,
        "from-accepted-date": validators.is_date,
        "from-created-date": validators.is_date,
        "from-deposit-date": validators.is_date,
        "from-event-end-date": validators.is_date,
        "from-event-start-date": validators.is_date,
        "from-index-date": validators.is_date,
        "from-issued-date": validators.is_date,
        "from-online-pub-date": validators.is_date,
        "from-posted-date": validators.is_date,
        "from-print-pub-date": validators.is_date,
        "from-pub-date": validators.is_date,
        "from-update-date": validators.is_date,
        "full-text.application": None,
        "full-text.type": None,
        "full-text.version": None,
        "funder": None,
        "funder-doi-asserted-by": None,
        "group-title": None,
        "has-abstract": validators.is_bool,
        "has-affiliation": validators.is_bool,
        "has-archive": validators.is_bool,
        "has-assertion": validators.is_bool,
        "has-authenticated-orcid": validators.is_bool,
        "has-award": validators.is_bool,
        "has-clinical-trial-number": validators.is_bool,
        "has-content-domain": validators.is_bool,
        "has-domain-restriction": validators.is_bool,
        "has-event": validators.is_bool,
        "has-full-text": validators.is_bool,
        "has-funder": validators.is_bool,
        "has-funder-doi": validators.is_bool,
        "has-license": validators.is_bool,
        "has-orcid": validators.is_bool,
        "has-references": validators.is_bool,
        "has-relation": validators.is_bool,
        "has-update": validators.is_bool,
        "has-update-policy": validators.is_bool,
        "is-update": validators.is_bool,
        "isbn": None,
        "issn": None,
        "license.delay": validators.is_integer,
        "license.url": None,
        "license.version": None,
        "location": None,
        "member": validators.is_integer,
        "orcid": None,
        "prefix": None,
        "relation.object": None,
        "relation.object-type": None,
        "relation.type": None,
        "type": validators.document_type,
        "type-name": None,
        "until-accepted-date": validators.is_date,
        "until-created-date": validators.is_date,
        "until-deposit-date": validators.is_date,
        "until-event-end-date": validators.is_date,
        "until-event-start-date": validators.is_date,
        "until-index-date": validators.is_date,
        "until-issued-date": validators.is_date,
        "until-online-pub-date": validators.is_date,
        "until-posted-date": validators.is_date,
        "until-print-pub-date": validators.is_date,
        "until-pub-date": validators.is_date,
        "until-update-date": validators.is_date,
        "update-type": None,
        "updates": None,
    }

    FACET_VALUES: typing.ClassVar[dict] = {
        "archive": None,
        "affiliation": None,
        "assertion": None,
        "assertion-group": None,
        "category-name": None,
        "container-title": 1000,
        "license": None,
        "funder-doi": None,
        "funder-name": None,
        "issn": 1000,
        "orcid": 1000,
        "published": None,
        "publisher-name": None,
        "relation-type": None,
        "source": None,
        "type-name": None,
        "update-type": None,
    }

    def order(self, order: str = "asc"):
        """
        Sets the order of results for API requests and retrieves an
        iterable object containing works metadata.

        The resulting order can be ascending or descending based
        on the provided argument. This method is typically used
        in combination with `query`, `filter`, `sort`, and `facet`
        methods for a refined query.

        Args:
            order (str, optional): The sorting order for the results.
                Accepts either "asc" for ascending or "desc" for
                descending order. Defaults to "asc".

        Returns:
            Iterable: An object implementing the `__iter__` method,
            allowing iteration over the sorted work's metadata.

        Note:
            This method is part of a chainable API workflow, meaning
            it can be chained with other methods (`query`, `filter`,
            etc.) to construct and execute advanced queries.
        """

        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)

        if order not in self.ORDER_VALUES:
            msg = "Sort order specified as {} but must be one of: {}".format(
                str(order), ", ".join(self.ORDER_VALUES)
            )
            raise UrlSyntaxError(
                msg,
            )

        request_params["order"] = order

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )

    def select(self, *args):
        """
        Retrieves an iterable object containing metadata for works.

        This method constructs a request URL by combining the specified
        arguments into query parameters and can be used in conjunction
        with methods like `query`, `filter`, `sort`, and `facet` to refine
        the request and retrieval process.

        Args:
            *args: A variable number of arguments that represent valid
                   `FIELDS_SELECT` parameters to be included in the request.

        Returns:
            Iterable: An object that allows iteration over the metadata
                      of works returned by the Crossref API.

        Usage:
            This method is particularly useful when chained with additional
            methods like `filter` or `sort` to create and execute more complex
            queries for retrieving specific selected fields from works metadata.
        """
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)

        select_args = []

        for item in args:
            if isinstance(item, list):
                select_args += [i.strip() for i in item]

            if isinstance(item, str):
                select_args += [i.strip() for i in item.split(",")]

        invalid_select_args = set(select_args) - set(self.FIELDS_SELECT)

        if len(invalid_select_args) != 0:
            msg = "Select field's specified as ({}) but must be one of: {}".format(
                ", ".join(invalid_select_args), ", ".join(self.FIELDS_SELECT)
            )
            raise UrlSyntaxError(
                msg,
            )

        request_params["select"] = ",".join(
            sorted(
                [i for i in set(request_params.get("select", "").split(",") + select_args) if i]
            ),
        )

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )

    def sort(self, sort: str = "score"):
        """
        This method retrieves an iterable object that implements the method
        __iter__. The arguments given will compose the parameters in the
        request url.
        This method can be used compounded with query, filter, order, and facet methods.
        params:
            kwargs: valid SORT_VALUES arguments.

        return: iterable object of Works metadata
        """
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)

        if sort not in self.SORT_VALUES:
            msg = "Sort field specified as {} but must be one of: {}".format(
                str(sort), ", ".join(self.SORT_VALUES)
            )
            raise UrlSyntaxError(
                msg,
            )

        request_params["sort"] = sort

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )

    def filter(self, **kwargs):
        """
        Apply filters to refine the query and retrieve an iterable object of works metadata.

        This method allows for the application of one or more filters to the query, building
        a request URL with the specified parameters. It can be used in combination with other
        query-refining methods such as `query`, `sort`, `order`, and `facet` to create advanced
        queries to the Crossref API.

        Args:
            **kwargs: Arbitrary keyword arguments representing the filters to apply.
                      Valid filters are defined by `FILTER_VALIDATOR`. Replace special
                      characters in parameter names (`.` to `__` and `-` to `_`) when
                      constructing filters.

        Returns:
            Iterable: An iterable object that allows iteration over works metadata
                      returned from the Crossref API.

        Raises:
            UrlSyntaxError: If invalid filter arguments are provided.

        Usage:
            This method is chainable and can be used recursively with other query-related
            methods to build complex queries. For example, you can chain this method with
            `sort` or `facet` to control the output data structure.
        """
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)

        for fltr, value in kwargs.items():
            decoded_fltr = fltr.replace("__", ".").replace("_", "-")
            if decoded_fltr not in self.FILTER_VALIDATOR:
                msg = (
                    f"Filter {decoded_fltr!s} specified but there is no such filter for"
                    f" this route. Valid filters for this route"
                    f" are: {', '.join(self.FILTER_VALIDATOR.keys())}"
                )
                raise UrlSyntaxError(
                    msg,
                )

            if self.FILTER_VALIDATOR[decoded_fltr] is not None:
                self.FILTER_VALIDATOR[decoded_fltr](str(value))

            if "filter" not in request_params:
                request_params["filter"] = decoded_fltr + ":" + str(value)
            else:
                request_params["filter"] += "," + decoded_fltr + ":" + str(value)

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )

    def facet(self, facet_name: str, facet_count: int = 100):
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)
        request_params["rows"] = 0

        if facet_name not in self.FACET_VALUES:
            msg = (
                f"Facet {facet_name} specified but there is no such facet for this route."
                " Valid facets for this route are: *, affiliation, funder-name, funder-doi,"
                " publisher-name, orcid, container-title, assertion, archive, update-type,"
                " issn, published, source, type-name, license, category-name, relation-type,"
                " assertion-group"
            )
            raise UrlSyntaxError(
                msg,
                ", ".join(self.FACET_VALUES.keys()),
            )

        facet_count = (
            self.FACET_VALUES[facet_name]
            if self.FACET_VALUES[facet_name] is not None
            and self.FACET_VALUES[facet_name] <= facet_count
            else facet_count
        )

        request_params["facet"] = f"{facet_name}:{facet_count}"
        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        ).json()

        return result["message"]["facets"]

    def query(self, *args, **kwargs):
        """
        Construct and execute a query to retrieve an iterable object of works metadata.

        This method dynamically builds a request URL based on the arguments and
        keyword parameters provided. It retrieves an iterable object implementing
        the `__iter__` method, allowing users to iterate over the metadata.

        The `query` method can be used in combination with other methods, such as
        `filter`, `sort`, `order`, and `facet`, to create complex and refined queries.

        Args:
            *args (str): Positional arguments representing free-text query strings
                         to search for specific metadata.
            **kwargs: Key-value pairs corresponding to valid `FIELDS_QUERY` arguments
                      to refine the query.

        Returns:
            Iterable: An object that allows iteration over the work's metadata corresponding
                      to the query.

        Raises:
            UrlSyntaxError: If the provided arguments result in an invalid query URL.

        Usage:
            This method supports method chaining and can be called recursively to fine-tune
            the query construction process.
        """
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)

        if args:
            request_params["query"] = " ".join([str(i) for i in args])

        for field, value in kwargs.items():
            if field not in self.FIELDS_QUERY:
                msg = (
                    f"Field query {field!s} specified but there is no such field query for"
                    " this route."
                    f" Valid field queries for this route are: {', '.join(self.FIELDS_QUERY)}"
                )
                raise UrlSyntaxError(
                    msg,
                )
            query_field_name = field.replace("_", "-")
            key = f"query.{query_field_name}"
            request_params[key] = value

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )

    def sample(self, sample_size: int = 20):
        """
        Retrieve a sample of works metadata as an iterable object.

        This method allows the user to retrieve a random sample of metadata
        records from the work's endpoint. The size of the sample can be controlled
        by the `sample_size` parameter.

        Args:
            sample_size (int, optional): The number of metadata records to fetch in the sample.
                                         Must be an integer between 0 and 100. Defaults to 20.

        Returns:
            Iterable: An iterable object containing the sample of works metadata.

        Raises:
            ValueError: If `sample_size` is not within the valid range (0-100). The limit of 100
            records is based on the Crossref API limits.

        Usage:
            This method is typically used to retrieve a smaller set of records for testing or
            exploratory purposes. It can be combined with other methods such as `filter` or `query`
            for more refined sampling.

        """
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)
        try:
            if sample_size > MAX_SAMPLE_SIZE:
                msg = (
                    f"Integer specified as {sample_size!s} but"
                    " must be a positive integer less than or equal to 100."
                )
                raise UrlSyntaxError(msg)
        except TypeError as exc:
            msg = (
                f"Integer specified as {sample_size!s} but"
                " must be a positive integer less than or equal to 100."
            )
            raise UrlSyntaxError(msg) from exc

        request_params["sample"] = sample_size

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            context=context,
            etiquette=self.etiquette,
            timeout=self.timeout,
            throttle=self.throttle,
            verify=self.verify,
            crossref_plus_token=self.crossref_plus_token,
        )

    def doi(self, doi: str, only_message: bool = True) -> Any | None:
        """
        Retrieve metadata for a given DOI (Digital Object Identifier).

        This method fetches metadata associated with the provided DOI from the Crossref API.
        Depending on the `only_message` parameter, the method returns either the full API
        response or the "message" portion, which contains the DOI-related metadata.

        Args:
            doi (str): The DOI string to query, which uniquely identifies the resource.
            only_message (bool, optional): If set to `True` (default), it returns only the
                "message" portion of the API response. If set to `False`, the full
                JSON response is returned.

        Returns:
            dict: The metadata associated with the provided DOI. Returns the "message"
                  portion if `only_message=True`, otherwise the complete API response.

        Raises:
            ValueError: If the provided DOI is invalid or improperly formatted.
            RequestException: If there is an issue connecting to the Crossref API
                              or receiving a response.
        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, doi]))
        request_params = {}
        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        if result.status_code == NOT_FOUND_404:
            return None
        result = result.json()

        return result["message"] if only_message is True else result

    def agency(self, doi: str, only_message: bool = True) -> Any | None:
        """
        Retrieve the metadata of the DOI Registration Agency for a specified DOI.

        This method queries the Crossref API to provide details about the agency
        responsible for registering a given DOI (Digital Object Identifier). The response
        can be customized to return either the complete JSON response or just the
        "message" portion containing the agency metadata.

        Args:
            doi (str): The DOI string to query, which uniquely identifies the resource.
            only_message (bool, optional): If True (default), only the "message" portion
                                           of the JSON response is returned. If False,
                                           the complete JSON structure is delivered.

        Returns:
            dict: The metadata associated with the agency responsible for the DOI. Returns
                  the "message" portion if `only_message=True`, otherwise returns the full
                  JSON response.

        Raises:
            ValueError: If the provided DOI is invalid or improperly formatted.
            RequestException: If there is an issue connecting to the Crossref API or processing
                              the response.
        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, doi, "agency"]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        if result.status_code == NOT_FOUND_404:
            return None

        result = result.json()

        return result["message"] if only_message is True else result

    def doi_exists(self, doi: str) -> bool:
        """
        Check the existence of a DOI in the Crossref database.

        This method queries the Crossref API to determine whether a specified
        Digital Object Identifier (DOI) exists. It returns `False` if the API
        responds with a 404 status code, indicating that the DOI does not exist.

        Args:
            doi (str): The DOI string to check for existence.

        Returns:
            bool: `True` if the DOI exists in the Crossref database, otherwise `False`.

        Raises:
            ValueError: If the DOI format is invalid.
            RequestException: If there is an issue connecting to the Crossref API.
        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, doi]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            only_headers=True,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        return result.status_code != NOT_FOUND_404


class Funders(Endpoint):
    CURSOR_AS_ITER_METHOD = False

    ENDPOINT = "funders"

    FILTER_VALIDATOR: typing.ClassVar[dict] = {"location": None}

    def query(self, *args):
        """
        Retrieve an iterable of funder metadata matching the query.

        This method constructs a query to the Crossref Funders endpoint using the provided
        arguments.
        The arguments are combined into a free-text search string for the `query` parameter.

        Args:
            *args: One or more strings to be used as the search query for funders.

        Returns:
            Funders: An iterable object of funder metadata matching the query.
        """
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if args:
            request_params["query"] = " ".join([str(i) for i in args])

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )

    def filter(self, **kwargs):
        """
        Apply filters to refine the query and retrieve an iterable object of works metadata.

        This method allows for the application of one or more filters to the query, building
        a request URL with the specified parameters. It can be used in combination with other
        query-refining methods such as `query`, `sort`, `order`, and `facet` to create advanced
        queries to the Crossref API.

        Args:
            **kwargs: Arbitrary keyword arguments representing the filters to apply.
                      Valid filters are defined by `FILTER_VALIDATOR`. Replace special
                      characters in parameter names (`.` to `__` and `-` to `_`) when
                      constructing filters.

        Returns:
            Iterable: An iterable object that allows iteration over works metadata
                      returned from the Crossref API.

        Raises:
            UrlSyntaxError: If any filter argument is not valid.

        Usage:
        This method is chainable and can be used recursively with other query-related
        methods to build complex queries. For example, you can chain this method with
        `sort` or `facet` to control the output data structure.
        """
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)

        for fltr, value in kwargs.items():
            decoded_fltr = fltr.replace("__", ".").replace("_", "-")
            if decoded_fltr not in self.FILTER_VALIDATOR:
                msg = (
                    f"Filter {decoded_fltr!s} specified but there is no such filter for this route."
                    f" Valid filters for this route are: {', '.join(self.FILTER_VALIDATOR.keys())}"
                )
                raise UrlSyntaxError(
                    msg,
                )

            if self.FILTER_VALIDATOR[decoded_fltr] is not None:
                self.FILTER_VALIDATOR[decoded_fltr](str(value))

            if "filter" not in request_params:
                request_params["filter"] = decoded_fltr + ":" + str(value)
            else:
                request_params["filter"] += "," + decoded_fltr + ":" + str(value)

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )

    def funder(self, funder_id: str | int, only_message: bool = True) -> Any | None:
        """
        Retrieve metadata for a specific Crossref funder by funder ID.

        This method queries the Crossref Funders endpoint to fetch metadata
        associated with the provided funder ID. The response can be limited
        to the "message" portion or include the full JSON response.

        Args:
            funder_id (int or str): The unique identifier of the funder in Crossref.
            only_message (bool, optional): If True (default), return only the "message"
                portion of the API response. If False, return the full JSON response.

        Returns:
            dict or None: The funder metadata as a dictionary if found, or None if the
                funder does not exist.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.

        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, str(funder_id)]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        if result.status_code == NOT_FOUND_404:
            return None

        result = result.json()

        return result["message"] if only_message is True else result

    def funder_exists(self, funder_id: str | int) -> bool:
        """
        Check if a Crossref funder exists for the given funder ID.

        This method queries the Crossref Funders endpoint to determine whether a funder
        with the specified ID exists. It returns `False` if the API responds with a 404
        status code, indicating the funder does not exist.

        Args:
            funder_id (int or str): The unique identifier of the funder in Crossref.

        Returns:
            bool: `True` if the funder exists, `False` otherwise.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.
        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, str(funder_id)]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            only_headers=True,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        return result.status_code != NOT_FOUND_404

    def works(self, funder_id: str | int) -> Works:
        """
        Retrieve an Work object associated with a specific funder.

        This method returns a `Works` instance configured to fetch all works
        (publications, datasets, etc.) linked to the given Crossref funder ID.

        Args:
            funder_id (int or str): The unique identifier of the funder in Crossref.

        Returns:
            Works: An object for accessing works metadata related to the funder.

        """
        context = f"{self.ENDPOINT}/{funder_id!s}"
        return Works(
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )


class Members(Endpoint):
    CURSOR_AS_ITER_METHOD = False

    ENDPOINT = "members"

    FILTER_VALIDATOR: typing.ClassVar[dict] = {
        "prefix": None,
        "has-public-references": validators.is_bool,
        "backfile-doi-count": validators.is_integer,
        "current-doi-count": validators.is_integer,
    }

    def query(self, *args):
        """
        Retrieve an iterable of Crossref member metadata matching the query.

        This method constructs a query to the Crossref Members endpoint using the provided
        arguments. The arguments are combined into a free-text search string for the
        `query` parameter.

        Args:
            *args: One or more strings to be used as the search query for members.

        Returns:
            Members: An iterable object of member metadata matching the query.
        """
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if args:
            request_params["query"] = " ".join([str(i) for i in args])

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )

    def filter(self, **kwargs):
        """
        Apply filters to refine the query and retrieve an iterable of Crossref member metadata.

        This method allows you to specify one or more filters as keyword arguments, which are
        validated and incorporated into the request URL. It can be chained with other query
        methods such as `query`, `order`, `sort`, and `facet` to build complex queries for
        retrieving member metadata from the Crossref API.

        Args:
            **kwargs: Arbitrary keyword arguments representing filters to apply.
                Valid filter names are defined in `FILTER_VALIDATOR`. Use double underscores
                (`__`) for dots and single underscores (`_`) for dashes in filter names.

        Returns:
            Members: An iterable object of member metadata matching the applied filters.

        Raises:
            UrlSyntaxError: If any filter argument is not valid for this endpoint.
        """
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)

        for fltr, value in kwargs.items():
            decoded_fltr = fltr.replace("__", ".").replace("_", "-")
            if decoded_fltr not in self.FILTER_VALIDATOR:
                msg = (
                    f"Filter {decoded_fltr!s} specified but there is no such filter for this route."
                    f" Valid filters for this route are: {', '.join(self.FILTER_VALIDATOR.keys())}"
                )
                raise UrlSyntaxError(msg)

            if self.FILTER_VALIDATOR[decoded_fltr] is not None:
                self.FILTER_VALIDATOR[decoded_fltr](str(value))

            if "filter" not in request_params:
                request_params["filter"] = decoded_fltr + ":" + str(value)
            else:
                request_params["filter"] += "," + decoded_fltr + ":" + str(value)

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )

    def member(self, member_id: str | int, only_message: bool = True) -> Any | None:
        """
        Retrieve metadata for a specific Crossref member by member ID.

        This method queries the Crossref Members endpoint to fetch metadata
        associated with the provided member ID. The response can be limited
        to the "message" portion or include the full JSON response.

        Args:
            member_id (int or str): The unique identifier of the member in Crossref.
            only_message (bool, optional): If True (default), return only the "message"
                portion of the API response. If False, return the full JSON response.

        Returns:
            dict or None: The member metadata as a dictionary if found, or None if the
                member does not exist.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.

        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, str(member_id)]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        if result.status_code == NOT_FOUND_404:
            return None

        result = result.json()

        return result["message"] if only_message is True else result

    def member_exists(self, member_id):
        """
        Check if a Crossref member exists for the given member ID.

        This method queries the Crossref Members endpoint to determine whether a member
        with the specified ID exists. It returns `False` if the API responds with a 404
        status code, indicating the member does not exist.

        Args:
            member_id (int or str): The unique identifier of the member in Crossref.

        Returns:
            bool: `True` if the member exists, `False` otherwise.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.

        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, str(member_id)]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            only_headers=True,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        return result.status_code != NOT_FOUND_404

    def works(self, member_id: str | int) -> Works:
        """
        Retrieve a Work object associated with a specific Crossref member.

        This method returns a `Works` instance configured to fetch all works
        (such as publications, datasets, etc.) linked to the given Crossref member ID.

        Args:
            member_id (int or str): The unique identifier of the member in Crossref.

        Returns:
            Works: An object for accessing works metadata related to the specified member.

        """
        context = f"{self.ENDPOINT}/{member_id!s}"
        return Works(
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )


class Types(Endpoint):
    CURSOR_AS_ITER_METHOD = False

    ENDPOINT = "types"

    def type(self, type_id: str | int, only_message: bool = True) -> Any | None:
        """
        Retrieve metadata for a specific Crossref document type by type ID.

        This method queries the Crossref Types endpoint to fetch metadata
        associated with the provided document type ID. The response can be
        limited to the "message" portion or include the full JSON response.

        Args:
            type_id (str | int): The unique identifier of the Crossref document type.
            only_message (bool, optional): If True (default), return only the "message"
                portion of the API response. If False, return the full JSON response.

        Returns:
            dict or None: The type metadata as a dictionary if found, or None if the
                type does not exist.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.

        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, str(type_id)]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        if result.status_code == NOT_FOUND_404:
            return None

        result = result.json()

        return result["message"] if only_message is True else result

    def all(self, request_params: dict | None) -> Iterable[dict]:
        """
        Retrieve an iterator over all available Crossref document types.

        This method fetches all document types from the Crossref Types endpoint and yields
        each type as a dictionary. It is useful for listing or processing all supported
        document types in the Crossref database.

        Returns:
            Iterator[dict]: An iterator yielding dictionaries, each representing a document type.
        """
        request_url = build_url_endpoint(self.ENDPOINT, self.context)
        request_params = dict(self.request_params)
        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )
        if result.status_code == NOT_FOUND_404:
            return None
        result = result.json()
        yield from result["message"]["items"]
        return None

    def type_exists(self, type_id: str | int):
        """
        Check if a Crossref document type exists for the given type ID.

        This method queries the Crossref Types endpoint to determine whether a document
        type with the specified ID exists. It returns `False` if the API responds with a
        404 status code, indicating the type does not exist.

        Args:
            type_id (str | int): The unique identifier of the Crossref document type.

        Returns:
            bool: `True` if the document type exists, `False` otherwise.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.

        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, str(type_id)]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            only_headers=True,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        return result.status_code != NOT_FOUND_404

    def works(self, type_id: str | int) -> Works:
        """
        Retrieve an iterable of works for a specific Crossref document type.

        This method returns a `Works` instance configured to fetch all works
        (such as articles, books, etc.) associated with the given Crossref
        document type ID.

        Args:
            type_id (str or int): The unique identifier of the Crossref document type.

        Returns:
            Works: An object for accessing works metadata related to the specified type.

        """
        context = f"{self.ENDPOINT}/{type_id!s}"
        return Works(
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )


class Prefixes(Endpoint):
    CURSOR_AS_ITER_METHOD = False

    ENDPOINT = "prefixes"

    def prefix(self, prefix_id: str | int, only_message: bool = True) -> Any | None:
        """
        Retrieve metadata for a specific Crossref prefix by prefix ID.

        This method queries the Crossref Prefixes endpoint to fetch metadata
        associated with the provided prefix ID. The response can be limited
        to the "message" portion or include the full JSON response.

        Args:
            prefix_id (str or int): The unique identifier of the Crossref prefix.
            only_message (bool, optional): If True (default), return only the "message"
                portion of the API response. If False, return the full JSON response.

        Returns:
            dict or None: The prefix metadata as a dictionary if found, or None if the
                prefix does not exist.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.

        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, str(prefix_id)]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        if result.status_code == NOT_FOUND_404:
            return None

        result = result.json()

        return result["message"] if only_message is True else result

    def works(self, prefix_id: str | int) -> Works:
        """
        Retrieve an Work object associated with a specific Crossref prefix.

        This method returns a `Works` instance configured to fetch all works
        (such as articles, books, etc.) linked to the given Crossref prefix ID.

        Args:
            prefix_id (str or int): The unique identifier of the Crossref prefix.

        Returns:
            Works: An object for accessing works metadata related to the specified prefix.

        """
        context = f"{self.ENDPOINT}/{prefix_id!s}"
        return Works(
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )


class Journals(Endpoint):
    CURSOR_AS_ITER_METHOD = False

    ENDPOINT = "journals"

    def query(self, *args):
        """
        Retrieve an iterable of Crossref journal metadata matching the query.

        This method constructs a query to the Crossref Journals endpoint using the provided
        arguments. The arguments are combined into a free-text search string for the `query`
        parameter, allowing you to search for journals by title, ISSN, or other metadata.

        Args:
            *args: One or more strings to be used as the search query for journals.

        Returns:
            Journals: An iterable object of journal metadata matching the query.
        """
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if args:
            request_params["query"] = " ".join([str(i) for i in args])

        return self.__class__(
            request_url=request_url,
            request_params=request_params,
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )

    def journal(self, issn: str, only_message: bool = True) -> Any | None:
        """
        Retrieve metadata for a specific journal by ISSN from the Crossref API.

        This method queries the Crossref Journals endpoint to fetch metadata
        associated with the provided ISSN. The response can be limited to the
        "message" portion or include the full JSON response.

        Args:
            issn (str): The ISSN (International Standard Serial Number) of the journal.
            only_message (bool, optional): If True (default), return only the "message"
                portion of the API response. If False, return the full JSON response.

        Returns:
            dict or None: The journal metadata as a dictionary if found, or None if the
                journal does not exist.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.
        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, str(issn)]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        if result.status_code == NOT_FOUND_404:
            return None

        result = result.json()

        return result["message"] if only_message is True else result

    def journal_exists(self, issn: str) -> bool:
        """
        Check if a journal exists in the Crossref database by ISSN.

        This method queries the Crossref Journals endpoint to determine whether a journal
        with the specified ISSN exists. It returns `False` if the API responds with a 404
        status code, indicating the journal does not exist.

        Args:
            issn (str): The ISSN (International Standard Serial Number) of the journal.

        Returns:
            bool: `True` if the journal exists in the Crossref database, otherwise `False`.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.
        """
        request_url = build_url_endpoint("/".join([self.ENDPOINT, str(issn)]))
        request_params = {}

        result = self.do_http_request(
            "get",
            request_url,
            data=request_params,
            only_headers=True,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

        return result.status_code != NOT_FOUND_404

    def works(self, issn: str) -> Works:
        """
        Retrieve a Works object associated with a specific journal by ISSN.

        This method returns a `Works` instance configured to fetch all works
        (such as articles, papers, etc.) linked to the given journal ISSN
        from the Crossref API.

        Args:
            issn (str): The ISSN (International Standard Serial Number) of the journal.

        Returns:
            Works: An object for accessing works metadata related to the specified journal.
        """

        context = f"{self.ENDPOINT}/{issn!s}"
        return Works(
            context=context,
            etiquette=self.etiquette,
            throttle=self.throttle,
            crossref_plus_token=self.crossref_plus_token,
            timeout=self.timeout,
            verify=self.verify,
        )


class Depositor:
    def __init__(  # noqa: PLR0913
        self,
        prefix,
        api_user,
        api_key,
        etiquette=None,
        use_test_server=False,
        timeout=100,
    ):
        self.do_http_request = HTTPRequest(throttle=False).do_http_request
        self.etiquette = etiquette or Etiquette()
        self.custom_header = {"user-agent": str(self.etiquette)}
        self.prefix = prefix
        self.api_user = api_user
        self.api_key = api_key
        self.use_test_server = use_test_server
        self.timeout = timeout

    def get_endpoint(self, verb):
        subdomain = "test" if self.use_test_server else "doi"
        return f"https://{subdomain}.crossref.org/servlet/{verb}"

    def register_doi(self, submission_id: str, request_xml: str) -> requests.Response:
        """
        Register a new DOI or update metadata for an existing DOI in Crossref.

        This method submits a metadata deposit to Crossref, either registering a new DOI
        or updating the metadata of an existing DOI. The submission is performed using
        the Crossref deposit API and requires a valid XML document compliant with the
        Crossref Submission Schema.

        Args:
            submission_id (str): The identifier used as the submission file name. This file name
                can be referenced in future requests to check the status of the submission.
            request_xml (str): The XML string containing the document metadata, which must conform
                to the Crossref Submission Schema.

        Returns:
            requests.Response: The HTTP response object returned by the Crossref API.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API or submitting the
            data.

        """

        endpoint = self.get_endpoint("deposit")

        files = {"mdFile": (f"{submission_id}.xml", request_xml)}

        params = {
            "operation": "doMDUpload",
            "login_id": self.api_user,
            "login_passwd": self.api_key,
        }

        return self.do_http_request(
            "post",
            endpoint,
            data=params,
            files=files,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

    def request_doi_status_by_filename(self, file_name: str, data_type: str = "result"):
        """
        Retrieve the status or contents of a DOI submission by file name.

        This method queries the Crossref deposit API to fetch the status or the original
        XML contents of a DOI submission, identified by the provided file name. The type
        of data returned is controlled by the `data_type` parameter.

        Args:
            file_name (str): The unique file name used to identify the DOI deposit submission.
            data_type (str, optional): The type of data to retrieve. Accepts:
                - "result": Returns a JSON object with the status of the submission (default).
                - "contents": Returns the original XML submitted by the publisher.

        Returns:
            requests.Response: The HTTP response object containing the requested data.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.
        """

        endpoint = self.get_endpoint("submissionDownload")

        params = {
            "usr": self.api_user,
            "pwd": self.api_key,
            "file_name": file_name,
            "type": data_type,
        }

        return self.do_http_request(
            "get",
            endpoint,
            data=params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )

    def request_doi_status_by_batch_id(
        self, doi_batch_id: str, data_type: str = "result"
    ) -> requests.Response:
        """
        Retrieve the status or contents of a DOI submission by batch ID.

        This method queries the Crossref deposit API to fetch either the status or the original
        XML contents of a DOI submission, identified by the provided `doi_batch_id`. The type
        of data returned is controlled by the `data_type` parameter.

        Args:
            doi_batch_id (str): The unique batch ID used to identify the DOI deposit submission.
            data_type (str, optional): The type of data to retrieve. Accepts:
                - "result": Returns a response with the status of the submission (default).
                - "contents": Returns the original XML submitted by the publisher.

        Returns:
            requests.Response: The HTTP response object containing the requested data.

        Raises:
            RequestException: If there is an issue connecting to the Crossref API.

        """

        endpoint = self.get_endpoint("submissionDownload")

        params = {
            "usr": self.api_user,
            "pwd": self.api_key,
            "doi_batch_id": doi_batch_id,
            "type": data_type,
        }

        return self.do_http_request(
            "get",
            endpoint,
            data=params,
            custom_header=self.custom_header,
            timeout=self.timeout,
        )
