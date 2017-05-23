# coding: utf-8
"""
Crossref Client that implements some of the Publisher Crossref API endpoints to
request a DOI number and follow the request status.
"""
import requests
import json

LIMIT = 100
MAXOFFSET = 10000


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


class APIExceptions(Exception):
    pass


class MaxOffsetException(StopIteration):
    pass


class RestfulClient(object):

    def rate_limits(self):

        endpoint = "http://api.crossref.org/members/1"

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

    def works(self, doi=None):
        params = {}
        endpoint = ["http://api.crossref.org/works"]

        endpoint.append(doi)

        endpoint = '/'.join([str(i) for i in endpoint if i is not None])

        if doi is not None:
            result = do_http_request('get', endpoint, data=params).json()
            yield result['message']
            raise StopIteration()

        params['offset'] = 0
        params['rows'] = LIMIT

        while True:

            result = do_http_request('get', endpoint, data=params).json()

            if len(result['message']['items']) == 0:
                break

            for item in result['message']['items']:
                yield item

            params['offset'] += LIMIT + 1

            if params['offset'] >= MAXOFFSET:
                raise MaxOffsetException(
                    'Offset exceded the max offset of %d' % MAXOFFISET)

    def funders(self, funders_id=None, works=False):
        params = {}
        endpoint = ["http://api.crossref.org/funders"]

        endpoint.append(funders_id)
        endpoint.append('works' if works is True else None)

        endpoint = '/'.join([str(i) for i in endpoint if i is not None])

        if funders_id is not None and works is False:
            result = do_http_request('get', endpoint, data=params).json()
            yield result['message']
            raise StopIteration()

        if funders_id is None and works is True:
            raise BadRequest('No funders_id given to retrieve works, funders_id must be given when works is set to True')

        params['offset'] = 0
        params['rows'] = LIMIT

        while True:

            result = do_http_request('get', endpoint, data=params).json()

            if len(result['message']['items']) == 0:
                break

            for item in result['message']['items']:
                yield item

            params['offset'] += LIMIT + 1

            if params['offset'] >= MAXOFFSET:
                raise MaxOffsetException(
                    'Offset exceded the max offset of %d' % MAXOFFISET)

    def prefixes(self, owner_prefix, works=False):
        params = {}
        endpoint = ["http://api.crossref.org/prefixes"]

        endpoint.append(owner_prefix)
        endpoint.append('works' if works is True else None)

        endpoint = '/'.join([str(i) for i in endpoint if i is not None])

        if works is False:
            result = do_http_request('get', endpoint, data=params).json()
            yield result['message']
            raise StopIteration()

        params['offset'] = 0
        params['rows'] = LIMIT

        while True:

            result = do_http_request('get', endpoint, data=params).json()

            if len(result['message']['items']) == 0:
                break

            for item in result['message']['items']:
                yield item

            params['offset'] += LIMIT + 1

            if params['offset'] >= MAXOFFSET:
                raise MaxOffsetException(
                    'Offset exceded the max offset of %d' % MAXOFFISET)


class DepositorClient(object):

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

    def _do_http_request(self, method, endpoint, data=None, files=None, timeout=10):

        if method == 'post':
            action = requests.post
        else:
            action = requests.get

        if method == 'post':
            result = action(endpoint, data=data, files=files, timeout=timeout)
        else:
            result = action(endpoint, params=data, timeout=timeout)

        return result

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

        result = self._do_http_request(
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

        result = self._do_http_request('get', endpoint, data=params, timeout=10)

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

        result = self._do_http_request('get', endpoint, data=params, timeout=10)

        return result
