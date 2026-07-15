import typing as ta

from ...types.models import Model
from ...types.models import ModelKey


##


MODELS: ta.Final[ta.Sequence[Model]] = [

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

]
