import requests
import json

from crossref import validators

LIMIT = 100
MAXOFFSET = 10000
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


def build_url_endpoint(endpoint, context=None):

    endpoint = '/'.join([i for i in [context, endpoint] if i])

    return 'https://%s/%s' % (API, endpoint)


class Endpoint:

    def __init__(self, request_url=None, request_params=None, context=None, cursor_as_iter_method=True):
        self.request_url = request_url or build_url_endpoint(self.ENDPOINT, context)
        self.request_params = request_params or dict()
        self.context = context or ''
        self.cursor_as_iter_method = cursor_as_iter_method

    @property
    def _rate_limits(self):
        request_params = dict(self.request_params)
        request_url = str(self.request_url)

        result = do_http_request('get', request_url, only_headers=True)

        rate_limits = {
            'X-Rate-Limit-Limit': result.headers.get('X-Rate-Limit-Limit', 'undefined'),
            'X-Rate-Limit-Interval': result.headers.get('X-Rate-Limit-Interval', 'undefined')
        }

        return rate_limits

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
    def version(self):
        request_params = dict(self.request_params)
        request_url = str(self.request_url)

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return result['message-version']

    @property
    def x_rate_limit_limit(self):

        return self._rate_limits.get('X-Rate-Limit-Limit', 'undefined')

    @property
    def x_rate_limit_interval(self):

        return self._rate_limits.get('X-Rate-Limit-Interval', 'undefined')

    def count(self):
        request_params = dict(self.request_params)
        request_url = str(self.request_url)
        request_params['rows'] = 0

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return int(result['message']['total-results'])

    @property
    def url(self):
        request_params = self._escaped_pagging()

        req = requests.Request(
            'get', self.request_url, params=request_params).prepare()

        return req.url

    def all(self):
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        cursor_as_iter_method = bool(self.cursor_as_iter_method)
        request_params = {}

        return iter(self.__class__(request_url, request_params, context, cursor_as_iter_method))

    def __iter__(self):
        request_url = str(self.request_url)
        if 'sample' in self.request_params:
            request_params = self._escaped_pagging()
            result = do_http_request(
                'get', self.request_url, data=request_params).json()

            for item in result['message']['items']:
                yield item

            return

        if self.cursor_as_iter_method == True:
            request_params = dict(self.request_params)
            request_params['cursor'] = '*'
            request_params['rows'] = LIMIT
            while True:
                result = do_http_request(
                    'get', request_url, data=request_params).json()

                if len(result['message']['items']) == 0:
                    return

                for item in result['message']['items']:
                    yield item

                request_params['cursor'] = result['message']['next-cursor']
        else:
            request_params = dict(self.request_params)
            request_params['offset'] = 0
            request_params['rows'] = LIMIT
            while True:
                result = do_http_request(
                    'get', request_url, data=request_params).json()

                if len(result['message']['items']) == 0:
                    return

                for item in result['message']['items']:
                    yield item

                request_params['offset'] += LIMIT + 1

                if request_params['offset'] >= MAXOFFSET:
                    raise MaxOffsetError(
                        'Offset exceded the max offset of %d',
                        MAXOFFSET
                    )


class Works(Endpoint):

    ENDPOINT = 'works'

    ORDER_VALUES = ('asc', 'desc', '1', '-1')

    SORT_VALUES = (
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
    )

    FIELDS_QUERY = (
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
    )

    FILTER_VALIDATOR = {
        'alternative_id': None,
        'archive': validators.archive,
        'article_number': None,
        'assertion': None,
        'assertion-group': None,
        'award.funder': None,
        'award.number': None,
        'category-name': None,
        'clinical-trial-number': None,
        'container-title': None,
        'content-domain': None,
        'directory': validators.directory,
        'doi': None,
        'from-accepted_date': validators.is_date,
        'from-created-date': validators.is_date,
        'from-deposit-date': validators.is_date,
        'from-event-end-date': validators.is_date,
        'from-event-start-date': validators.is_date,
        'from-index-date': validators.is_date,
        'from-issued-date': validators.is_date,
        'from-online-pub-date': validators.is_date,
        'from-posted-date': validators.is_date,
        'from-print-pub-date': validators.is_date,
        'from-pub-date': validators.is_date,
        'from-update-date': validators.is_date,
        'full-text.application': None,
        'full-text.type': None,
        'full-text.version': None,
        'funder': None,
        'funder-doi-asserted-by': None,
        'group-title': None,
        'has_abstract': validators.is_bool,
        'has-affiliation': validators.is_bool,
        'has-archive': validators.is_bool,
        'has-assertion': validators.is_bool,
        'has-authenticated-orcid': validators.is_bool,
        'has-award': validators.is_bool,
        'has-clinical-trial-number': validators.is_bool,
        'has-content-domain': validators.is_bool,
        'has-domain-restriction': validators.is_bool,
        'has-event': validators.is_bool,
        'has-full-text': validators.is_bool,
        'has-funder': validators.is_bool,
        'has-funder-doi': validators.is_bool,
        'has-license': validators.is_bool,
        'has-orcid': validators.is_bool,
        'has-references': validators.is_bool,
        'has-relation': validators.is_bool,
        'has-update': validators.is_bool,
        'has-update-policy': validators.is_bool,
        'is-update': validators.is_bool,
        'isbn': None,
        'issn': None,
        'license.delay': validators.is_integer,
        'license.url': None,
        'license.version': None,
        'member': validators.is_integer,
        'orcid': None,
        'prefix': None,
        'relation.object': None,
        'relation.object-type': None,
        'relation.type': None,
        'type': validators.document_type,
        'type-name': None,
        'until-accepted-date': validators.is_bool,
        'until-created-date': validators.is_bool,
        'until-deposit-date': validators.is_bool,
        'until-event-end-date': validators.is_bool,
        'until-event-start-date': validators.is_bool,
        'until-index-date': validators.is_bool,
        'until-issued-date': validators.is_bool,
        'until-online-pub-date': validators.is_bool,
        'until-posted-date': validators.is_bool,
        'until-print-pub-date': validators.is_bool,
        'until-pub-date': validators.is_bool,
        'until-update-date': validators.is_bool,
        'update-type': None,
        'updates': None
     }

    def order(self, order='asc'):
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)
        cursor_as_iter_method = bool(self.cursor_as_iter_method)

        if order not in self.ORDER_VALUES:
            raise UrlSyntaxError(
                'Sort order specified as %s but must be one of: %s' % (
                    str(order),
                    ', '.join(self.ORDER_VALUES)
                )
            )

        request_params['order'] = order

        return self.__class__(request_url, request_params, context, cursor_as_iter_method)

    def sort(self, sort='score'):
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)
        cursor_as_iter_method = bool(self.cursor_as_iter_method)

        if sort not in self.SORT_VALUES:
            raise UrlSyntaxError(
                'Sort field specified as %s but must be one of: %s' % (
                    str(sort),
                    ', '.join(self.SORT_VALUES)
                )
            )

        request_params['sort'] = sort

        return self.__class__(request_url, request_params, context, cursor_as_iter_method)

    def filter(self, **kwargs):
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)
        cursor_as_iter_method = bool(self.cursor_as_iter_method)

        for fltr, value in kwargs.items():
            decoded_fltr = fltr.replace('__', '.').replace('_', '-')
            if decoded_fltr not in self.FILTER_VALIDATOR.keys():
                raise UrlSyntaxError(
                    'Filter %s specified but there is no such filter for this route. Valid filters for this route are: %s' % (
                        str(decoded_fltr),
                        ', '.join(self.FILTER_VALIDATOR.keys())
                    )
                )

            if self.FILTER_VALIDATOR[decoded_fltr] is not None:
                self.FILTER_VALIDATOR[decoded_fltr](str(value))

            if 'filter' not in request_params:
                request_params['filter'] = decoded_fltr + ':' + str(value)
            else:
                request_params['filter'] += ',' + decoded_fltr + ':' + str(value)

        return self.__class__(request_url, request_params, context, cursor_as_iter_method)

    def query(self, *args, **kwargs):
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)
        cursor_as_iter_method = bool(self.cursor_as_iter_method)

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

        return self.__class__(request_url, request_params, context, cursor_as_iter_method)

    def sample(self, sample_size=20):
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
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

        return self.__class__(request_url, request_params, context)

    def doi(self, doi):
        request_url = build_url_endpoint(
            '/'.join([self.ENDPOINT, doi])
        )
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return result['message']

    def doi_exists(self, doi):
        request_url = build_url_endpoint(
            '/'.join([self.ENDPOINT, doi])
        )
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params, only_headers=True)

        if result.status_code == 404:
            return False

        return True


class Funders(Endpoint):

    ENDPOINT = 'funders'

    def query(self, *args):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if args:
            request_params['query'] = ' '.join(list(args))

        return self.__class__(request_url, request_params)

    def funder(self, funder_id):
        request_url = build_url_endpoint(
            '/'.join([self.ENDPOINT, str(funder_id)])
        )
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return result['message']

    def funder_exists(self, funder_id):
        request_url = build_url_endpoint(
            '/'.join([self.ENDPOINT, str(funder_id)])
        )
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params, only_headers=True)

        if result.status_code == 404:
            return False

        return True

    def works(self, funder_id):

        context = '%s/%s' % (self.ENDPOINT, str(funder_id))
        return Works(context=context)


class Members(Endpoint):

    ENDPOINT = 'members'

    def query(self, *args):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if args:
            request_params['query'] = ' '.join(list(args))

        return self.__class__(request_url, request_params)

    def member(self, member_id):
        request_url = build_url_endpoint(
            '/'.join([self.ENDPOINT, str(member_id)])
        )
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return result['message']

    def member_exists(self, member_id):
        request_url = build_url_endpoint(
            '/'.join([self.ENDPOINT, str(member_id)])
        )
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params, only_headers=True)

        if result.status_code == 404:
            return False

        return True

    def works(self, member_id):

        context = '%s/%s' % (self.ENDPOINT, str(member_id))
        return Works(context=context)


class Types(Endpoint):

    ENDPOINT = 'types'

    def type(self, type_id):
        request_url = build_url_endpoint(
            '/'.join([self.ENDPOINT, str(type_id)])
        )
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return result['message']

    def all(self):
        context = str(self.context)
        request_url = build_url_endpoint(self.ENDPOINT, context)
        request_params = dict(self.request_params)

        result = do_http_request(
            'get', request_url, data=request_params).json()

        for item in result['message']['items']:
            yield item

    def works(self, type_id):

        context = '%s/%s' % (self.ENDPOINT, str(type_id))
        return Works(context=context)


class Prefixes(Endpoint):

    ENDPOINT = 'prefixes'

    def prefix(self, prefix_id):
        request_url = build_url_endpoint(
            '/'.join([self.ENDPOINT, str(prefix_id)])
        )
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return result['message']

    def works(self, prefix_id):

        context = '%s/%s' % (self.ENDPOINT, str(prefix_id))
        return Works(context=context)


class Journals(Endpoint):

    ENDPOINT = 'journals'

    def query(self, *args):
        request_url = build_url_endpoint(self.ENDPOINT)
        request_params = dict(self.request_params)

        if args:
            request_params['query'] = ' '.join(list(args))

        return self.__class__(request_url, request_params)

    def journal(self, journal_id):
        request_url = build_url_endpoint(
            '/'.join([self.ENDPOINT, str(journal_id)])
        )
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params).json()

        return result['message']

    def journal_exists(self, journal_id):
        request_url = build_url_endpoint(
            '/'.join([self.ENDPOINT, str(journal_id)])
        )
        request_params = {}

        result = do_http_request(
            'get', request_url, data=request_params, only_headers=True)

        if result.status_code == 404:
            return False

        return True

    def works(self, journal_id):

        context = '%s/%s' % (self.ENDPOINT, str(journal_id))
        return Works(context=context)


class Depositor(object):

    def __init__(self, prefix, api_user, api_key):

        self.prefix = prefix
        self.api_user = api_user
        self.api_key = api_key

    def register_doi(self, submission_id, request_xml):
        """
        This method registry a new DOI number in Crossref or update some DOI
        metadata.

        submission_id: Will be used as the submission file name. The file name
        could be used in future requests to retrieve the submission status.

        request_xml: The XML with the document metadata. It must be under
        compliance with the Crossref Submission Schema.
        """

        endpoint = "https://doi.crossref.org/servlet/deposit"

        files = {
            'mdFile': ('%s.xml' % submission_id, request_xml)
        }

        params = {
            'operation': 'doMDUpload',
            'login_id': self.api_user,
            'login_passwd': self.api_key
        }

        result = do_http_request(
            'post', endpoint, data=params, files=files, timeout=10)

        return result

    def request_doi_status_by_filename(self, file_name, data_type='result'):
        """
        This method retrieve the DOI requests status.

        file_name: Used as unique ID to identify a deposit.

        data_type: [contents, result]
            contents - retrieve the XML submited by the publisher
            result - retrieve a JSON with the status of the submission
        """

        endpoint = "https://doi.crossref.org/servlet/submissionDownload"

        params = {
            'usr': self.api_user,
            'pwd': self.api_key,
            'file_name': file_name,
            'type': data_type
        }

        result = do_http_request('get', endpoint, data=params, timeout=10)

        return result

    def request_doi_status_by_batch_id(self, doi_batch_id, data_type='result'):
        """
        This method retrieve the DOI requests status.

        file_name: Used as unique ID to identify a deposit.

        data_type: [contents, result]
            contents - retrieve the XML submited by the publisher
            result - retrieve a XML with the status of the submission
        """

        endpoint = "https://doi.crossref.org/servlet/submissionDownload"

        params = {
            'usr': self.api_user,
            'pwd': self.api_key,
            'doi_batch_id': doi_batch_id,
            'type': data_type
        }

        result = do_http_request('get', endpoint, data=params, timeout=10)

        return result
