import pytest

from omlish import marshal as msh

from ..attributes import ContextWindow
from ..attributes import MaxOutputTokens
from ..attributes import ModelAttribute
from ..attributes import SupportsTools
from ..providers import CompositeModelAttributesProvider
from ..providers import ModeldbModelAttributesProvider
from ..providers import StaticModelAttributesProvider


@pytest.mark.asyncs('asyncio')
async def test_modeldb_known_model():
    attrs = await ModeldbModelAttributesProvider().provide_model_attributes('gpt-4o')

    assert attrs.get(ContextWindow) == ContextWindow(128000)
    assert attrs.get(MaxOutputTokens) is not None
    assert attrs.get(SupportsTools) == SupportsTools(True)


@pytest.mark.asyncs('asyncio')
async def test_modeldb_unknown_model_is_empty():
    attrs = await ModeldbModelAttributesProvider().provide_model_attributes('not-a-real-model-xyz')
    assert list(attrs) == []


@pytest.mark.asyncs('asyncio')
async def test_static_overrides_cache():
    static = StaticModelAttributesProvider({'gpt-4o': [ContextWindow(999)]})
    comp = CompositeModelAttributesProvider([static, ModeldbModelAttributesProvider()])

    attrs = await comp.provide_model_attributes('gpt-4o')

    # Earlier provider wins per attribute type...
    assert attrs.get(ContextWindow) == ContextWindow(999)
    # ...but other attributes still come through from the cache.
    assert attrs.get(SupportsTools) == SupportsTools(True)


@pytest.mark.asyncs('asyncio')
async def test_local_model_carries_only_what_is_known():
    static = StaticModelAttributesProvider({'my-tinygrad-thing': [ContextWindow(4096)]})
    comp = CompositeModelAttributesProvider([static, ModeldbModelAttributesProvider()])

    attrs = await comp.provide_model_attributes('my-tinygrad-thing')
    assert attrs.get(ContextWindow) == ContextWindow(4096)
    assert attrs.get(SupportsTools) is None  # unknown -> absent, not None-filled


def test_marshal_round_trip():
    cw = ContextWindow(200000)
    m = msh.marshal(cw, ModelAttribute)
    assert m == {'context_window': 200000}
    assert msh.unmarshal(m, ModelAttribute) == cw
