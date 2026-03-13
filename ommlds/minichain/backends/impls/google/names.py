r"""
https://ai.google.dev/gemini-api/docs/models

FIXME: paginated lol

curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | \
  om j -FR -x 'models[].name' | sort

====

aqa
deep-research-pro-preview-12-2025
gemini-2.0-flash
gemini-2.0-flash-001
gemini-2.0-flash-lite
gemini-2.0-flash-lite-001
gemini-2.5-computer-use-preview-10-2025
gemini-2.5-flash
gemini-2.5-flash-image
gemini-2.5-flash-lite
gemini-2.5-flash-lite-preview-09-2025
gemini-2.5-flash-native-audio-latest
gemini-2.5-flash-native-audio-preview-09-2025
gemini-2.5-flash-native-audio-preview-12-2025
gemini-2.5-flash-preview-tts
gemini-2.5-pro
gemini-2.5-pro-preview-tts
gemini-3-flash-preview
gemini-3-pro-image-preview
gemini-3-pro-preview
gemini-3.1-flash-image-preview
gemini-3.1-flash-lite-preview
gemini-3.1-pro-preview
gemini-3.1-pro-preview-customtools
gemini-embedding-001
gemini-embedding-2-preview
gemini-flash-latest
gemini-flash-lite-latest
gemini-pro-latest
gemini-robotics-er-1.5-preview
gemma-3-12b-it
gemma-3-1b-it
gemma-3-27b-it
gemma-3-4b-it
gemma-3n-e2b-it
gemma-3n-e4b-it
imagen-4.0-fast-generate-001
imagen-4.0-generate-001
imagen-4.0-ultra-generate-001
nano-banana-pro-preview
veo-2.0-generate-001
veo-3.0-fast-generate-001
veo-3.0-generate-001
veo-3.1-fast-generate-preview
veo-3.1-generate-preview

"""  # noqa
from ....models.names import ModelNameCollection
from ...strings.manifests import BackendStringsManifest


##


MODEL_NAMES = ModelNameCollection(
    default='gemini',
    aliases={
        'gemini-3-pro-preview': None,
        'gemini-3-pro': 'gemini-3-pro-preview',

        'gemini-3-flash-preview': None,
        'gemini-3-flash': 'gemini-3-flash-preview',

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
_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'google',
    model_names=MODEL_NAMES,
)
