import abc
import enum
import typing as ta

from .. import check
from .. import lang


class ParamStyle(enum.Enum):
    QMARK = 'qmark'  # Question mark style, e.g. ...WHERE name=?
    FORMAT = 'format'  # ANSI C printf format codes, e.g. ...WHERE name=%s

    NUMERIC = 'numeric'  # Numeric, positional style, e.g. ...WHERE name=:1

    NAMED = 'named'  # Named style, e.g. ...WHERE name=:name
    PYFORMAT = 'pyformat'  # Python extended format codes, e.g. ...WHERE name=%(name)s


ParamKey: ta.TypeAlias = str | int


class ParamsPreparer(lang.Abstract):
    @abc.abstractmethod
    def add(self, k: ParamKey) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def prepare(self) -> lang.Args:
        raise NotImplementedError


class NumericParamsPreparer(ParamsPreparer, lang.Final):
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
        ret = self._str_by_key[k] = f":{pos + 1}"
        return ret

    def prepare(self) -> lang.Args:
        return lang.Args(*self._args)


class ReusableParamsPreparer(ParamsPreparer, lang.Abstract):  # noqa
    pass
