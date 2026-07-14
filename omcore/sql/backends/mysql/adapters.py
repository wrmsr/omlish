from ...api.dbapi import DbapiAdapter
from ...params import ParamStyle
from .dialect import MysqlDialect


##


def mysql_adapter(
        *,
        param_style: ParamStyle = ParamStyle.PYFORMAT,
) -> DbapiAdapter:
    return DbapiAdapter(
        param_style=param_style,
        dialect=MysqlDialect(),
    )
