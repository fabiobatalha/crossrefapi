from datetime import datetime


def directory(value: str) -> bool:
    expected = "DOAJ"
    if str(value) in expected:
        return True
    oneof = ", ".join(expected)
    msg = f"Directory specified as {value!s} but must be one of: {oneof}"
    raise ValueError(msg)


def archive(value: str) -> bool:
    expected = ("Portico", "CLOCKSS", "DWT")
    if str(value) in expected:
        return True
    oneof = ", ".join(expected)
    msg = f"Archive specified as {value!s} but must be one of: {oneof}"
    raise ValueError(msg)


def document_type(value: str) -> bool:
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
    oneof = ", ".join(expected)
    msg = f"Type specified as {value!s} but must be one of: {oneof}"
    raise ValueError(msg)


def is_bool(value: str) -> bool:
    expected = ["t", "true", "1", "f", "false", "0"]
    if str(value) in expected:
        return True
    oneof = ", ".join(expected)
    msg = f"Boolean specified {value!s} True but must be one of: {oneof}"
    raise ValueError(msg)


def is_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y")  # noqa: DTZ007
    except ValueError:
        try:
            datetime.strptime(value, "%Y-%m")  # noqa: DTZ007
        except ValueError:
            try:
                datetime.strptime(value, "%Y-%m-%d")  # noqa: DTZ007
            except ValueError as exc:
                msg = f"Invalid date {value!s}."
                raise ValueError(msg) from exc
    return True


def is_integer(value: str | int) -> bool | None:
    try:
        value = int(value)
        if value >= 0:
            return True
    except ValueError:
        pass
    msg = f"Integer specified as {value!s} but must be a positive integer."
    raise ValueError(msg)
