import typing as ta

from omlish import lang
from omlish import typedvalues as tv

from .attributes import ContextWindow
from .attributes import InputTokenCost
from .attributes import MaxOutputTokens
from .attributes import ModelAttribute
from .attributes import ModelAttributes
from .attributes import ModelAttributesProvider
from .attributes import OutputTokenCost
from .attributes import SupportsReasoning
from .attributes import SupportsStructuredOutput
from .attributes import SupportsTools


with lang.auto_proxy_import(globals()):
    from ... import modeldb


##


class StaticModelAttributesProvider(ModelAttributesProvider):
    """Caller-supplied attributes, keyed by model name - the home for local/weird models with no public metadata."""

    def __init__(self, by_model: ta.Mapping[str, ta.Sequence[ModelAttribute]]) -> None:
        super().__init__()

        self._by_model = {k: tuple(v) for k, v in by_model.items()}

    async def provide_model_attributes(self, model: str) -> ModelAttributes:
        return tv.collect(*self._by_model.get(model, ()))


##


class CompositeModelAttributesProvider(ModelAttributesProvider):
    """Merges a chain of providers; earlier providers win per attribute type (so static/local overrides the cache)."""

    def __init__(self, providers: ta.Sequence[ModelAttributesProvider]) -> None:
        super().__init__()

        self._providers = list(providers)

    async def provide_model_attributes(self, model: str) -> ModelAttributes:
        by_ty: dict[type, ModelAttribute] = {}
        for p in self._providers:
            for a in await p.provide_model_attributes(model):
                by_ty.setdefault(type(a), a)
        return tv.collect(*by_ty.values())


##


@lang.cached_function
def _modeldb_index() -> ta.Mapping[str, modeldb.Model]:
    # Flatten the provider-nested models.dev cache to a model-id -> model-dict index (first occurrence wins).
    idx: dict[str, modeldb.Model] = {}
    for provider in modeldb.load_providers().values():
        for model_id, model in (provider.models or {}).items():
            idx.setdefault(model_id, model)
    return idx


def _extract_modeldb_attributes(model: modeldb.Model) -> list[ModelAttribute]:
    out: list[ModelAttribute] = []

    if (limit := model.limit) is not None:
        out.append(ContextWindow(int(limit.context)))
        out.append(MaxOutputTokens(int(limit.output)))

    if (cost := model.cost) is not None:
        out.append(InputTokenCost(cost.input))
        out.append(OutputTokenCost(cost.output))

    out.append(SupportsTools(model.tool_call))
    out.append(SupportsReasoning(model.reasoning))
    if (so := model.structured_output) is not None:
        out.append(SupportsStructuredOutput(so))

    return out


class ModeldbModelAttributesProvider(ModelAttributesProvider):
    """Reads the bundled models.dev cache (`ommlds.modeldb`); unknown models resolve to no attributes."""

    async def provide_model_attributes(self, model: str) -> ModelAttributes:
        m = _modeldb_index().get(model)
        if m is None:
            return tv.empty()
        return tv.collect(*_extract_modeldb_attributes(m))
