import os
import re
import shlex
import sys


##


_DEFAULT_TIMEBOMB_NAME = '-'.join([*__name__.split('.'), 'timebomb'])


def timebomb_payload(delay_s: float, name: str = _DEFAULT_TIMEBOMB_NAME) -> str:
    return (
        '('
        f'echo {shlex.quote(name)} && '
        f'sleep {delay_s:g} && '
        'sh -c \'killall5 -9 -o $PPID -o $$ ; kill 1\''
        ') &'
    )


##


DOCKER_FOR_MAC_HOSTNAME = 'docker.for.mac.localhost'


_LIKELY_IN_DOCKER_PATTERN = re.compile(r'^overlay / .*/docker/')


def is_likely_in_docker() -> bool:
    if getattr(sys, 'platform') != 'linux':
        return False
    with open('/proc/mounts') as f:
        ls = f.readlines()
    return any(_LIKELY_IN_DOCKER_PATTERN.match(l) for l in ls)


##


# Set by pyproject, docker-dev script
DOCKER_HOST_PLATFORM_KEY = 'DOCKER_HOST_PLATFORM'


def get_docker_host_platform() -> str | None:
    return os.environ.get(DOCKER_HOST_PLATFORM_KEY)
