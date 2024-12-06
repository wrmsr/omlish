import re
import sys


DOCKER_FOR_MAC_HOSTNAME = 'docker.for.mac.localhost'


_LIKELY_IN_DOCKER_PATTERN = re.compile(r'^overlay / .*/(docker|desktop-containerd)/')


def is_likely_in_docker() -> bool:
    if getattr(sys, 'platform') != 'linux':
        return False
    with open('/proc/mounts') as f:
        ls = f.readlines()
    return any(_LIKELY_IN_DOCKER_PATTERN.match(l) for l in ls)
