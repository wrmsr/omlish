"""
https://platform.openai.com/docs/models/compare

curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | \
  om j -FR -x 'data[].id' | sort

"""
from ....models.names import ModelNameCollection
from ...strings.manifests import BackendStringsManifest


##


_GPT_MODEL_NAMES = [
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-instruct',

    'gpt-4',
    'gpt-4-turbo',

    'gpt-4.1',
    'gpt-4.1-mini',
    'gpt-4.1-nano',

    'gpt-4o',
    'gpt-4o-mini',

    'gpt-5',
    'gpt-5-chat-latest',
    'gpt-5-mini',
    'gpt-5-nano',
]


MODEL_NAMES = ModelNameCollection(
    default='gpt',
    aliases={
        **{
            n: None
            for n in _GPT_MODEL_NAMES
        },

        **{
            'gpt' + n.removeprefix('gpt-'): n
            for n in _GPT_MODEL_NAMES
        },

        'gpt': 'gpt-4o',
        'gpt-mini': 'gpt-4o-mini',

        #

        'o3': None,
        'o3-mini': None,

        'o4-mini': None,
        'o4-mini-deep-research': None,
    },
)


# @omlish-manifest
_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'openai',
    model_names=MODEL_NAMES,
)
