from omcore import marshal as msh

from .types import ToolDtype


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    tool_dtype_poly = msh.polymorphism_from_subclasses(ToolDtype, naming=msh.Naming.SNAKE)
    msh.install_standard_factories(
        cfgs,
        msh.PolymorphismMarshalerFactory(tool_dtype_poly),
        msh.PolymorphismUnmarshalerFactory(tool_dtype_poly),
    )
