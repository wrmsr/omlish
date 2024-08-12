import typing as ta

from .pyenv import PyenvInstallOpts
from .pyenv import PyenvInterpProvider


class LinuxInterpProvider(PyenvInterpProvider):

    def _pyenv_pios(self) -> ta.Sequence[PyenvInstallOpts]:
        return [
            *super()._pyenv_pios(),
        ]
