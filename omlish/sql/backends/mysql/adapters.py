from ...api.dbapi import DbapiAdapter
from ...params import ParamStyle
from ...syntax import QuoteStyles
from .queries import MysqlRenderer


##


def mysql_adapter(
        *,
        param_style: ParamStyle = ParamStyle.PYFORMAT,
) -> DbapiAdapter:
    return DbapiAdapter(
        param_style=param_style,
        quote_style=QuoteStyles.BACKTICK,
        query_renderer=MysqlRenderer,
    )
