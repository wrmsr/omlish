"""
https://ai.google.dev/gemini-api/docs/models

FIXME: paginated lol

curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | \
  om j -FR -x 'models[].name' | sort
"""
from ....models.names import ModelNameCollection
from ...strings.packs import ModelNameBackendStringPack


##


MODEL_NAMES = ModelNameCollection(
    default='gemini',
    aliases={
        'gemini-2.5-pro': None,
        'gemini-2.5-flash': None,
        'gemini-2.5-flash-lite': None,

        'gemini-pro': 'gemini-2.5-pro',
        'gemini-flash': 'gemini-2.5-flash',
        'gemini-flash-lite': 'gemini-2.5-flash-lite',

        'gemini': 'gemini-flash',
    },
)


# @omlish-manifest
_MODEL_NAMES_PACK = ModelNameBackendStringPack(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'google',
    MODEL_NAMES,
)
