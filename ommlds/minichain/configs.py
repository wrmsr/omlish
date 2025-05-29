"""
TODO:
 - ServiceConfig, specifically?
"""
from omlish import lang
from omlish import typedvalues as tv


##


class Config(tv.TypedValue, lang.Abstract):
    pass


##


def consume_configs(
        *cfgs: Config,
        override: bool = False,
        check_type: type | tuple[type, ...] | None = None,
) -> tv.TypedValuesConsumer[Config]:
    return tv.TypedValues(
        *cfgs,
        override=override,
        check_type=check_type if check_type is not None else Config,
    ).consume()
