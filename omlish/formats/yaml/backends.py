# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import typing as ta

from ...lite.abstract import Abstract
from ...lite.cached import cached_nullary
from ...lite.check import check


##


class YamlBackend(Abstract):
    @abc.abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def loads(self, s: str) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def dumps(self, o: ta.Any) -> str:
        raise NotImplementedError

    #

    def set_as_default(self) -> None:
        DEFAULT_YAML_BACKEND.INSTANCE = self


#


class NoYamlBackendAvailableError(Exception):
    pass


class FirstAvailableYamlBackend(YamlBackend):
    def __init__(self, backends: ta.Sequence[YamlBackend]) -> None:
        super().__init__()

        self._backends = backends

    def is_available(self) -> bool:
        return any(b.is_available() for b in self._backends)

    def loads(self, s: str) -> ta.Any:
        for b in self._backends:
            if b.is_available():
                return b.loads(s)
        raise NoYamlBackendAvailableError

    def dumps(self, o: ta.Any) -> str:
        for b in self._backends:
            if b.is_available():
                return b.dumps(o)
        raise NoYamlBackendAvailableError


#


class PyyamlYamlBackend(YamlBackend):
    @cached_nullary
    def _import(self) -> ta.Optional[ta.Any]:
        try:
            import yaml  # noqa
        except ImportError:
            return None
        else:
            return yaml

    def is_available(self) -> bool:
        return self._import() is not None

    def loads(self, s: str) -> ta.Any:
        return check.not_none(self._import()).safe_load(s)

    def dumps(self, o: ta.Any) -> str:
        return check.not_none(self._import()).safe_dump(o)


#


class RelativeImportGoyamlYamlBackend(YamlBackend):
    @cached_nullary
    def _import(self) -> ta.Optional[ta.Any]:
        try:
            mod = __import__('goyaml.backend', globals=globals(), level=1)
        except ImportError:
            return None
        else:
            return mod.backend

    def is_available(self) -> bool:
        return self._import() is not None

    @cached_nullary
    def _backend(self) -> YamlBackend:
        return check.not_none(self._import()).GoyamlYamlBackend()

    def loads(self, s: str) -> ta.Any:
        return self._backend().loads(s)

    def dumps(self, o: ta.Any) -> str:
        return self._backend().dumps(o)


##


@ta.final
class DEFAULT_YAML_BACKEND:  # noqa
    """This isn't just a mutable global because in amalgamated code that's not really possible."""

    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    INSTANCE: ta.ClassVar[YamlBackend] = FirstAvailableYamlBackend([
        PyyamlYamlBackend(),
        RelativeImportGoyamlYamlBackend(),
    ])
