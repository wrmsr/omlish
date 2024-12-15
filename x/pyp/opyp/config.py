import ast
import collections
import itertools
import os
import sys
import typing as ta

from .errors import PypError
from .names import NameFinder
from .names import is_magic_var


def get_config_contents() -> str:
    """Returns the empty string if no config file is specified."""

    config_file = os.environ.get('PYP_CONFIG_PATH')
    if config_file is None:
        return ''
    try:
        with open(config_file) as f:
            return f.read()
    except FileNotFoundError:
        print(f'warning: Config file not found at PYP_CONFIG_PATH={config_file}', file=sys.stderr)
        return ''


class PypConfig:
    """
    PypConfig is responsible for handling user configuration.

    We allow users to configure pyp with a config file that is very Python-like. Rather than executing the config file
    as Python unconditionally, we treat it as a source of definitions. We keep track of what each top-level stmt in the
    AST of the config file defines, and if we need that definition in our program, use it. A wrinkle here is that
    definitions in the config file may depend on other definitions within the config file; this is handled by
    build_missing_config. Another wrinkle is wildcard imports; these are kept track of and added to the list of special
    cased wildcard imports in build_missing_imports.
    """

    def __init__(self) -> None:
        config_contents = get_config_contents()
        try:
            config_ast = ast.parse(config_contents)
        except SyntaxError as e:
            error = f': {e.text!r}' if e.text else ''
            raise PypError(f'Config has invalid syntax{error}') from e

        # List of config parts
        self.parts: list[ast.stmt] = config_ast.body

        # Maps from a name to index of config part that defines it
        self.name_to_def: dict[str, int] = {}
        self.def_to_names: dict[int, list[str]] = collections.defaultdict(list)

        # Maps from index of config part to undefined names it needs
        self.requires: dict[int, set[str]] = collections.defaultdict(set)

        # Modules from which automatic imports work without qualification, ordered by AST encounter
        self.wildcard_imports: list[str] = []

        self.shebang: str = '#!/usr/bin/env python3'
        if config_contents.startswith('#!'):
            self.shebang = '\n'.join(
                itertools.takewhile(lambda line: line.startswith('#'), config_contents.splitlines()),
            )

        top_level: tuple[ta.Any, ...] = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        top_level += (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign, ast.If, ast.Try)
        for index, part in enumerate(self.parts):
            if not isinstance(part, top_level):
                node_type = type(
                    part.value if isinstance(part, ast.Expr) else part,
                ).__name__.lower()
                raise PypError(
                    'Config only supports a subset of Python at top level; '
                    f'unsupported construct ({node_type}) on line {part.lineno}',
                )

            f = NameFinder(part)
            for name in f.top_level_defined:
                if self.name_to_def.get(name, index) != index:
                    raise PypError(f'Config has multiple definitions of {name!r}')

                if is_magic_var(name):
                    raise PypError(f'Config cannot redefine built-in magic variable {name!r}')
                self.name_to_def[name] = index
                self.def_to_names[index].append(name)

            self.requires[index] = f.undefined
            self.wildcard_imports.extend(f.wildcard_imports)
