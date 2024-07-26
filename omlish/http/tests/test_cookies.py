"""
https://github.com/pallets/werkzeug/blob/9e050f7750214d6779636813b8d661250804e811/tests/test_py
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
import pytest

from ..cookies import CookieTooBigError
from ..cookies import dump_cookie
from ..cookies import parse_cookie
from ..encodings import latin1_decode


def test_parse_cookie():
    cookies = parse_cookie(
        "dismiss-top=6; CP=null*; PHPSESSID=0a539d42abc001cdc762809248d4beed;"
        'a=42; b="\\";"; ; fo234{=bar;blub=Blah; "__Secure-c"=d;'
        "==__Host-eq=bad;__Host-eq=good;"
    )
    assert cookies == {
        "CP": ["null*"],
        "PHPSESSID": ["0a539d42abc001cdc762809248d4beed"],
        "a": ["42"],
        "dismiss-top": ["6"],
        "b": ['";'],
        "fo234{": ["bar"],
        "blub": ["Blah"],
        '"__Secure-c"': ["d"],
        "__Host-eq": ["good"],
    }


def test_dump_cookie():
    rv = dump_cookie(
        "foo",
        "bar baz blub",
        max_age=360,
        httponly=True,
        sync_expires=False,
    )
    assert set(rv.split("; ")) == {
        "HttpOnly",
        "Max-Age=360",
        "Path=/",
        'foo="bar baz blub"',
    }
    assert dump_cookie("key", "xxx/") == "key=xxx/; Path=/"
    assert dump_cookie("key", "xxx=", path=None) == "key=xxx="


def test_bad_cookies():
    cookies = parse_cookie(
        "first=IamTheFirst ; a=1; oops ; a=2 ;second = andMeTwo;"
    )
    expect = {
        "first": ["IamTheFirst"],
        "a": ["1", "2"],
        "oops": [""],
        "second": ["andMeTwo"],
    }
    assert cookies == expect
    assert cookies["a"] == ["1", "2"]


def test_empty_keys_are_ignored():
    cookies = parse_cookie("spam=ham; duck=mallard; ; ")
    expect = {"spam": ["ham"], "duck": ["mallard"]}
    assert cookies == expect


def test_cookie_quoting():
    val = dump_cookie("foo", "?foo")
    assert val == "foo=?foo; Path=/"
    assert parse_cookie(val)["foo"] == ["?foo"]
    assert parse_cookie(r'foo="foo\054bar"')["foo"] == ["foo,bar"]


def test_parse_set_cookie_directive():
    val = 'foo="?foo"; version="0.1";'
    assert parse_cookie(val) == {"foo": ["?foo"], "version": ["0.1"]}


def test_cookie_domain_resolving():
    val = dump_cookie("foo", "bar", domain="\N{SNOWMAN}.com")
    assert val == "foo=bar; Domain=xn--n3h.com; Path=/"


def test_cookie_unicode_dumping():
    val = dump_cookie("foo", "\N{SNOWMAN}")
    assert val == 'foo="\\342\\230\\203"; Path=/'
    cookies = parse_cookie(val)
    assert cookies["foo"] == ["\N{SNOWMAN}"]


def test_cookie_unicode_keys():
    # Yes, this is technically against the spec but happens
    val = dump_cookie("fö", "fö")
    assert val == latin1_decode('fö="f\\303\\266"; Path=/')
    cookies = parse_cookie(val)
    assert cookies["fö"] == "fö"


def test_cookie_unicode_parsing():
    # This is submitted by Firefox if you set a Unicode cookie.
    cookies = parse_cookie("fÃ¶=fÃ¶")
    assert cookies["fö"] == ["fö"]


def test_cookie_domain_encoding():
    val = dump_cookie("foo", "bar", domain="\N{SNOWMAN}.com")
    assert val == "foo=bar; Domain=xn--n3h.com; Path=/"

    val = dump_cookie("foo", "bar", domain="foo.com")
    assert val == "foo=bar; Domain=foo.com; Path=/"


def test_cookie_maxsize():
    val = dump_cookie("foo", "bar" * 1360 + "b")
    assert len(val) == 4093

    with pytest.raises(CookieTooBigError):
        dump_cookie("foo", "bar" * 1360 + "ba")

    with pytest.raises(CookieTooBigError):
        dump_cookie("foo", "w" * 501, max_size=512)


@pytest.mark.parametrize(
    ("samesite", "expected"),
    (
            ("strict", "foo=bar; SameSite=Strict"),
            ("lax", "foo=bar; SameSite=Lax"),
            ("none", "foo=bar; SameSite=None"),
            (None, "foo=bar"),
    ),
)
def test_cookie_samesite_attribute(samesite, expected):
    value = dump_cookie("foo", "bar", samesite=samesite, path=None)
    assert value == expected


def test_cookie_samesite_invalid():
    with pytest.raises(ValueError):
        dump_cookie("foo", "bar", samesite="invalid")


def test_cookie_partitioned():
    value = dump_cookie("foo", "bar", partitioned=True, secure=True)
    assert value == "foo=bar; Secure; Path=/; Partitioned"


def test_cookie_partitioned_sets_secure():
    value = dump_cookie("foo", "bar", partitioned=True, secure=False)
    assert value == "foo=bar; Secure; Path=/; Partitioned"
