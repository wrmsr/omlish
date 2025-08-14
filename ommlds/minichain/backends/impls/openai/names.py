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
