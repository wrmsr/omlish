r"""
https://platform.openai.com/docs/models/compare

curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | \
  om j -FR -x 'data[].id' | sort

====

gpt-3.5-turbo
gpt-3.5-turbo-0125
gpt-3.5-turbo-1106
gpt-3.5-turbo-16k
gpt-3.5-turbo-instruct
gpt-3.5-turbo-instruct-0914
gpt-4
gpt-4-0613
gpt-4-turbo
gpt-4-turbo-2024-04-09
gpt-4.1
gpt-4.1-2025-04-14
gpt-4.1-mini
gpt-4.1-mini-2025-04-14
gpt-4.1-nano
gpt-4.1-nano-2025-04-14
gpt-4o
gpt-4o-2024-05-13
gpt-4o-2024-08-06
gpt-4o-2024-11-20
gpt-4o-mini
gpt-4o-mini-2024-07-18
gpt-4o-mini-transcribe
gpt-4o-mini-transcribe-2025-03-20
gpt-4o-mini-transcribe-2025-12-15
gpt-5
gpt-5-2025-08-07
gpt-5-chat-latest
gpt-5-codex
gpt-5-mini
gpt-5-mini-2025-08-07
gpt-5-nano
gpt-5-nano-2025-08-07
gpt-5-pro
gpt-5-pro-2025-10-06
gpt-5-search-api
gpt-5-search-api-2025-10-14
gpt-5.1
gpt-5.1-2025-11-13
gpt-5.1-chat-latest
gpt-5.1-codex
gpt-5.1-codex-max
gpt-5.1-codex-mini
gpt-5.2
gpt-5.2-2025-12-11
gpt-5.2-chat-latest
gpt-5.2-codex
gpt-5.2-pro
gpt-5.2-pro-2025-12-11
gpt-5.3-chat-latest
gpt-5.3-codex
gpt-5.4
gpt-5.4-2026-03-05
gpt-5.4-pro
gpt-5.4-pro-2026-03-05
o3
o3-2025-04-16
o3-mini
o3-mini-2025-01-31
o4-mini
o4-mini-2025-04-16
o4-mini-deep-research
o4-mini-deep-research-2025-06-26

"""  # noqa
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

    'gpt-5.1',

    'gpt-5.2',
]


CHAT_MODEL_NAMES = ModelNameCollection(
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

        'gpt': 'gpt-5.2',
        'gpt-mini': 'gpt-5-mini',

        #

        'o3': None,
        'o3-mini': None,

        'o4-mini': None,
        'o4-mini-deep-research': None,
    },
)


# @omlish-manifest
_CHAT_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'openai',
    model_names=CHAT_MODEL_NAMES,
)


##


# @omlish-manifest
_COMPLETION_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'CompletionService',
    ],
    'openai',
)


##


# @omlish-manifest
_EMBEDDING_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'EmbeddingService',
    ],
    'openai',
)
