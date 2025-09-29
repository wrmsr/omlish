from omlish import lang
from omlish import marshal as msh

from .types import ToolDtype


##


@lang.static_init
def _install_standard_marshaling() -> None:
    tool_dtype_poly = msh.polymorphism_from_subclasses(ToolDtype, naming=msh.Naming.SNAKE)
    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(tool_dtype_poly),
        msh.PolymorphismUnmarshalerFactory(tool_dtype_poly),
    )
