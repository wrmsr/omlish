import typing as ta

from omcore import lang

from ..types.models import Model
from ..types.models import ModelKey
from ..types.options import Options
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
        http=Model.Http(
            base_url='https://api.openai.com/v1',
        ),
    ),

    # groq

    Model(
        key=ModelKey(
            provider='groq',
            id='openai/gpt-oss-120b',
        ),
        name='GPT OSS 120B',
        backend='openai-completions',
        http=Model.Http(
            base_url='https://api.groq.com/openai/v1',
            extra_headers={
                'User-Agent': 'python-httpx/0.28.1',  # required or it 403's lol
            },
        ),
    ),

    # anthropic

    Model(
        key=ModelKey(
            provider='anthropic',
            id='claude-sonnet-5',
        ),
        name='Claude Sonnet 5',
        backend='anthropic-messages',
        http=Model.Http(
            base_url='https://api.anthropic.com/v1',
            extra_headers={
                'anthropic-version': '2023-06-01',
            },
        ),
        default_options=Options(
            max_tokens=4096,
        ),
    ),

]


##


@lang.cached_function(lock=True)
def default_model_catalog() -> ModelCatalog:
    return ModelCatalog(DEFAULT_MODELS)
