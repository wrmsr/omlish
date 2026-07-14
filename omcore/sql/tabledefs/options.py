import typing as ta

from ... import lang
from ... import typedvalues as tv


##


class ColumnOption(tv.TypedValue, lang.Abstract):
    pass


class IndexOption(tv.TypedValue, lang.Abstract):
    pass


class TableOption(tv.TypedValue, lang.Abstract):
    pass


ColumnOptions: ta.TypeAlias = tv.TypedValues[ColumnOption]
IndexOptions: ta.TypeAlias = tv.TypedValues[IndexOption]
TableOptions: ta.TypeAlias = tv.TypedValues[TableOption]


##


class BackendOption(tv.TypedValue, lang.Abstract):
    """
    Marker for any backend-specific option, of any element kind. A backend defines its own marker subclass (e.g.
    PostgresOption) under backends/<name>, mixed into concrete options alongside the relevant ColumnOption /
    IndexOption / TableOption. Core code references only this base, never a concrete backend.
    """
