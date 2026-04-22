r"""
https://docs.anthropic.com/en/docs/about-claude/models#model-comparison-table

curl -s https://api.anthropic.com/v1/models -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" | \
    om j -FR -x 'data[].id' | sort

====

claude-haiku-4-5-20251001
claude-opus-4-6
claude-opus-4-7
claude-sonnet-4-6

"""  # noqa
from omlish import lang

from ....models.names import ModelNameCollection
from ...strings.manifests import BackendStringsManifest


##


MODEL_NAMES = ModelNameCollection(
    default='claude',
    aliases={
        **dict(lang.flatten(
            [
                (mn := f'claude-{tier}-{ver}', None),
                (f'claude-{tier}', mn),
                (tier, mn),
            ]
            for tier, ver in [
                ('opus', '4-7'),
                ('sonnet', '4-6'),
                ('haiku', '4-5'),
            ]
        )),

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
