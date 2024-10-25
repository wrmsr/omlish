import json

import pytest

from .... import lang
from ..render import JsonRenderer
from ..render import StreamJsonRenderer
from ..stream import yield_parser_events
from .helpers import TEST_DOCS


DOC = lang.get_relative_resources('.', globals=globals())['stress.json'].read_text()


@pytest.mark.parametrize('indent', [None, 2])
@pytest.mark.parametrize('separators', [None, (',', ':'), (', ', ': ')])
@pytest.mark.parametrize('sort_keys', [False, True])
def test_render(
        indent,
        separators,
        sort_keys,
):
    for s in TEST_DOCS:
        obj = json.loads(s)
        kw = dict(
            indent=indent,
            separators=separators,
            sort_keys=sort_keys,
        )
        r = json.dumps(obj, **kw)

        l = JsonRenderer.render_str(obj, **kw)
        assert l == r

        l = StreamJsonRenderer.render_str(yield_parser_events(obj), **kw)
        assert l == r
