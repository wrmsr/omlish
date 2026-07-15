import typing as ta

from ...types.models import Model
from ...types.models import ModelKey


##


MODELS: ta.Final[ta.Sequence[Model]] = [

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

]
