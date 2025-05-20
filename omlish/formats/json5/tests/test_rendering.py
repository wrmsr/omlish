import pytest

from .... import lang
from ...json.consts import PRETTY_KWARGS
from ..codec import loads
from ..rendering import Json5Renderer


KITCHEN_SINK_STR = lang.get_relative_resources(globals=globals())['kitchen_sink.json5'].read_text()


@pytest.mark.parametrize('multiline_strings', [False, True])
@pytest.mark.parametrize('ensure_ascii', [False, True])
@pytest.mark.parametrize('pretty', [False, True])
def test_rendering(
    multiline_strings,
    ensure_ascii,
    pretty,
):
    obj = loads(KITCHEN_SINK_STR)
    kw = dict(
        multiline_strings=multiline_strings,
        ensure_ascii=ensure_ascii,
        **(PRETTY_KWARGS if pretty else {}),
    )
    s = Json5Renderer.render_str(obj, **kw)
    obj2 = loads(s)
    assert obj == obj2
