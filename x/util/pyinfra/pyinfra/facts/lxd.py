from __future__ import annotations

import json

from pyinfra.api import FactBase


class LxdContainers(FactBase):
    """
    Returns a list of running LXD containers
    """

    def command(self) -> str:
        return "lxc list --format json --fast"

    def requires_command(self) -> str:
        return "lxc"

    default = list

    def process(self, output):
        output = list(output)
        assert len(output) == 1
        return json.loads(output[0])
