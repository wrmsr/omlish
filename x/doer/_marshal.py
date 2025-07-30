# ruff: noqa: UP006 UP007 UP043 UP045
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.cached import static_init
from omlish.lite.check import check
from omlish.lite.marshal import ObjMarshalContext
from omlish.lite.marshal import ObjMarshaler
from omlish.lite.marshal import set_obj_marshaler
from omlish.lite.reflect import deep_subclasses

from .configs import DoerDefConfig
from .configs import DoerExecutableConfig
from .configs import DoerTaskConfig
from .configs import PythonDoerExecutableConfig
from .configs import ShellDoerExecutableConfig


##


@dc.dataclass(frozen=True)
class _AttrTagSwitchedDoerObjMarshaler(ObjMarshaler):
    tag_attr_by_type: ta.Mapping[type, str]

    def marshal(self, o: ta.Any, ctx: ObjMarshalContext) -> ta.Any:
        return ctx.manager.marshal_obj(o)

    def unmarshal(self, o: ta.Any, ctx: ObjMarshalContext) -> ta.Any:
        check.isinstance(o, ta.Mapping)
        tc_cs = {c for c, a in self.tag_attr_by_type.items() if a in o}
        if not tc_cs:
            raise ValueError(f'No tag attr set: {o}')
        return ctx.manager.unmarshal_obj(o, check.single(tc_cs))


##


_DOER_EXECUTABLE_CONFIG_TAG_ATTR_BY_CLS: ta.Mapping[ta.Type[DoerExecutableConfig], str] = {
    ShellDoerExecutableConfig: 'sh',
    PythonDoerExecutableConfig: 'py',
}


@static_init
def _install_doer_marshaling() -> None:
    for tag_cls in [
        DoerTaskConfig,
        DoerDefConfig,
    ]:
        dct = {  # type: ignore
            cls: check.single(
                a
                for b, a in _DOER_EXECUTABLE_CONFIG_TAG_ATTR_BY_CLS.items()
                if issubclass(cls, b)
            )
            for cls in deep_subclasses(tag_cls)  # type: ignore
            if abc.ABC not in cls.__bases__
        }

        set_obj_marshaler(tag_cls, _AttrTagSwitchedDoerObjMarshaler(dct))
