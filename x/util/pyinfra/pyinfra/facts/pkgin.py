from __future__ import annotations

from pyinfra.api import FactBase

from .util.packaging import parse_packages

PKGIN_REGEX = r"^([a-zA-Z\-0-9]+)-([0-9\.]+\-?[a-z0-9]*)\s"


class PkginPackages(FactBase):
    """
    Returns a dict of installed pkgin packages:

    .. code:: python

        {
            "package_name": ["version"],
        }
    """

    def command(self) -> str:
        return "pkgin list"

    def requires_command(self) -> str:
        return "pkgin"

    default = dict

    def process(self, output):
        return parse_packages(PKGIN_REGEX, output)
