import typing as ta

from ...types.compat import OpenaiCompat
from ...types.models import Model
from ...types.models import ModelKey
from ...types.options import Options


##


MODELS: ta.Final[ta.Sequence[Model]] = [

    Model(
        key=ModelKey(
            provider='anthropic',
            id='claude-sonnet-5',
        ),
        name='Claude Sonnet 5',
        backend='anthropic-messages',
        compat=OpenaiCompat(
            max_tokens_field='max_tokens',
        ),
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
