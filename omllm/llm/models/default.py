import typing as ta

from omcore import lang

from ..types.models import Model
from ..types.models import ModelKey
from .catalog import ModelCatalog


##


DEFAULT_MODELS: ta.Final[ta.Sequence[Model]] = [

    # openai

    Model(
        key=ModelKey(
            provider='openai',
            id='gpt-5.4-mini',
        ),
        name='GPT 5.4 Mini',
        backend='openai-completions',
        base_url='https://api.openai.com/v1',
    ),

    # groq

    Model(
        key=ModelKey(
            provider='groq',
            id='openai/gpt-oss-120b',
        ),
        name='GPT OSS 120B',
        backend='openai-completions',
        base_url='https://api.groq.com/openai/v1',
    ),

]


##


@lang.cached_function(lock=True)
def default_model_catalog() -> ModelCatalog:
    return ModelCatalog(DEFAULT_MODELS)
