from ...api.dbapi import DbapiAdapter
from ...params import ParamStyle
from .dialect import SqliteDialect


##


def sqlite_adapter(
        *,
        param_style: ParamStyle = ParamStyle.QMARK,
) -> DbapiAdapter:
    return DbapiAdapter(
        param_style=param_style,
        dialect=SqliteDialect(),
    )
