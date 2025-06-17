# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import os
import re
import sys
import typing as ta


##


# Set by pyproject, docker-dev script
DOCKER_HOST_PLATFORM_KEY = 'DOCKER_HOST_PLATFORM'


def get_docker_host_platform() -> ta.Optional[str]:
    return os.environ.get(DOCKER_HOST_PLATFORM_KEY)


##


_LIKELY_IN_DOCKER_PATTERN = re.compile(r'^overlay / .*/(docker|desktop-containerd)/')


def is_likely_in_docker() -> bool:
    if getattr(sys, 'platform') != 'linux':
        return False
    with open('/proc/mounts') as f:
        ls = f.readlines()
    return any(_LIKELY_IN_DOCKER_PATTERN.match(l) for l in ls)
