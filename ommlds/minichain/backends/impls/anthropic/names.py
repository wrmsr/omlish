"""
https://docs.anthropic.com/en/docs/about-claude/models#model-comparison-table

curl -s https://api.anthropic.com/v1/models -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" | \
  om j -FR -x 'data[].id' | sort
"""
from ....models.names import ModelNameCollection
from ...strings.manifests import BackendStringsManifest


##


MODEL_NAMES = ModelNameCollection(
    default='claude',
    aliases={
        'claude-opus-4-1-20250805': None,
        'claude-opus-4-1': 'claude-opus-4-1-20250805',
        'claude-opus': 'claude-opus-4-1',

        'claude-sonnet-4-5-20250929': None,
        'claude-sonnet-4-5': 'claude-sonnet-4-5-20250929',
        'claude-sonnet': 'claude-sonnet-4-5',

        'claude-haiku-4-5-20251001': None,
        'claude-haiku-4-5': 'claude-haiku-4-5-20251001',
        'claude-haiku': 'claude-haiku-4-5',

        'claude': 'claude-haiku',
    },
)


# @omlish-manifest
_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'anthropic',
    model_names=MODEL_NAMES,
)
