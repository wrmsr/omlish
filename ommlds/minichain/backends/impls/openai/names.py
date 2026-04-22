r"""
https://developers.openai.com/api/docs/models/all
https://platform.openai.com/docs/models/compare

curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | \
  om j -FR -x 'data[].id' | sort

====

gpt-4.1
gpt-4.1-2025-04-14

gpt-4.1-mini
gpt-4.1-mini-2025-04-14

gpt-4.1-nano
gpt-4.1-nano-2025-04-14

gpt-5.4
gpt-5.4-2026-03-05

gpt-5.4-mini
gpt-5.4-mini-2026-03-17

gpt-5.4-nano
gpt-5.4-nano-2026-03-17

gpt-5.4-pro
gpt-5.4-pro-2026-03-05

"""  # noqa
from ....models.names import ModelNameCollection
from ...strings.manifests import BackendStringsManifest


##


_GPT_MODEL_NAMES = [
    *[
        f'gpt-{pfx}{sfx}'
        for pfx in ['4', '4.1']
        for sfx in ['', '-mini', '-nano']
    ],

    *[
        f'gpt-{pfx}{sfx}'
        for pfx in ['5', '5.4']
        for sfx in ['', '-mini', '-nano', '-pro']
    ],
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

        **{
            f'gpt{sfx}': f'gpt-5{sfx}'
            for sfx in ['', '-mini', '-nano', '-pro']
        },
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
