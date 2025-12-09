import contextlib
import contextvars
import sys
import typing as ta

from .... import lang
from ...specs import ClassSpec
from .. import concerns as _concerns  # noqa  # imported for registration
from ..configs import DEFAULT_NAMED_PACKAGE_CONFIG
from ..configs import PACKAGE_CONFIG_CACHE
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


def _is_pkg_init_mod(mod_name: str) -> bool:
    if (mod_obj := sys.modules.get(mod_name)) is None:
        return False
    if (mod_spec := getattr(mod_obj, '__spec__', None)) is None:
        return False
    return bool(mod_spec.submodule_search_locations)


def drive_cls_processing(
        cls: type,
        cs: ClassSpec,
        *,
        plan_only: bool = False,
        warn: bool = False,
        debug: bool = False,
) -> type:
    options: list[ProcessingOption] = list(_OPTIONS_CONTEXT_VAR.get())
    if plan_only:
        options.append(gp.PlanOnly(True))
    if warn or debug:
        options.append(gp.Verbosity(warn=warn, debug=debug))

    #

    cls_mod = cls.__module__
    if _is_pkg_init_mod(cls_mod):
        cls_pkg = cls_mod
    else:
        cls_pkg = cls_mod.rpartition('.')[0]
    pkg_cfg = lang.coalesce(PACKAGE_CONFIG_CACHE.get(cls_pkg), DEFAULT_NAMED_PACKAGE_CONFIG)

    #

    ctx = ProcessingContext(
        cls,
        cs,
        all_processing_context_item_factories(),
        pkg_cfg=pkg_cfg,
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
