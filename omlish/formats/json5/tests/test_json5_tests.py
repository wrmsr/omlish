import json
import math
import os.path
import typing as ta

import pytest

from ..errors import Json5Error
from ..parsing import parse


##


TEST_EXTENSIONS = {
    # Valid JSON should remain valid JSON5. These cases have a .json extension and are tested via JSON.parse().
    'json',

    # JSON5's new features should remain valid ES5. These cases have a .json5 extension are tested via eval().
    'json5',

    # Valid ES5 that's explicitly disallowed by JSON5 is also invalid JSON. These cases have a .js extension and are
    # expected to fail.
    'js',

    # Invalid ES5 should remain invalid JSON5. These cases have a .txt extension and are expected to fail.
    'txt',
}


def assert_json_equal(l, r):
    if isinstance(l, list):
        for le, re in zip(l, r, strict=True):
            assert_json_equal(le, re)

    elif isinstance(l, dict):
        for (lk, lv), (rk, rv) in zip(l.items(), r.items(), strict=True):
            assert_json_equal(lk, rk)
            assert_json_equal(lv, rv)

    elif isinstance(l, float) and math.isnan(l):
        assert math.isnan(r)

    else:
        assert l == r


def test_json5_tests():
    json5: ta.Any
    try:
        import json5
    except ImportError:
        json5 = None

    for dp, dns, fns in os.walk(os.path.join(os.path.dirname(__file__), 'json5_tests')):  # noqa
        for fn in fns:
            if '.' not in fn:
                continue

            ext = fn.rpartition('.')[2]
            if ext not in TEST_EXTENSIONS:
                continue

            fp = os.path.join(dp, fn)
            with open(fp) as f:
                src = f.read()

            if ext == 'json':
                j = json.loads(src)

                j5 = parse(src)
                assert_json_equal(j5, j)

                if json5 is not None:
                    j5x = json5.loads(src)
                    assert_json_equal(j5, j5x)

            elif ext == 'json5':
                j5 = parse(src)

                if json5 is not None:
                    try:
                        j5x = json5.loads(src)
                    except Exception:  # noqa
                        pass
                    else:
                        assert_json_equal(j5, j5x)

            elif ext in ('js', 'txt'):
                with pytest.raises(Exception):  # noqa
                    json.loads(src)

                with pytest.raises(Json5Error):
                    parse(src)

                if json5 is not None:
                    with pytest.raises(Exception):  # noqa
                        json5.loads(src)
