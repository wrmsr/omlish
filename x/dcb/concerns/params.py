"""
check.is_(check.isinstance(cls.__dict__[PARAMS_ATTR], Params), info.params)
check.is_(check.isinstance(check.not_none(info.cls_metadata)[ParamsExtras], ParamsExtras), info.params_extras)  # noqa

    def _check_params(self) -> None:
        if self._info.params.order and not self._info.params.eq:
            raise ValueError('eq must be true if order is true')

"""
from ..processing import ProcessingContext
from ..processing import Processor
from ..registry import register_context_item_factory
from ..specs import ClassSpec
from ..std import StdParams


##


def build_std_params(cs: ClassSpec) -> StdParams:
    raise NotImplementedError


@register_context_item_factory(StdParams)
def _std_params_context_item_factory(ctx: ProcessingContext) -> StdParams:
    return build_std_params(ctx.cs)


##


class ParamsProcessor(Processor):
    def check(self) -> None:
        pass

    def process(self, cls: type) -> type:
        return cls
