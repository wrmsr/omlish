# encoding: utf8

from __future__ import annotations

from pyinfra.api import FactBase

from .util.packaging import parse_packages

CARGO_REGEX = r"^([a-zA-Z0-9\-]+)\sv([0-9\.]+)"


class CargoPackages(FactBase):
    """
    Returns a dict of installed cargo packages globally:

    .. code:: python

        {
            "package_name": ["version"],
        }
    """

    default = dict

    def command(self) -> str:
        return "cargo install --list"

    def requires_command(self) -> str:
        return "cargo"

    def process(self, output):
        return parse_packages(CARGO_REGEX, output)
