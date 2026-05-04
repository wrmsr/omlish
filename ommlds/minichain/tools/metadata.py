import typing as ta

from omlish import lang
from omlish import marshal as msh

from ..metadata import CommonMetadata
from ..metadata import Metadata


##


class ToolUseMetadata(Metadata, lang.Abstract, lang.Sealed):
    pass


ToolUseMetadatas: ta.TypeAlias = ToolUseMetadata | CommonMetadata


##


class ToolUseResultMetadata(Metadata, lang.Abstract, lang.Sealed):
    pass


ToolUseResultMetadatas: ta.TypeAlias = ToolUseResultMetadata | CommonMetadata


##


@msh.register_global_lazy_init
def _setup_marshaling(cfgs: msh.ConfigRegistry) -> None:
    for cls in [
        ToolUseMetadata,
        ToolUseResultMetadata,
    ]:
        msh.install_standard_factories_to(cfgs, *msh.standard_polymorphism_factories(
            msh.polymorphism_from_subclasses(
                cls,
                naming=msh.Naming.SNAKE,
            ),
            msh.WrapperTypeTagging(),
        ))
