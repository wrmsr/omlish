from ....standard import ModelNameCollection
from ...strings.packs import ModelNameBackendStringPack


##


MODEL_NAMES = ModelNameCollection(
    default='claude',
    aliases={
        'claude-opus-4-1': 'claude-opus-4-1-20250805',
        'claude-opus': 'claude-opus-4-1',

        'claude-sonnet-4': 'claude-sonnet-4-20250514',
        'claude-sonnet': 'claude-sonnet-4',

        'claude-haiku-3-5-latest': 'claude-3-5-haiku-latest',
        'claude-haiku-3-5': 'claude-haiku-3-5-latest',
        'claude-haiku': 'claude-haiku-3-5',

        'claude': 'claude-haiku',
    },
)


# @omlish-manifest
_MODEL_NAMES_PACK = ModelNameBackendStringPack(
    ['ChatChoicesService'],
    'anthropic',
    MODEL_NAMES,
)
