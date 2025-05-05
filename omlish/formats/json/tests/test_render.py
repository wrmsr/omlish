import json

import pytest

from .... import lang
from ..rendering import JsonRenderer
from ..stream.parsing import yield_parser_events
from ..stream.rendering import StreamJsonRenderer
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
    for i, s in enumerate(TEST_DOCS):  # noqa
        obj = json.loads(s)
        kw = dict(
            indent=indent,
            separators=separators,
            sort_keys=sort_keys,
        )
        r = json.dumps(obj, **kw)

        l = JsonRenderer.render_str(obj, **kw)
        assert l == r

        if not sort_keys:  # FIXME
            l = StreamJsonRenderer.render_str(yield_parser_events(obj), **kw)
            assert l == r
