"""
https://github.com/microsoft/language-server-protocol/tree/gh-pages/_specifications/lsp/3.18
https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/metaModel/metaModel.json
https://github.com/microsoft/lsprotocol/tree/main/generator
https://github.com/microsoft/lsprotocol/blob/main/generator/lsp.json
"""
import os.path
import typing as ta

from omdev.cache import data as dcache
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json


##


def _update_marshal_metadata(**kwargs):
    def inner(cls):
        return msh.update_object_metadata(**{
            **dict(
                field_naming=msh.Naming.LOW_CAMEL,
                field_defaults=msh.FieldMetadata(
                    options=msh.FieldOptions(
                        omit_if=lambda v: v is None or (not isinstance(v, str) and isinstance(v, ta.Sequence) and not v)
                    ),
                ),
            ),
            **kwargs,
        })(cls)
    return inner


##


@dc.dataclass(frozen=True, kw_only=True)
class LspType(lang.Abstract):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class ArrayLspType(LspType):
    element: LspType


LspBaseType: ta.TypeAlias = ta.Literal[
    'URI',
    'DocumentUri',
    'integer',
    'uinteger',
    'decimal',
    'RegExp',
    'string',
    'boolean',
    'null',
]


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata()
class BaseLspType(LspType):
    name: LspBaseType


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata()
class LiteralLspType(LspType):  # StructureLiteral
    value: 'LspStructure'


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata()
class MapLspType(LspType):
    key: LspType
    value: LspType


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata()
class OrLspType(LspType):
    items: ta.Sequence[LspType]


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata()
class ReferenceLspType(LspType):
    name: str


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata()
class StringLiteralLspType(LspType):
    value: str


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata()
class TupleLspType(LspType):
    items: ta.Sequence[LspType]


#


# class LspMessageDirection(enum.StrEnum):
#     SERVER_TO_CLIENT = 'serverToClient'
#     CLIENT_TO_SERVER = 'clientToServer'

LspMessageDirection: ta.TypeAlias = ta.Literal[
    'serverToClient',
    'clientToServer',
    'both',
]


@dc.dataclass(frozen=True, kw_only=True)
class LspMessage(lang.Abstract):
    method: str
    type_name: str
    message_direction: LspMessageDirection
    params: LspType | None = None
    documentation: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata(ignore_unknown=True)
class LspRequest(LspMessage):
    result: LspType


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata(ignore_unknown=True)
class LspNotification(LspMessage):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata(ignore_unknown=True)
class LspProperty:
    name: str
    optional: bool = False
    type: LspType


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata(ignore_unknown=True)
class LspStructure:
    name: str | None = None
    extends: ta.Sequence[LspType] | None = None
    mixins: ta.Sequence[LspType] | None = None
    properties: ta.Sequence[LspProperty] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata(ignore_unknown=True)
class LspEnumerationEntry:
    name: str
    value: str | int | float


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata(ignore_unknown=True)
class LspEnumeration:
    type: LspType
    values: ta.Sequence[LspEnumerationEntry]


#


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata(ignore_unknown=True)
class LspTypeAlias:
    name: str
    type: LspType


#


@dc.dataclass(frozen=True, kw_only=True)
@_update_marshal_metadata(ignore_unknown=True)
class LspSpec:
    requests: ta.Sequence[LspRequest] | None = None
    notifications: ta.Sequence[LspNotification] | None = None
    structures: ta.Sequence[LspStructure] | None = None
    enumerations: ta.Sequence[LspEnumeration] | None = None
    type_aliases: ta.Sequence[LspTypeAlias] | None = None


##


@lang.static_init
def _install_lsp_marshalling() -> None:
    extended_content_poly = msh.polymorphism_from_subclasses(
        LspType,
        naming=msh.Naming.LOW_CAMEL,
        strip_suffix=True,
    )
    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(extended_content_poly, msh.FieldTypeTagging('kind')),
        msh.PolymorphismUnmarshalerFactory(extended_content_poly, msh.FieldTypeTagging('kind')),
    )


##


LSP_SPEC_DATA = dcache.GitSpec(
    'https://github.com/microsoft/lsprotocol',
    rev='a79f4dc86bcf3f8655dbc7171952c7dcf6931f37',
    subtrees=[
        'generator/lsp.json',
        'generator/lsp.schema.json',
    ],
)


def _main() -> None:
    spec_dir = dcache.default().get(LSP_SPEC_DATA)

    with open(os.path.join(spec_dir, 'generator', 'lsp.json')) as f:
        spec_content = json.load(f)

    spec = msh.unmarshal(spec_content, LspSpec)

    print(json.dumps_pretty(msh.marshal(spec)))


if __name__ == '__main__':
    _main()
