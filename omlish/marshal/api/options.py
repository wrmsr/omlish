"""
TODO:
 - MarshalOption, UnmarshalOption, check if a context got something unexpected
 - Options only apply to Factories?
  - MarshalFactoryOption, MarshalOption, UnmarshalFactoryOption, MarshalOption ?
"""
import typing as ta

from ... import lang
from ... import typedvalues as tv
from .configs import Config
from .configs import Configs


##


class Option(tv.TypedValue, lang.Abstract):
    pass


Options: ta.TypeAlias = tv.TypedValues[Option]


##


_EMPTY_OPTIONS: Options = Options()


##


class DefaultOptions(tv.UniqueScalarTypedValue[Options], Config, lang.Final):
    pass


class IgnoreDefaultOptions(tv.UniqueTypedValue, Option, lang.Final):
    pass


def build_effective_options(configs: Configs, options: ta.Iterable[Option] | None = None) -> Options:
    if not options:
        return _EMPTY_OPTIONS

    given = Options(*options)
    if IgnoreDefaultOptions in given:
        return given

    if (defaults := configs.get().get(DefaultOptions)) is None:
        return given

    return defaults.v.update(
        *given,
        mode='override',
    )
