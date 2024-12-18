# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.check import check

from .types import DeployPathPlaceholder
from .types import DeployPathPlaceholderMap


class DeployPathPlaceholders:
    def __new__(cls, *args, **kwargs):
        raise TypeError

    DT = DeployPathPlaceholder('dt')

    DEPLOY_KEY = DeployPathPlaceholder('deploy-key')  # DeployKey

    APP = DeployPathPlaceholder('app')  # DeployApp
    APP_KEY = DeployPathPlaceholder('app-key')  # DeployKey
    APP_REV = DeployPathPlaceholder('app-rev')  # DeployRev

    CONF = DeployPathPlaceholder('conf')  # DeployConf

    @classmethod
    def map_of(cls, **kwargs: str) -> DeployPathPlaceholderMap:
        return {
            DEPLOY_PATH_PLACEHOLDER_KWARGS_MAP[k]: v
            for k, v in kwargs.items()
        }


def _check_deploy_path_placeholder_value(a: str, s: str) -> str:
    check.equal(a.upper(), a)
    check.equal(s.lower(), s)
    check.not_in('_', s)
    check.equal(a.lower().replace('_', '-'), s)
    return s


DEPLOY_PATH_PLACEHOLDERS: ta.FrozenSet[DeployPathPlaceholder] = ta.cast(
    ta.FrozenSet[DeployPathPlaceholder],
    frozenset(
        _check_deploy_path_placeholder_value(a, v)
        for a, v in DeployPathPlaceholders.__dict__.items()
        if isinstance(v, str)
        and not a.startswith('_')
    ),
)


DEPLOY_PATH_PLACEHOLDER_KWARGS_MAP: ta.Mapping[str, DeployPathPlaceholder] = {
    p.replace('-', '_'): p
    for p in DEPLOY_PATH_PLACEHOLDERS
}
