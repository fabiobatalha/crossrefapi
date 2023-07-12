from datetime import datetime


def directory(value):
    expected = "DOAJ"

    if str(value) in expected:
        return True

    msg = "Directory specified as {} but must be one of: {}".format(str(value), ", ".join(expected))
    raise ValueError(
        msg,
    )


def archive(value):
    expected = ("Portico", "CLOCKSS", "DWT")

    if str(value) in expected:
        return True

    msg = "Archive specified as {} but must be one of: {}".format(str(value), ", ".join(expected))
    raise ValueError(
        msg,
    )


def document_type(value):

    expected = (
        "book-section",
        "monograph",
        "report",
        "book-track",
        "journal-article",
        "book-part",
        "other",
        "book",
        "journal-volume",
        "book-set",
        "reference-entry",
        "proceedings-article",
        "journal",
        "component",
        "book-chapter",
        "report-series",
        "proceedings",
        "standard",
        "reference-book",
        "posted-content",
        "journal-issue",
        "dissertation",
        "dataset",
        "book-series",
        "edited-book",
        "standard-series",
    )

    if str(value) in expected:
        return True

    msg = "Type specified as {} but must be one of: {}".format(str(value), ", ".join(expected))
    raise ValueError(
        msg,
    )


def is_bool(value):

    expected = ["t", "true", "1", "f", "false", "0"]

    if str(value) in expected:
        return True

    msg = "Boolean specified {} True but must be one of: {}".format(str(value), ", ".join(expected))
    raise ValueError(
        msg,
    )


def is_date(value):
    try:
        datetime.strptime(value, "%Y")  # noqa: DTZ007
    except ValueError:
        try:
            datetime.strptime(value, "%Y-%m")   # noqa: DTZ007
        except ValueError:
            try:
                datetime.strptime(value, "%Y-%m-%d")   # noqa: DTZ007
            except ValueError as exc:
                msg = f"Invalid date {value}."
                raise ValueError(msg) from exc
    return True


def is_integer(value):

    try:
        value = int(value)
        if value >= 0:
            return True
    except ValueError:
        pass

    raise ValueError("Integer specified as %s but must be a positive integer." % str(value))
