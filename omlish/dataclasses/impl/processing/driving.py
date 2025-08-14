import contextlib
import contextvars
import typing as ta

from .... import lang
from ...specs import ClassSpec
from .. import concerns as _concerns  # noqa  # imported for registration
from ..generation import processor as gp
from .base import ProcessingContext
from .base import ProcessingOption
from .base import Processor
from .registry import all_processing_context_item_factories
from .registry import ordered_processor_types


##


_OPTIONS_CONTEXT_VAR: contextvars.ContextVar[ta.Sequence[ProcessingOption]] = contextvars.ContextVar(
    f'{__name__}._OPTIONS_CONTEXT_VAR',
    default=(),
)


@contextlib.contextmanager
def processing_options_context(*opts: ProcessingOption) -> ta.Iterator[None]:
    with lang.context_var_setting(
            _OPTIONS_CONTEXT_VAR,
            (*_OPTIONS_CONTEXT_VAR.get(), *opts),
    ):
        yield


##


def drive_cls_processing(
        cls: type,
        cs: ClassSpec,
        *,
        plan_only: bool = False,
        verbose: bool = False,
) -> type:
    options: list[ProcessingOption] = list(_OPTIONS_CONTEXT_VAR.get())
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
