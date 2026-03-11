import abc
import typing as ta

from textual.app import ComposeResult

from omlish import check


##


class ComposeOnce:
    _has_composed = False

    @ta.final
    def compose(self) -> ComposeResult:
        check.state(not self._has_composed)
        self._has_composed = True

        return self._compose_once()

    @abc.abstractmethod
    def _compose_once(self) -> ComposeResult:
        raise NotImplementedError
