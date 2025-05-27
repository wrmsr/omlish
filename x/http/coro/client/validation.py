# ruff: noqa: UP006 UP007
import http.client
import re


##


class HttpClientValidation:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    # These characters are not allowed within HTTP method names to prevent http header injection.
    _CONTAINS_DISALLOWED_METHOD_PCHAR_PAT = re.compile('[\x00-\x1f]')

    @classmethod
    def validate_method(cls, method: str) -> None:
        """Validate a method name for putrequest."""

        # prevent http header injection
        match = cls._CONTAINS_DISALLOWED_METHOD_PCHAR_PAT.search(method)
        if match:
            raise ValueError(
                f"method can't contain control characters. {method!r} (found at least {match.group()!r})",
            )

    #

    # These characters are not allowed within HTTP URL paths. See https://tools.ietf.org/html/rfc3986#section-3.3 and
    # the # https://tools.ietf.org/html/rfc3986#appendix-A pchar definition.
    #  - Prevents CVE-2019-9740.  Includes control characters such as \r\n.
    #  - We don't restrict chars above \x7f as putrequest() limits us to ASCII.
    _CONTAINS_DISALLOWED_URL_PCHAR_PAT = re.compile('[\x00-\x20\x7f]')

    @classmethod
    def validate_path(cls, url: str) -> None:
        """Validate a url for putrequest."""

        # Prevent CVE-2019-9740.
        match = cls._CONTAINS_DISALLOWED_URL_PCHAR_PAT.search(url)
        if match:
            raise http.client.InvalidURL(
                f"URL can't contain control characters. {url!r} (found at least {match.group()!r})",
            )

    @classmethod
    def validate_host(cls, host: str) -> None:
        """Validate a host so it doesn't contain control characters."""

        # Prevent CVE-2019-18348.
        match = cls._CONTAINS_DISALLOWED_URL_PCHAR_PAT.search(host)
        if match:
            raise http.client.InvalidURL(
                f"URL can't contain control characters. {host!r} (found at least {match.group()!r})",
            )

    #

    # The patterns for both name and value are more lenient than RFC definitions to allow for backwards compatibility.
    _LEGAL_HEADER_NAME_PAT = re.compile(rb'[^:\s][^:\r\n]*')
    _ILLEGAL_HEADER_VALUE_PAT = re.compile(rb'\n(?![ \t])|\r(?![ \t\n])')

    @classmethod
    def validate_header_name(cls, header: bytes) -> None:
        if not cls._LEGAL_HEADER_NAME_PAT.fullmatch(header):
            raise ValueError(f'Invalid header name {header!r}')

    @classmethod
    def validate_header_value(cls, value: bytes) -> None:
        if cls._ILLEGAL_HEADER_VALUE_PAT.search(value):
            raise ValueError(f'Invalid header value {value!r}')
