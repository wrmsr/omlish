import abc
import typing as ta

from .... import lang


##


class Backend(lang.Abstract):
    @abc.abstractmethod
    def dump(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def dumps(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def load(self, fp: ta.Any, **kwargs: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def loads(self, s: str | bytes | bytearray, **kwargs: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def dump_pretty(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def dumps_pretty(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def dump_compact(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def dumps_compact(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        raise NotImplementedError
