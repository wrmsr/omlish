import typing as ta

from omcore import lang

from ..types.models import Model
from .catalog import ModelCatalog


##


DEFAULT_MODELS: ta.Final[ta.Sequence[Model]] = [

    Model(
        id='gpt-5.4-mini',
        name='gpt-5.4-mini',
        backend='openai-completions',
        provider='openai',
        base_url='https://api.openai.com/v1',
    ),

]


##


@lang.cached_function(lock=True)
def default_model_catalog() -> ModelCatalog:
    return ModelCatalog(DEFAULT_MODELS)
