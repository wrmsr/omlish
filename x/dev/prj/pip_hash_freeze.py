#!/usr/bin/env python3
"""
Freezes packages from a requirements.txt file and a python environment (usually a virtualenv) into a fully frozen and
hashed set of packages.

    . my-venv/bin/activate
    pip-hash-freeze requirements.txt >frozen-requirements.txt
    pip install -r frozen-requirements.txt

https://www.peterdebelak.com/blog/generating-a-fully-qualified-and-hashed-requirements-file/

The MIT License (MIT)

Copyright (c) 2015-2020 Peter Debelak

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import argparse
import fileinput
import json
from typing import Generator, Iterable
from urllib.request import urlopen

import pkg_resources


class Requirement:
    """Represents a single package requirement."""

    def __init__(self, requirement: pkg_resources.DistInfoDistribution):
        self.name = requirement.project_name
        self.version = requirement.version

    def __str__(self) -> str:
        """A string representatation suitable for printing into a requirements file"""
        return " \\\n    ".join([f"{self.name}=={self.version}", *self.hashes()])

    def __eq__(self, other) -> bool:
        """Equality check used for deduping"""
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        """Make hashable so it can deduped using a set"""
        return hash((self.name, self.version))

    def hashes(self) -> Generator[str, None, None]:
        """
        Fetch sha256 hashes for this version of this package

        Returns them in a format suitable for printing into a requirements file.
        """
        with urlopen(f"https://pypi.org/pypi/{self.name}/{self.version}/json") as f:
            data = json.load(f)
        for release in data["releases"][self.version]:
            sha = release["digests"]["sha256"]
            yield f"--hash=sha256:{sha}"


def parser() -> argparse.ArgumentParser:
    """Create argument parser for help text"""
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "requirements_files",
        nargs="*",
        help="One or more requirements files to freeze, defaults to stdin if no files are provided.",
    )
    return p


def resolve_requirements(
    requirements: Iterable[str],
) -> Generator[Requirement, None, None]:
    """Use pkg_resources to parse and resolve requirements"""
    for requirement in pkg_resources.working_set.resolve(
        pkg_resources.parse_requirements(requirements)
    ):
        yield Requirement(requirement)


def main():
    """Print sorted list of fully-qualified and -hashed requirements from given requirements."""
    parser().parse_args()
    for requirement in sorted(set(resolve_requirements(fileinput.input())), key=lambda req: req.name.lower()):
        print(requirement)


if __name__ == "__main__":
    main()
