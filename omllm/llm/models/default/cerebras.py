import typing as ta

from ...types.models import Model
from ...types.models import ModelKey


##


MODELS: ta.Final[ta.Sequence[Model]] = [

    Model(
        key=ModelKey(
            provider='cerebras',
            id='gpt-oss-120b',
        ),
        name='GPT OSS 120B',
        backend='openai-completions',
        http=Model.Http(
            base_url='https://api.cerebras.ai/v1',
        ),
    ),

]
