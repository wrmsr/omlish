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


##


class InitAddClass:
    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*args, **kwargs)

        self._init_add_class()

    init_add_class: str | ta.Sequence[str] | None = None

    def _init_add_class(self) -> None:
        for b in type(self).__mro__[-2::-1]:
            self._init_add_class_for_mro(b)

    def _init_add_class_for_mro(self, cls: type) -> None:
        try:
            iac = cls.__dict__['init_add_class']
        except KeyError:
            return

        if not iac:
            return

        if isinstance(iac, str):
            iac = [iac]

        self.add_class(*iac)  # type: ignore[attr-defined]
