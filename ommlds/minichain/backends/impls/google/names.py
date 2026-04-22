r"""
https://ai.google.dev/gemini-api/docs/models

FIXME: paginated lol

curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | \
  om j -FR -x 'models[].name' | sort

====

gemini-2.5-flash
gemini-2.5-flash-lite

gemini-2.5-pro

gemini-3-flash-preview
gemini-3-pro-preview

gemini-3.1-flash-lite-preview

gemini-3.1-pro-preview
gemini-3.1-pro-preview-customtools

gemini-flash-latest
gemini-flash-lite-latest
gemini-pro-latest

"""  # noqa
from ....models.names import ModelNameCollection
from ...strings.manifests import BackendStringsManifest


##


MODEL_NAMES = ModelNameCollection(
    default='gemini',
    aliases={
        (pro := 'gemini-3.1-pro-preview'): None,
        'gemini-3.1-pro': pro,
        'gemini-3-pro': pro,
        'gemini-pro': pro,

        (flash := 'gemini-3-flash-preview'): None,
        'gemini-3-flash': flash,
        'gemini-flash': flash,

        (flash_lite := 'gemini-3.1-flash-lite-preview'): None,
        'gemini-3.1-flash-lite': flash_lite,
        'gemini-3-flash-lite': flash_lite,
        'gemini-flash-lite': flash_lite,

        (flash2 := 'gemini-2.5-flash'): None,
        'gemini-2-flash': flash2,

        (flash_lite2 := 'gemini-2.5-flash-lite'): None,
        'gemini-2-flash-lite': flash_lite2,

        'gemini': 'gemini-flash',
    },
)


# @omlish-manifest
_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'google',
    model_names=MODEL_NAMES,
)
