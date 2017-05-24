import requests
import json

from crossref import validators

LIMIT = 20
MAXOFFSET = 40
API = "api.crossref.org"


class CrossrefAPIError(Exception):
    pass


class MaxOffsetError(CrossrefAPIError):
    pass


class UrlSyntaxError(CrossrefAPIError, ValueError):
    pass


def do_http_request(method, endpoint, data=None, files=None, timeout=10, only_headers=False):

    if method == 'post':
        action = requests.post
    else:
        action = requests.get

    if only_headers is True:
        return requests.head(endpoint)

    if method == 'post':
        result = action(endpoint, data=data, files=files, timeout=timeout)
    else:
        result = action(endpoint, params=data, timeout=timeout)

    return result


def build_url_endpoint(parts):
    return 'http://%s' % '/'.join([str(i) for i in parts if i is not None])


class Endpoint:

    def __init__(self, request_url=None, request_params=None):
        self.request_url = build_url_endpoint(self.ENDPOINT)
        self.request_params = request_params or dict()

    def _escaped_pagging(self):
        escape_pagging = ['offset', 'rows']
        request_params = dict(self.request_params)

        for item in escape_pagging:
            try:
                del(request_params[item])
            except KeyError:
                pass

        return request_params

    @property
    def url(self):
        request_params = self._escaped_pagging()
        req = requests.Request(
            'get', self.request_url, params=request_params).prepare()

        return req.url

    def all(self):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = {}

        return iter(self.__class__(request_url, request_params))

    def __iter__(self):

        if 'sample' in self.request_params:
            request_params = self._escaped_pagging()
            result = do_http_request(
                'get', self.request_url, data=request_params).json()

            for item in result['message']['items']:
                yield item

            return

        self.request_params['offset'] = 0
        self.request_params['rows'] = LIMIT

        while True:
            result = do_http_request(
                'get', self.request_url, data=self.request_params).json()

            if len(result['message']['items']) == 0:
                return

            for item in result['message']['items']:
                yield item

            self.request_params['offset'] += LIMIT + 1

            if self.request_params['offset'] >= MAXOFFSET:
                raise MaxOffsetError(
                    'Offset exceded the max offset of %d',
                    MAXOFFSET
                )


class Works(Endpoint):

    ENDPOINT = [API, 'works']

    ORDER_VALUES = ['asc', 'desc', '1', '-1']

    SORT_VALUES = [
        'created',
        'deposited',
        'indexed',
        'is-referenced-by-count',
        'issued',
        'published',
        'published-online',
        'published-print',
        'references-count',
        'relevance',
        'score',
        'submitted',
        'updated'
    ]

    FIELDS_QUERY = [
        'affiliation',
        'author',
        'bibliographic',
        'chair',
        'container_title',
        'contributor',
        'editor',
        'event_acronym',
        'event_location',
        'event_name',
        'event_sponsor',
        'event_theme',
        'funder_name',
        'publisher_location',
        'publisher_name',
        'title',
        'translator'
    ]

    FILTER_VALUES = [
        ('alternative-id', None),
        ('archive', None),
        ('article-number', None),
        'assertion',
        'assertion-group',
        'award.funder',
        'award.number',
        'category-name',
        'clinical-trial-number',
        'container-title',
        'content-domain',
        'directory',
        'doi',
        ('from-accepted-date', validator.is_date),
        'from-created-date',
        'from-deposit-date',
        'from-event-end-date',
        'from-event-start-date',
        'from-index-date',
        'from-issued-date',
        'from-online-pub-date',
        'from-posted-date',
        'from-print-pub-date',
        'from-pub-date',
        'from-update-date',
        'full-text.application',
        'full-text.type',
        'full-text.version',
        'funder',
        'funder-doi-asserted-by',
        'group-title',
        ('has-abstract', validator.is_bool),
        'has-affiliation',
        'has-archive',
        'has-assertion',
        'has-authenticated-orcid',
        'has-award',
        'has-clinical-trial-number',
        'has-content-domain',
        'has-domain-restriction',
        'has-event',
        'has-full-text',
        'has-funder',
        'has-funder-doi',
        'has-license',
        'has-orcid',
        'has-references',
        'has-relation',
        'has-update',
        'has-update-policy',
        'is-update',
        'isbn',
        'issn',
        'license.delay',
        'license.url',
        'license.version',
        'member',
        'orcid',
        'prefix',
        'relation.object',
        'relation.object-type',
        'relation.type',
        'type',
        'type-name',
        'until-accepted-date',
        'until-created-date',
        'until-deposit-date',
        'until-event-end-date',
        'until-event-start-date',
        'until-index-date',
        'until-issued-date',
        'until-online-pub-date',
        'until-posted-date',
        'until-print-pub-date',
        'until-pub-date',
        'until-update-date',
        'update-type',
        'updates'
     ]

    def order(self, order='asc'):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if order not in self.ORDER_VALUES:
            raise UrlSyntaxError(
                'Sort order specified as %s but must be one of: %s' % (
                    str(order),
                    ', '.join(self.ORDER_VALUES)
                )
            )

        request_params['order'] = order

        return self.__class__(request_url, request_params)

    def sort(self, sort='score'):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if sort not in self.SORT_VALUES:
            raise UrlSyntaxError(
                'Sort field specified as %s but must be one of: %s' % (
                    str(sort),
                    ', '.join(self.SORT_VALUES)
                )
            )

        request_params['sort'] = sort

        return self.__class__(request_url, request_params)

    def filter(self, filter=None):
        parts = [self.ENDPOINT]
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)
        if filter:
            request_params['filter'] = filter

            "Filter sdsd specified but there is no such filter for this route. Valid filters for this route are: has-assertion, from-print-pub-date, until-deposit-date, from-accepted-date, has-authenticated-orcid, from-created-date, relation.object, issn, until-online-pub-date, group-title, full-text.application, until-created-date, license.version, from-deposit-date, has-abstract, has-event, funder, assertion-group, from-online-pub-date, from-issued-date, directory, content-domain, license.url, from-index-date, full-text.version, full-text.type, until-posted-date, has-orcid, has-archive, type, is-update, until-event-start-date, update-type, from-pub-date, has-license, funder-doi-asserted-by, isbn, has-full-text, doi, orcid, has-content-domain, prefix, until-event-end-date, has-funder, award.funder, clinical-trial-number, member, has-domain-restriction, until-accepted-date, container-title, license.delay, from-posted-date, has-affiliation, from-update-date, has-award, until-print-pub-date, from-event-start-date, has-funder-doi, until-index-date, has-update, until-update-date, until-issued-date, until-pub-date, award.number, has-references, type-name, has-relation, alternative-id, archive, relation.type, updates, relation.object-type, category-name, has-clinical-trial-number, assertion, article-number, has-update-policy, from-event-end-date"

        return self.__class__(request_url, request_params)

    def query(self, *args, **kwargs):

        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if args:
            request_params['query'] = ' '.join(list(args))

        for field, value in kwargs.items():
            if field not in self.FIELDS_QUERY:
                raise UrlSyntaxError(
                    'Field query %s specified but there is no such field query for this route. Valid field queries for this route are: %s' % (
                        str(field), ', '.join(self.FIELDS_QUERY)
                    )
                )
            request_params['query.%s' % field.replace('_', '-')] = value

        return self.__class__(request_url, request_params)

    def sample(self, sample_size=20):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = {}
        try:
            if sample_size > 100:
                raise UrlSyntaxError(
                    'Integer specified as %s but must be a positive integer less than or equal to 100.' % str(sample_size)
                )
        except TypeError:
            raise UrlSyntaxError(
                'Integer specified as %s but must be a positive integer less than or equal to 100.' % str(sample_size)
            )

        request_params['sample'] = sample_size

        return self.__class__(request_url, request_params)

    def doi(self, doi):
        self.ENDPOINT.append(doi)
        parts = self.ENDPOINT
        request_url = build_url_endpoint(parts)
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return result['message']


class Funders(Endpoint):

    ENDPOINT = [API, 'funders']

    def query(self, *args):

        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if args:
            request_params['query'] = ' '.join(list(args))

        return self.__class__(request_url, request_params)

    def funder(self, funder_id):
        self.ENDPOINT.append(funder_id)
        parts = self.ENDPOINT
        request_url = build_url_endpoint(parts)
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return result['message']


class RestfulClient(Works):

    def rate_limits(self):

        endpoint = build_url_endpoint(['members', '1'])

        result = do_http_request('get', endpoint, only_headers=True)

        rate_limits = {
            'X-Rate-Limit-Limit': result.headers.get('X-Rate-Limit-Limit', 'undefined'),
            'X-Rate-Limit-Interval': result.headers.get('X-Rate-Limit-Interval', 'undefined')
        }

        return rate_limits

    @property
    def x_rate_limit_limit(self):

        return self.rate_limits['X-Rate-Limit-Limit']

    @property
    def x_rate_limit_interval(self):

        return self.rate_limits['X-Rate-Limit-Interval']

    @property
    def works(self):

        return Works()
