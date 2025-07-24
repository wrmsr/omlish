# @omlish-lite
# ruff: noqa: UP006 UP007 UP043 UP045
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
import http.client
import re


##


class CoroHttpClientValidation:
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
