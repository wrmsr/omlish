import abc
import collections.abc
import enum
import functools
import typing as ta

from .. import check
from .. import lang


T = ta.TypeVar('T')


##


ParamKey: ta.TypeAlias = str | int

SequencePreparedParams: ta.TypeAlias = ta.Sequence[ParamKey]
MappingPreparedParams: ta.TypeAlias = ta.Mapping[str, ParamKey]

PreparedParams: ta.TypeAlias = SequencePreparedParams | MappingPreparedParams


class ParamsPreparer(lang.Abstract):
    @abc.abstractmethod
    def add(self, k: ParamKey) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def prepare(self) -> PreparedParams:
        raise NotImplementedError


class SequenceParamsPreparer(ParamsPreparer, lang.Abstract):
    @abc.abstractmethod
    def prepare(self) -> SequencePreparedParams:
        raise NotImplementedError


class MappingParamsPreparer(ParamsPreparer, lang.Abstract):
    @abc.abstractmethod
    def prepare(self) -> MappingPreparedParams:
        raise NotImplementedError


##


class LinearParamsPreparer(SequenceParamsPreparer):
    def __init__(self, placeholder: str) -> None:
        super().__init__()

        self._placeholder = placeholder
        self._args: list[ParamKey] = []

    def add(self, k: ParamKey) -> str:
        self._args.append(k)
        return self._placeholder

    def prepare(self) -> SequencePreparedParams:
        return self._args


#


class NumericParamsPreparer(SequenceParamsPreparer):
    def __init__(self) -> None:
        super().__init__()

        self._args: list[ParamKey] = []
        self._str_by_key: dict[ParamKey, str] = {}
        self._pos_by_name: dict[str, int] = {}
        self._pos_by_id: dict[int, int] = {}

    def add(self, k: ParamKey) -> str:
        try:
            return self._str_by_key[k]
        except KeyError:
            pass

        pos = len(self._args)
        if isinstance(k, str):
            check.not_in(k, self._pos_by_name)
            self._pos_by_name[k] = pos
        elif isinstance(k, int):
            check.not_in(k, self._pos_by_id)
            self._pos_by_id[k] = pos
        else:
            raise TypeError(f'Invalid key type: {type(k)}')

        self._args.append(k)
        ret = self._str_by_key[k] = f':{pos + 1}'
        return ret

    def prepare(self) -> SequencePreparedParams:
        return self._args


#


class NamedParamsPreparer(MappingParamsPreparer):
    def __init__(
            self,
            render: ta.Callable[[str], str],
            *,
            anon: ta.Callable[[int], str] | None = None,
    ) -> None:
        super().__init__()

        self._render = render
        self._anon = anon if anon is not None else self.underscore_anon
        self._kwargs: dict[str, ParamKey] = {}
        self._str_by_key: dict[ParamKey, str] = {}
        self._kwargs_by_name: dict[str, str] = {}
        self._kwargs_by_id: dict[int, str] = {}

    @staticmethod
    def render_named(kwarg: str) -> str:
        return f':{kwarg}'

    @staticmethod
    def render_pyformat(kwarg: str) -> str:
        return f'%({kwarg})s'

    @staticmethod
    def underscore_anon(n: int) -> str:
        return f'_{n}'

    def add(self, k: ParamKey) -> str:
        try:
            return self._str_by_key[k]
        except KeyError:
            pass

        kwarg: str
        if isinstance(k, str):
            check.not_in(k, self._kwargs_by_name)
            kwarg = k  # TODO: collisions
            self._kwargs_by_name[k] = kwarg
        elif isinstance(k, int):
            check.not_in(k, self._kwargs_by_id)
            kwarg = self._anon(len(self._kwargs_by_id))  # TODO: collisions
            self._kwargs_by_id[k] = kwarg
        else:
            raise TypeError(f'Invalid key type: {type(k)}')

        self._kwargs[kwarg] = k
        ret = self._str_by_key[k] = self._render(kwarg)
        return ret

    def prepare(self) -> MappingPreparedParams:
        return self._kwargs


##


class ParamStyle(enum.Enum):
    QMARK = 'qmark'  # Question mark style, e.g. ...WHERE name=?
    FORMAT = 'format'  # ANSI C printf format codes, e.g. ...WHERE name=%s

    NUMERIC = 'numeric'  # Numeric, positional style, e.g. ...WHERE name=:1

    NAMED = 'named'  # Named style, e.g. ...WHERE name=:name
    PYFORMAT = 'pyformat'  # Python extended format codes, e.g. ...WHERE name=%(name)s


_PARAMS_PREPARER_FACTORIES_BY_STYLE: ta.Mapping[ParamStyle, ta.Callable[[], ParamsPreparer]] = {
    ParamStyle.QMARK: functools.partial(LinearParamsPreparer, '?'),
    ParamStyle.FORMAT: functools.partial(LinearParamsPreparer, '%s'),

    ParamStyle.NUMERIC: NumericParamsPreparer,

    ParamStyle.NAMED: functools.partial(NamedParamsPreparer, NamedParamsPreparer.render_named),
    ParamStyle.PYFORMAT: functools.partial(NamedParamsPreparer, NamedParamsPreparer.render_pyformat),
}


def make_params_preparer(style: ParamStyle) -> ParamsPreparer:
    try:
        fac = _PARAMS_PREPARER_FACTORIES_BY_STYLE[style]
    except KeyError:
        raise ValueError(style) from None
    else:
        return fac()


##


@ta.overload
def substitute_prepared_params(
        params: SequencePreparedParams,
        values: ta.Mapping[ParamKey, T],
) -> ta.Sequence[T]:
    ...


@ta.overload
def substitute_prepared_params(
        params: MappingPreparedParams,
        values: ta.Mapping[ParamKey, T],
) -> ta.Mapping[str, T]:
    ...


def substitute_prepared_params(params, values):
    if isinstance(params, collections.abc.Mapping):
        return {k: values[v] for k, v in params.items()}

    elif isinstance(params, collections.abc.Sequence):
        return [values[a] for a in params]

    else:
        raise TypeError(params)
