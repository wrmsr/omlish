import typing as ta

from omlish import lang
from omlish import typedvalues as tv


##


class Option(tv.TypedValue, lang.Abstract):
    pass


# TODO: PEP696 default=Option
OptionT_co = ta.TypeVar('OptionT_co', bound=Option, covariant=True)


##


class Output(tv.TypedValue, lang.Abstract):
    pass


# TODO: PEP696 default=Output
OutputT_contra = ta.TypeVar('OutputT_contra', bound=Output, contravariant=True)
