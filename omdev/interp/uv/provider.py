# ruff: noqa: UP006 UP007 UP045
"""
uv run pip
uv run --python 3.11.6 pip
uv venv --python 3.11.6 --seed barf
python3 -m venv barf && barf/bin/pip install uv && barf/bin/uv venv --python 3.11.6 --seed barf2
"""
import typing as ta

from omlish.logs.protocols import LoggerLike

from ..inspect import InterpInspector
from ..providers.base import InterpProvider
from ..types import Interp
from ..types import InterpSpecifier
from ..types import InterpVersion
from .uv import Uv


##


class UvInterpProvider(InterpProvider):
    def __init__(
            self,
            *,
            pyenv: Uv,
            inspector: InterpInspector,
            log: ta.Optional[LoggerLike] = None,
    ) -> None:
        super().__init__()

        self._pyenv = pyenv
        self._inspector = inspector
        self._log = log

    async def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return []

    async def get_installed_version(self, version: InterpVersion) -> Interp:
        raise NotImplementedError
