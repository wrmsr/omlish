# ruff: noqa: UP006 UP007
"""
sudo rm -rf \
    /usr/local/.ghcup \
    /opt/hostedtoolcache \

/usr/local/.ghcup       6.4G, 3391250 files
/opt/hostedtoolcache    8.0G, 14843980 files
/usr/local/lib/android  6.4G, 17251667 files
"""
from .env import register_github_env_var


GITHUB_ACTIONS_ENV_VAR = register_github_env_var('GITHUB_ACTIONS')


def is_in_github_actions() -> bool:
    return GITHUB_ACTIONS_ENV_VAR() is not None
