#!/usr/bin/env python3
# ruff: noqa: UP006 UP007
# @omlish-amalg ./amalg_resources_test.py
from omlish.lite.resources import read_package_resource_binary
from omlish.lite.resources import read_package_resource_text


ATOM_SQL = read_package_resource_text(__package__, 'atom.sql')


ATOM_SQL_BYTES = read_package_resource_binary(__package__, 'atom.sql')


def _main() -> None:
    print(ATOM_SQL)


if __name__ == '__main__':
    _main()
