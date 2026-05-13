# ruff: noqa: UP037
import typing as ta

from ... import lang
from ..api.naming import Naming
from ..api.vias import MarshalVia
from ..api.vias import MarshalViaMetadata
from ..api.vias import UnmarshalVia
from ..api.vias import UnmarshalViaMetadata
from ..factories.lazy import LazyMarshalerFactory
from ..factories.lazy import LazyUnmarshalerFactory
from .api import AUTO_STRIP_SUFFIX
from .api import PolymorphismOptions
from .api import TypeTagging
from .api import WrapperTypeTagging
from .api import polymorphism_from_subclasses


with lang.auto_proxy_import(globals()):
    from . import marshal as _marshal
    from . import unmarshal as _unmarshal


T = ta.TypeVar('T')


##


def set_polymorphic_from_subclasses(
        *,
        type_tagging: TypeTagging = WrapperTypeTagging(),
        naming: Naming | None = None,
        strip_suffix: bool | type[AUTO_STRIP_SUFFIX] | str = False,
) -> ta.Callable[[type[T]], type[T]]:
    opts = PolymorphismOptions(
        type_tagging=type_tagging,
        naming=naming,
        strip_suffix=strip_suffix,
    )

    def inner(cls):
        lmf = LazyMarshalerFactory(lambda: _marshal.PolymorphismMarshalerFactory(
            polymorphism_from_subclasses(
                cls,
                naming=opts.naming,
                strip_suffix=opts.strip_suffix,
            ),
            opts.type_tagging,
        ))

        luf = LazyUnmarshalerFactory(lambda: _unmarshal.PolymorphismUnmarshalerFactory(
            polymorphism_from_subclasses(
                cls,
                naming=opts.naming,
                strip_suffix=opts.strip_suffix,
            ),
            opts.type_tagging,
        ))

        MarshalViaMetadata(MarshalVia(lmf))(cls)
        UnmarshalViaMetadata(UnmarshalVia(luf))(cls)

        return cls

    return inner
