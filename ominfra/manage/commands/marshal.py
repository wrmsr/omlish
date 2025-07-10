from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.marshal import PolymorphicObjMarshaler

from .base import Command
from .base import CommandNameMap


##


def install_command_marshaling(
        cmds: CommandNameMap,
        msh: ObjMarshalerManager,
) -> None:
    for fn in [
        lambda c: c,
        lambda c: c.Output,
    ]:
        msh.set_obj_marshaler(
            fn(Command),
            PolymorphicObjMarshaler.of([
                PolymorphicObjMarshaler.Impl(
                    fn(cmd),
                    name,
                    msh.get_obj_marshaler(fn(cmd)),
                )
                for name, cmd in cmds.items()
            ]),
        )
