import typing as ta

from .. import nodes as no


Args = ta.Sequence[ta.Any]
Xlat = ta.Callable[[ta.Any], no.Node]
Macro = ta.Callable[['Xlat', Args], no.Node]
Matcher = ta.Union[ta.Callable[[Args], bool], bool]
