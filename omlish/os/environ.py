# ruff: noqa: UP045
# @omlish-lite
import contextlib
import os
import typing as ta


##


class EnvVar:
    def __init__(self, name: str) -> None:
        super().__init__()

        if not isinstance(name, str):
            raise TypeError(name)
        if not name:
            raise NameError(name)
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._name!r})'

    def __hash__(self) -> int:
        return hash((self.__class__, self._name))

    def __eq__(self, other):
        if not isinstance(other, EnvVar):
            return NotImplemented
        return self._name == other._name

    def __bool__(self) -> bool:
        raise TypeError

    def __str__(self) -> str:
        raise TypeError

    #

    @classmethod
    def _get_mut_environ(
            cls,
            environ: ta.Optional[ta.MutableMapping[str, str]] = None,
    ) -> ta.MutableMapping[str, str]:
        if environ is None:
            return os.environ
        return environ

    @classmethod
    def _get_environ(
            cls,
            environ: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> ta.Mapping[str, str]:
        if environ is None:
            return cls._get_mut_environ()
        return environ

    #

    def is_set(self, environ: ta.Optional[ta.Mapping[str, str]] = None) -> bool:
        return self._name in self._get_environ(environ)

    _NO_DEFAULT: ta.ClassVar[ta.Any] = object()

    @ta.overload
    def get(
            self,
            *,
            environ: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> str:
        ...

    @ta.overload
    def get(
            self,
            default: str,
            /,
            *,
            environ: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> str:
        ...

    @ta.overload
    def get(
            self,
            default: ta.Optional[str],
            /,
            *,
            environ: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> ta.Optional[str]:
        ...

    @ta.overload
    def get(
            self,
            default: ta.Callable[[], str],
            /,
            *,
            environ: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> str:
        ...

    @ta.overload
    def get(
            self,
            default: ta.Callable[[], ta.Optional[str]],
            /,
            *,
            environ: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> ta.Optional[str]:
        ...

    def get(self, default=_NO_DEFAULT, /, *, environ=None):
        environ = self._get_environ(environ)
        try:
            return environ[self._name]
        except KeyError:
            if default is self._NO_DEFAULT:
                raise
            elif callable(default):
                return default()
            else:
                return default

    #

    def set(self, value: ta.Optional[str], *, environ: ta.Optional[ta.MutableMapping[str, str]] = None) -> None:
        environ = self._get_mut_environ(environ)
        if value is not None:
            environ[self._name] = value
        else:
            del environ[self._name]

    @contextlib.contextmanager
    def set_context(
            self,
            value: ta.Optional[str],
            *,
            environ: ta.Optional[ta.MutableMapping[str, str]] = None,
    ) -> ta.Iterator[ta.Optional[str]]:
        prev = self.get(None, environ=environ)
        self.set(value, environ=environ)
        try:
            yield prev
        finally:
            self.set(prev, environ=environ)
