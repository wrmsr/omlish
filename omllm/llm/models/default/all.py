import typing as ta

from omcore import lang

from ...types.models import Model
from ..catalog import ModelCatalog


with lang.auto_proxy_import(globals()):
    from . import anthropic
    from . import cerebras
    from . import groq
    from . import openai


##


@lang.cached_function(lock=True)
def default_models() -> ta.Sequence[Model]:
    return [
        *anthropic.MODELS,
        *cerebras.MODELS,
        *groq.MODELS,
        *openai.MODELS,
    ]


@lang.cached_function(lock=True)
def default_model_catalog() -> ModelCatalog:
    return ModelCatalog(default_models())
