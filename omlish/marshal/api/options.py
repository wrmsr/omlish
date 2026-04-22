"""
TODO:
 - MarshalOption, UnmarshalOption, check if a context got something unexpected
 - Options only apply to Factories?
  - MarshalFactoryOption, MarshalOption, UnmarshalFactoryOption, MarshalOption ?
"""
import typing as ta

from ... import lang
from ... import typedvalues as tv


##


class Option(tv.TypedValue, lang.Abstract):
    pass


Options: ta.TypeAlias = tv.TypedValues[Option]


##


_EMPTY_OPTIONS: Options = Options()
