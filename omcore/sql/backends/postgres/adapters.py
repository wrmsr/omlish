from ...api.dbapi import DbapiAdapter
from ...params import ParamStyle
from .dialect import PostgresDialect


##


def postgres_adapter(
        *,
        param_style: ParamStyle = ParamStyle.FORMAT,
) -> DbapiAdapter:
    return DbapiAdapter(
        param_style=param_style,
        dialect=PostgresDialect(),
    )
