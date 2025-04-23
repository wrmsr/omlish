
from .. import concerns as _concerns  # noqa  # imported for registration
from ..generation import processor as gp
from ..specs import ClassSpec
from .base import ProcessingContext
from .base import ProcessingOption
from .base import Processor
from .registry import all_processing_context_item_factories
from .registry import ordered_processor_types


##


def drive_cls_processing(
        cls: type,
        cs: ClassSpec,
        *,
        plan_only: bool = False,
        verbose: bool = False,
) -> type:
    options: list[ProcessingOption] = []
    if plan_only:
        options.append(gp.PlanOnly(True))
    if verbose:
        options.append(gp.Verbose(True))

    #

    ctx = ProcessingContext(
        cls,
        cs,
        all_processing_context_item_factories(),
        options=options,
    )

    processors: list[Processor] = [
        proc_cls(ctx)
        for proc_cls in ordered_processor_types()
    ]

    for p in processors:
        p.check()

    ret = cls
    for p in processors:
        ret = p.process(ret)

    return ret
