from crossref.utils import asbool
from datetime import datetime


def is_bool(value):

    expected = ['t', 'true', '1', 'f', 'false', '0']

    if str(value).lower() in expected:
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
