"""
https://github.com/pallets/werkzeug/blob/9e050f7750214d6779636813b8d661250804e811/src/werkzeug/http.py
https://github.com/pallets/werkzeug/blob/9e050f7750214d6779636813b8d661250804e811/src/werkzeug/sansio/http.py
"""
# Copyright 2007 Pallets
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#     disclaimer.
#
# 2.  Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#     following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3.  Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import datetime
import re
import typing as ta
import urllib.parse

from .. import collections as col
from .dates import http_date


##


_COOKIE_RE = re.compile(
    r"""
    ([^=;]*)
    (?:\s*=\s*
      (
        "(?:[^\\"]|\\.)*"
      |
        .*?
      )
    )?
    \s*;\s*
    """,
    flags=re.ASCII | re.VERBOSE,
)
_COOKIE_UNSLASH_RE = re.compile(rb'\\([0-3][0-7]{2}|.)')


def _cookie_unslash_replace(m: ta.Match[bytes]) -> bytes:
    v = m.group(1)

    if len(v) == 1:
        return v

    return int(v, 8).to_bytes(1, 'big')


def parse_cookie(
        cookie: str | None = None,
        *,
        no_latin1: bool = False,
) -> ta.MutableMapping[str, list[str]]:
    if (not no_latin1) and cookie:
        cookie = cookie.encode('latin1').decode()

    if not cookie:
        return {}

    cookie = f'{cookie};'
    out = []

    for ck, cv in _COOKIE_RE.findall(cookie):
        ck = ck.strip()
        cv = cv.strip()

        if not ck:
            continue

        if len(cv) >= 2 and cv[0] == cv[-1] == '"':
            # Work with bytes here, since a UTF-8 character could be multiple bytes.
            cv = _COOKIE_UNSLASH_RE.sub(
                _cookie_unslash_replace,
                cv[1:-1].encode(),
            ).decode(errors='replace')

        out.append((ck, cv))

    return col.multi_map(out)


##


_COOKIE_NO_QUOTE_RE = re.compile(r"[\w!#$%&'()*+\-./:<=>?@\[\]^`{|}~]*", re.ASCII)
_COOKIE_SLASH_RE = re.compile(rb'[\x00-\x19\",;\\\x7f-\xff]', re.ASCII)
_COOKIE_SLASH_MAP = {b'"': b'\\"', b'\\': b'\\\\'}
_COOKIE_SLASH_MAP.update(
    (v.to_bytes(1, 'big'), b'\\%03o' % v)
    for v in [*range(0x20), *b',;', *range(0x7F, 256)]
)


class CookieTooBigError(Exception):
    pass


def dump_cookie(
        key: str,
        value: str = '',
        *,
        max_age: datetime.timedelta | int | None = None,
        expires: str | datetime.datetime | float | None = None,
        path: str | None = '/',
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        sync_expires: bool = True,
        max_size: int = 4093,
        samesite: str | None = None,
        partitioned: bool = False,
) -> str:
    if path is not None:
        # safe = https://url.spec.whatwg.org/#url-path-segment-string as well as percent for things that are already
        # quoted excluding semicolon since it's part of the header syntax
        path = urllib.parse.quote(path, safe="%!$&'()*+,/:=@")

    if domain:
        domain = domain.partition(':')[0].lstrip('.').encode('idna').decode('ascii')

    if isinstance(max_age, datetime.timedelta):
        max_age = int(max_age.total_seconds())

    if expires is not None:
        if not isinstance(expires, str):
            expires = http_date(expires)
    elif max_age is not None and sync_expires:
        expires = http_date(datetime.datetime.now(tz=datetime.UTC).timestamp() + max_age)

    if samesite is not None:
        samesite = samesite.title()

        if samesite not in {'Strict', 'Lax', 'None'}:
            raise ValueError("SameSite must be 'Strict', 'Lax', or 'None'.")

    if partitioned:
        secure = True

    # Quote value if it contains characters not allowed by RFC 6265. Slash-escape with
    # three octal digits, which matches http.cookies, although the RFC suggests base64.
    if not _COOKIE_NO_QUOTE_RE.fullmatch(value):
        # Work with bytes here, since a UTF-8 character could be multiple bytes.
        value = _COOKIE_SLASH_RE.sub(
            lambda m: _COOKIE_SLASH_MAP[m.group()], value.encode(),
        ).decode('ascii')
        value = f'"{value}"'

    # Send a non-ASCII key as mojibake. Everything else should already be ASCII.
    # TODO Remove encoding dance, it seems like clients accept UTF-8 keys
    buf = [f"{key.encode().decode('latin1')}={value}"]

    for k, v in (
            ('Domain', domain),
            ('Expires', expires),
            ('Max-Age', max_age),
            ('Secure', secure),
            ('HttpOnly', httponly),
            ('Path', path),
            ('SameSite', samesite),
            ('Partitioned', partitioned),
    ):
        if v is None or v is False:
            continue

        if v is True:
            buf.append(k)
            continue

        buf.append(f'{k}={v}')

    rv = '; '.join(buf)

    # Warn if the final value of the cookie is larger than the limit. If the cookie is too large, then it may be
    # silently ignored by the browser, which can be quite hard to debug.
    cookie_size = len(rv)
    if max_size and cookie_size > max_size:
        raise CookieTooBigError(cookie_size)

    return rv
