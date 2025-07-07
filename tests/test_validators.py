import pytest

from crossref import validators


def test_directory_1():
    result = validators.directory("DOAJ")

    assert result


def test_directory_2():
    with pytest.raises(ValueError, match="must be one of"):
        validators.directory("any invalid archive")


def test_archive_1():
    result = validators.archive("CLOCKSS")

    assert result


def test_archive_2():
    with pytest.raises(ValueError, match="must be one of"):
        validators.archive("any invalid archive")


def test_document_type_1():
    result = validators.document_type("book-chapter")

    assert result


def test_document_type_2():
    with pytest.raises(ValueError, match="must be one of"):
        validators.document_type("any invalid type")


def test_is_bool_3():
    result = validators.is_bool("true")

    assert result


def test_is_bool_4():
    result = validators.is_bool("false")

    assert result


def test_is_bool_5():
    result = validators.is_bool("1")

    assert result


def test_is_bool_6():
    with pytest.raises(ValueError, match="must be one of"):
        validators.is_bool("jljlj")


def test_is_date_1():
    result = validators.is_date("2017")

    assert result


def test_is_date_2():
    result = validators.is_date("2017-12")

    assert result


def test_is_date_3():
    result = validators.is_date("2017-12-31")

    assert result


def test_is_date_4():
    with pytest.raises(ValueError, match="Invalid date"):
        validators.is_date("asas")


def test_is_date_5():
    with pytest.raises(ValueError, match="Invalid date"):
        validators.is_date("2017-30")


def test_is_date_6():
    with pytest.raises(ValueError, match="Invalid date"):
        validators.is_date("2017-12-00")


def test_is_integer_1():
    result = validators.is_integer("10")

    assert result


def test_is_integer_2():
    with pytest.raises(ValueError, match="Integer specified as -1 but must be a positive integer."):
        validators.is_integer("-1")


def test_is_integer_3():
    with pytest.raises(ValueError, match="Integer specified as dd but must be a positive integer."):
        validators.is_integer("dd")
