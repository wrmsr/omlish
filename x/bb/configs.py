"""
TODO:
- dynamic
- hierarchical
- expire
 - lol, configurable
- class-level default kwargs
- sql source? kazoo source?
- class Parsable(ta.Typeclass[T]): ?
- generate dataclass on the side, allow instantiation as if it were just one of those
- https://github.com/toml-lang/toml
- keyvalues interop
- STRICT MODE - reject unknown env vars with a given prefix
"""
import abc
import collections.abc
import datetime
import itertools
import os
import typing as ta
import weakref

from omnibus import callables as ca
from omnibus import check
from omnibus import lang
from omnibus import properties

from . import typeclass as tc


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


class NOT_SET(lang.Marker):
    pass


Getter = ta.Callable[[str], ta.Any]
Parser = ta.Callable[[str], ta.Any]


class ConfigValueSource(lang.Abstract):

    @abc.abstractmethod
    def get_config_value(self, name: str) -> ta.Any:
        raise NotImplementedError


_type = type


class ConfigProperty:

    def __init__(
            self,
            default: ta.Any = NOT_SET,
            type: ta.Any = NOT_SET,
            *,
            name: str = None,
            coerce: ta.Callable[[ta.Any], ta.Any] = None,
            validate: ta.Callable[[ta.Any], None] = None,
            required: bool = False,
            attr_name: str = None,
            parser: Parser = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.default = default
        self.type = _type(default) if default is not NOT_SET and type is NOT_SET else type
        self.coerce = coerce
        self.validate = validate
        self.required = required
        self.attr_name = attr_name or '_%s_%x_value' % (self.__class__.__name__, id(self))
        self._parser = parser

    @properties.cached
    def parser(self) -> Parser:
        if self._parser is not None:
            return self._parser
        else:
            return Parsable(self.type).parse

    def __get__(self, instance: ta.Any, owner: ta.Type) -> ta.Any:
        if instance is None:
            return self

        if self.name is None:
            raise NameError

        try:
            return getattr(instance, self.attr_name)
        except AttributeError:
            pass

        value = instance.get_config_value(self.name)

        if value is NOT_SET:
            if self.default is not NOT_SET:
                if callable(self.default):
                    value = self.default(instance)
                else:
                    value = self.default
            else:
                raise ValueError(f'{self.name} is not set')

        if self.coerce is not None:
            value = self.coerce(value)

        elif self.type is not NOT_SET and self.type != str and isinstance(value, str):
            value = self.parser(value)

        if self.validate is not None:
            self.validate(value)

        setattr(instance, self.attr_name, value)
        return value

    def __set_name__(self, owner: ta.Any, name: str) -> None:
        if self.name is None:
            self.name = name.upper()

    def __set__(self, instance: ta.Any, value: ta.Any) -> None:
        if instance is None:
            raise ValueError('Operation not supported')
        setattr(instance, self.attr_name, value)

    def __delete__(self, instance: ta.Any) -> None:
        if instance is None:
            raise ValueError('Operation not supported')
        delattr(instance, self.attr_name)


def check_required(instance) -> None:
    for name in dir(instance):
        try:
            member = getattr(type(instance), name)
        except AttributeError:
            continue

        try:
            if not isinstance(member, ConfigProperty):
                continue
        except TypeError:
            continue

        if member.required:
            getattr(instance, name)


def infer_getter(source: ta.Any) -> Getter:
    if isinstance(source, ConfigValueSource):
        return source.get_config_value
    elif isinstance(source, collections.abc.Mapping):
        return dict_getter(source)
    elif source is None:
        return lambda name: NOT_SET
    else:
        check.arg(callable(source))
        return source


CONFIG_TYPE_REGISTRY: ta.Set[ta.Type['Config']] = weakref.WeakSet()


class ConfigMeta(abc.ABCMeta):

    def __new__(mcls, name, bases, namespace):
        cls = lang.super_meta(super(), mcls, name, bases, namespace)
        CONFIG_TYPE_REGISTRY.add(cls)
        return cls


class Config(ConfigValueSource, metaclass=ConfigMeta):

    CONFIG_PREFIX = NOT_SET

    def __init__(self, source=None) -> None:
        super().__init__()
        getter = infer_getter(source)
        if self.CONFIG_PREFIX is NOT_SET:
            cls_name = type(self).__name__
            check.state(cls_name.endswith('Config'))
            prefix = lang.decamelize(cls_name[:-6]).upper() + '_'
        elif self.CONFIG_PREFIX is not None:
            prefix = check.isinstance(self.CONFIG_PREFIX, str)
        else:
            prefix = None
        if prefix:
            getter = prefixed_getter(prefix, getter)
        self._getter = getter

    def get_config_value(self, name: str) -> ta.Any:
        return self._getter(name)


@ca.constructor()
def prefixed_getter(prefix: str, getter: Getter) -> Getter:
    def inner(name: str) -> ta.Any:
        return getter(prefix + name)

    return inner


@ca.constructor()
def filtered_getter(allowed: ta.Iterable[str], getter: Getter) -> Getter:
    def inner(name: str) -> ta.Any:
        if name in allowed:
            return getter(name)
        else:
            return NOT_SET

    return inner


@ca.constructor()
def aliased_getter(aliases: ta.Dict[str, ta.Union[str, ta.Iterable[str]]], getter: Getter) -> Getter:
    def inner(name: str) -> ta.Any:
        name_aliases = aliases.get(name, [])
        if isinstance(name_aliases, str):
            name_aliases = [name_aliases]
        for aname in itertools.chain([name], name_aliases):
            value = getter(aname)
            if value is not NOT_SET:
                return value
        return NOT_SET

    return inner


@ca.constructor()
def dict_getter(dct: ta.Mapping) -> Getter:
    def getter(name: str) -> ta.Any:
        try:
            return dct[name]
        except KeyError:
            return NOT_SET

    return getter


@ca.constructor()
def chain_getter(*getters) -> Getter:
    def inner(name: str) -> ta.Any:
        for getter in getters:
            value = getter(name)
            if value is not NOT_SET:
                return value
        return NOT_SET

    return inner


def parse_env_file(path: str) -> ta.Iterator[ta.Tuple[str, str]]:
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            k = k.strip()
            v = v.strip().strip("'").strip('"')
            yield k, v


def load_env_file(path: str) -> None:
    for k, v in parse_env_file(path):
        try:
            os.environ[k]
        except KeyError:
            os.environ[k] = v


def maybe_load_env_file(path: str) -> None:
    if os.path.isfile(path):
        load_env_file(path)


@ca.constructor()
def env_getter() -> Getter:
    return dict_getter(os.environ)


@ca.constructor()
def attr_getter(obj: ta.Any) -> Getter:
    def getter(name: str) -> ta.Any:
        return getattr(obj, name, NOT_SET)

    return getter


@ca.constructor()
def nop_getter(name: str) -> ta.Any:
    return NOT_SET


def property(
        default: T = NOT_SET,
        type: ta.Type[T] = NOT_SET,
        *args,
        **kwargs
) -> T:
    return ConfigProperty(default, type, *args, **kwargs)  # noqa


class Parsable(tc.Typeclass[T]):

    @tc.method()
    def parse(self, s: str) -> T:
        raise NotImplementedError


class _(Parsable[str]):  # noqa

    def parse(self, s: str) -> str:
        return s


class _(Parsable[int]):  # noqa

    def parse(self, s: str) -> int:
        return int(s)


class _(Parsable[float]):  # noqa

    def parse(self, s: str) -> float:
        return float(s)


class _(Parsable[bool]):  # noqa

    TRUE_VALUES = frozenset(['yes', 'true', 't', '1'])
    FALSE_VALUES = frozenset(['no', 'false', 'f', '0'])

    def parse(self, s: str) -> bool:
        if s.lower() in self.TRUE_VALUES:
            return True
        elif s.lower() in self.FALSE_VALUES:
            return False
        else:
            raise ValueError(s)


class _(Parsable[datetime.date]):  # noqa

    FORMAT = '%Y-%m-%d'

    def parse(self, s: str) -> datetime.date:
        return datetime.datetime.strptime(s, self.FORMAT).date()


class _(Parsable[ta.Optional[T]]):  # noqa

    @properties.cached
    def t(self) -> ta.Callable[[str], T]:
        return Parsable(self[T]).parse

    def parse(self, s: str) -> ta.Optional[T]:
        if not s:
            return None
        else:
            return self.t(s)


class _(Parsable[ta.List[T]]):  # noqa

    @properties.cached
    def t(self) -> ta.Callable[[str], T]:
        return Parsable(self[T]).parse

    def parse(self, s: str) -> ta.List[T]:
        return [self.t(e) for e in s.split(',')]


class _(Parsable[ta.Set[T]]):  # noqa

    @properties.cached
    def t(self) -> ta.Callable[[str], T]:
        return Parsable(self[T]).parse

    def parse(self, s: str) -> ta.List[T]:
        return {self.t(e) for e in s.split(',')}


class _(Parsable[ta.Dict[K, V]]):  # noqa

    @properties.cached
    def k(self) -> ta.Callable[[str], K]:
        return Parsable(self[K]).parse

    @properties.cached
    def v(self) -> ta.Callable[[str], V]:
        return Parsable(self[V]).parse

    def parse(self, s: str) -> ta.Dict[K, V]:
        ret = {}
        for part in s.split(','):
            key_part, value_part = part.split('=')
            ret[self.k(key_part)] = self.v(value_part)
        return ret
