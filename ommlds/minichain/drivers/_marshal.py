from omlish import lang
from omlish import marshal as msh

from .ai import events as _ai_events  # noqa
from .tools import events as _tools_events  # noqa
from .types import Event
from .user import events as _user_events  # noqa


##


@lang.static_init
def _install_standard_marshaling() -> None:
    cls_poly = msh.polymorphism_from_subclasses(
        Event,
        naming=msh.Naming.SNAKE,
        strip_suffix='Event',
    )
    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(cls_poly),
        msh.PolymorphismUnmarshalerFactory(cls_poly),
    )
