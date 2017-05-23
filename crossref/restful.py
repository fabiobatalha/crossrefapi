import requests
import json

LIMIT = 20
MAXOFFSET = 40
API = "api.crossref.org"

ORDER_VALUES = ['asc', 'desc', '1', '-1']
SORT_VALUES = [
    'score',
    'created',
    'issued',
    'indexed',
    'is-referenced-by-count',
    'relevance',
    'published',
    'published-print',
    'published-online',
    'submitted',
    'updated',
    'references-count',
    'deposited'
]
FIELDS_QUERY = [
    'affiliation',
    'event_acronym',
    'bibliographic',
    'container_title',
    'publisher_name',
    'author',
    'event_theme',
    'chair',
    'event_location',
    'translator',
    'funder_name',
    'event_name',
    'publisher_location',
    'title',
    'contributor',
    'editor',
    'event_sponsor'
]


class APIExceptions(Exception):
    pass


class MaxOffsetException(APIExceptions, StopIteration):
    pass


class BadRequest(APIExceptions, ValueError):
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


class Works(object):

    ENDPOINT = [API, 'works']

    def __init__(self, request_url=None, request_params=None):
        self.request_url = build_url_endpoint(self.ENDPOINT)
        self.request_params = request_params or dict()

    def url(self):
        escape_pagging = ['offset', 'rows']
        params = '&'.join(['='.join([k, v]) for k, v in self.request_params.items() if k not in escape_pagging])
        url = '?'.join([self.request_url, params])

        return url

    def order(self, order='asc'):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if order not in ORDER_VALUES:
            raise BadRequest(
                'Sort order specified as %s but must be one of: %s' % (
                    str(order),
                    ', '.join(SORT_VALUES)
                )
            )

        request_params['order'] = order

        return self.__class__(request_url, request_params)

    def sort(self, sort='score'):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if sort not in SORT_VALUES:
            raise BadRequest(
                'Sort field specified as %s but must be one of: ' % (
                    str(sort),
                    ', '.join(SORT_VALUES)
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

        return self.__class__(request_url, request_params)

    def query(self, *args, **kwargs):

        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if args:
            request_params['query'] = ' '.join(list(args))

        for field, value in kwargs.items():
            if field not in FIELDS_QUERY:
                raise BadRequest(
                    'Field query %s specified but there is no such field query for this route. Valid field queries for this route are: %s' % (
                        str(field), ', '.join(FIELDS_QUERY)
                    )
                )
            request_params['query.%s' % field.replace('_', '-')] = value

        return self.__class__(request_url, request_params)

    def all(self):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = {}

        return iter(self.__class__(request_url, request_params))

    def sample(self, sample_size=20):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = {}
        try:
            if sample_size > 100:
                raise BadRequest(
                    'Integer specified as %s but must be a positive integer less than or equal to 100.' % str(sample_size)
                )
        except TypeError:
            raise BadRequest(
                'Integer specified as %s but must be a positive integer less than or equal to 100.' % str(sample_size)
            )

        request_params['sample'] = sample_size

        return iter(self.__class__(request_url, request_params))

    def doi(self, doi):
        parts = self.ENDPOINT.append(doi)
        request_url = build_url_endpoint(parts)
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return result['message']

    def __iter__(self):
        self.request_params['offset'] = 0
        self.request_params['rows'] = LIMIT

        while True:
            result = do_http_request(
                'get', self.request_url, data=self.request_params).json()

            if len(result['message']['items']) == 0:
                raise StopIteration()

            for item in result['message']['items']:
                yield item

            self.request_params['offset'] += LIMIT + 1

            if self.request_params['offset'] >= MAXOFFSET:
                raise MaxOffsetException(
                    'Offset exceded the max offset of %d',
                    MAXOFFSET
                )

    _gen = __iter__


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
