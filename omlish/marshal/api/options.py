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
from .configs import ConfigRegistry
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


##


def update_default_options(
        configs: ConfigRegistry,
        *options: Option,
        discard: ta.Literal['all'] | ta.Iterable[type] | None = None,
        mode: ta.Literal['append', 'prepend', 'override', 'default'] = 'append',
) -> ConfigRegistry:
    def inner(_: ConfigRegistry) -> None:
        if (defaults := configs.get().get(DefaultOptions)) is not None:
            new = defaults.v.update(*options, discard=discard, mode=mode)
        else:
            new = Options(*options)

        configs.update(None, DefaultOptions(new), mode='override')

    configs.call_atomically(inner)
    return configs


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
