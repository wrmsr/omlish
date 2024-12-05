from __future__ import annotations

from pyinfra.api import FactBase

from .util.packaging import parse_packages

CHOCO_REGEX = r"^([a-zA-Z0-9\.\-\+\_]+)\s([0-9\.]+)$"


class ChocoPackages(FactBase):
    """
    Returns a dict of installed choco (Chocolatey) packages:

    .. code:: python

        {
            "package_name": ["version"],
        }
    """

    def command(self) -> str:
        return "choco list"

    shell_executable = "ps"

    default = dict

    def process(self, output):
        return parse_packages(CHOCO_REGEX, output)


class ChocoVersion(FactBase):
    """
    Returns the choco (Chocolatey) version.
    """

    def command(self) -> str:
        return "choco --version"

    def process(self, output):
        return "".join(output).replace("\n", "")
