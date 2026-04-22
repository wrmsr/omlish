import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from ... import reflect as rfl


JsonValue: ta.TypeAlias = ta.Union[  # noqa
    ta.Mapping[str, 'JsonValue'],

    ta.Sequence['JsonValue'],

    str,

    int,
    float,

    bool,

    None,
]


class MarshalJsonValue(lang.NotInstantiable, lang.Final):
    pass


class _JsonValueMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if rty is not MarshalJsonValue:
            return None
        return lambda: msh.NopMarshalerUnmarshaler()


class _JsonValueUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if rty is not MarshalJsonValue:
            return None
        return lambda: msh.NopMarshalerUnmarshaler()


@lang.static_init
def _install_standard_marshaling() -> None:
    msh.register_global_config(
        JsonValue,
        msh.ReflectOverride(MarshalJsonValue),
        identity=True,
    )

    msh.install_standard_factories(
        _JsonValueMarshalerFactory(),
        _JsonValueUnmarshalerFactory(),
    )


@dc.dataclass(frozen=True)
@msh.update_fields_options(['v'], marshal_as=JsonValue, unmarshal_as=JsonValue)
class JsonContent:
    v: JsonValue


def test_marshal_json():
    jv = {'abc': [{'def': 420}, 'ghi']}
    m = msh.marshal(jv, JsonValue)
    assert m == jv
    jv2 = msh.unmarshal(m, JsonValue)
    assert jv2 == jv

    jc = JsonContent(jv)
    m = msh.marshal(jc)
    assert m == {'v': jv}
    jc2 = msh.unmarshal(m, JsonContent)
    assert jc2 == jc
