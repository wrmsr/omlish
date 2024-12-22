# ruff: noqa: UP006 UP007
"""
uv run pip
uv run --python 3.11.6 pip
uv venv --python 3.11.6 --seed barf
python3 -m venv barf && barf/bin/pip install uv && barf/bin/uv venv --python 3.11.6 --seed barf2
"""
import typing as ta

from ..providers.base import InterpProvider
from ..types import Interp
from ..types import InterpSpecifier
from ..types import InterpVersion


class UvInterpProvider(InterpProvider):
    def get_installed_versions(self, spec: InterpSpecifier) -> ta.Awaitable[ta.Sequence[InterpVersion]]:
        raise NotImplementedError

    def get_installed_version(self, version: InterpVersion) -> ta.Awaitable[Interp]:
        raise NotImplementedError
