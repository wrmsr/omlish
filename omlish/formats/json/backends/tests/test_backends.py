import io
import json

import pytest

from ...consts import COMPACT_KWARGS
from ...consts import PRETTY_KWARGS
from ...tests.helpers import SIMPLE_DOCS
from ..base import Backend
from ..orjson import ORJSON_BACKEND
from ..std import STD_BACKEND
from ..ujson import UJSON_BACKEND


def _test_backend(be: Backend):
    for d in SIMPLE_DOCS:
        obj = json.loads(d)

        #

        be_obj = be.loads(d)
        assert be_obj == obj

        buf = io.StringIO(d)
        be_obj = be.load(buf)
        assert be_obj == obj

        #

        js_pretty = json.dumps(obj, **PRETTY_KWARGS)

        be_pretty = be.dumps_pretty(obj)
        assert be_pretty == js_pretty

        buf = io.StringIO()
        be.dump_pretty(obj, buf)
        be_pretty = buf.getvalue()
        assert be_pretty == js_pretty

        #

        js_compact = json.dumps(obj, **COMPACT_KWARGS)
        be_compact = be.dumps_compact(obj)
        assert be_compact == js_compact

        buf = io.StringIO()
        be.dump_compact(obj, buf)
        be_compact = buf.getvalue()
        assert be_compact == js_compact


def test_std_backend():
    _test_backend(STD_BACKEND)


@pytest.mark.skipif(ORJSON_BACKEND is None, reason='no orjson')
def test_orjson_backend():
    _test_backend(ORJSON_BACKEND)  # type: ignore


@pytest.mark.skipif(UJSON_BACKEND is None, reason='no ujson')
def test_ujson_backend():
    _test_backend(UJSON_BACKEND)  # type: ignore
