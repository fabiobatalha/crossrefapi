from crossref.utils import asbool


def is_bool(value):

    expected = ['t', 'true', '1', 'f', 'false', '0']

    if str(value).lower() in expected:
        return True

    return False
