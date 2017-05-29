# coding: utf-8

from crossref.utils import asbool
from datetime import datetime


def directory(value):
    expected = (
        'DOAJ'
    )

    if str(value) in expected:
        return True

    raise ValueError('Directory specified as %s but must be one of: %s' % (
            str(value),
            ', '.join(expected)
        )
    )


def archive(value):
    expected = (
        'Portico',
        'CLOCKSS',
        'DWT'
        )

    if str(value) in expected:
        return True

    raise ValueError('Archive specified as %s but must be one of: %s' % (
            str(value),
            ', '.join(expected)
        )
    )


def document_type(value):

    expected = (
        'book-section',
        'monograph',
        'report',
        'book-track',
        'journal-article',
        'book-part',
        'other',
        'book',
        'journal-volume',
        'book-set',
        'reference-entry',
        'proceedings-article',
        'journal',
        'component',
        'book-chapter',
        'report-series',
        'proceedings',
        'standard',
        'reference-book',
        'posted-content',
        'journal-issue',
        'dissertation',
        'dataset',
        'book-series',
        'edited-book',
        'standard-series'
    )

    if str(value) in expected:
        return True

    raise ValueError('Type specified as %s but must be one of: %s' % (
            str(value),
            ', '.join(expected)
        )
    )


def is_bool(value):

    expected = ['t', 'true', '1', 'f', 'false', '0']

    if str(value) in expected:
        return True

    raise ValueError('Boolean specified %s True but must be one of: %s' % (
            str(value),
            ', '.join(expected)
        )
    )


def is_date(value):

    try:
        datetime.strptime(value, '%Y')
        return True
    except ValueError:
        try:
            datetime.strptime(value, '%Y-%m')
            return True
        except ValueError:
            try:
                datetime.strptime(value, '%Y-%m-%d')
                return True
            except:
                pass

    raise ValueError('Date specified as %s but must be of the form: yyyy or yyyy-mm or yyyy-mm-dd ' % str(value))


def is_integer(value):

    try:
        value = int(value)
        if value >= 0:
            return True
    except ValueError:
        pass

    raise ValueError('Integer specified as %s but must be a positive integer.' % str(value))
