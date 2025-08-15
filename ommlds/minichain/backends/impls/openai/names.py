"""
https://platform.openai.com/docs/models/compare

curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | \
  om j -FR -x 'data[].id' | sort

"""
from ....models.names import ModelNameCollection
from ...strings.packs import ModelNameBackendStringPack


##


MODEL_NAMES = ModelNameCollection(
    default='gpt',
    aliases={
        'gpt-3.5-turbo': None,
        'gpt-3.5-turbo-instruct': None,

        'gpt-4': None,
        'gpt-4-turbo': None,

        'gpt-4.1': None,
        'gpt-4.1-mini': None,
        'gpt-4.1-nano': None,

        'gpt-4o': None,
        'gpt-4o-mini': None,

        'gpt-5': None,
        'gpt-5-chat-latest': None,
        'gpt-5-mini': None,
        'gpt-5-nano': None,

        'o3': None,
        'o3-mini': None,

        'o4-mini': None,
        'o4-mini-deep-research': None,

        'gpt': 'gpt-4o',
        'gpt-mini': 'gpt-4o-mini',
    },
)


# @omlish-manifest
_MODEL_NAMES_PACK = ModelNameBackendStringPack(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'openai',
    MODEL_NAMES,
)
