"""
TODO:
 - MarshalOption, UnmarshalOption, check if a context got something unexpected
 - Options only apply to Factories?
  - MarshalFactoryOption, MarshalOption, UnmarshalFactoryOption, MarshalOption ?
"""
import typing as ta


if ta.TYPE_CHECKING:
    from ... import collections as col


##


class Option:
    pass


Options: ta.TypeAlias = 'col.TypeMap[Option]'
