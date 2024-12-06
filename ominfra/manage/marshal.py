import typing as ta

from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.marshal import PolymorphicObjMarshaler

from .commands.base import Command


def install_command_marshaling(
        msh: ObjMarshalerManager,
        cmds_by_name: ta.Mapping[str, ta.Type[Command]]
) -> None:
    for fn in [
        lambda c: c,
        lambda c: c.Output,
    ]:
        msh.register_opj_marshaler(
            fn(Command),
            PolymorphicObjMarshaler.of([
                PolymorphicObjMarshaler.Impl(
                    fn(cmd),
                    name,
                    msh.get_obj_marshaler(fn(cmd)),
                )
                for name, cmd in cmds_by_name.items()
            ]),
        )
