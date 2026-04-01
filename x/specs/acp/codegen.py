"""
JSON Schema to Python dataclass code generator.
"""
import io
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.lang.casing import StringCasingError
from omlish.specs import jsonschema as js


##


MISSING: ta.Any = object()

JSON_TYPE_MAP: ta.Mapping[str, str] = {
    'string': 'str',
    'integer': 'int',
    'number': 'float',
    'boolean': 'bool',
}

_low_camel_to_snake = lang.LOW_CAMEL_CASE.to(lang.SNAKE_CASE)


def _snake_name(json_name: str) -> str:
    if json_name.startswith('_'):
        return json_name.lstrip('_')
    try:
        return _low_camel_to_snake(json_name)
    except StringCasingError:
        return json_name


def _ref_name(ref_str: str) -> str:
    return ref_str.split('/')[-1]


def _tag_to_camel(tag: str) -> str:
    return ''.join(p.capitalize() for p in tag.split('_'))


##
# IR: Type references


class TypeRef(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class PrimitiveTypeRef(TypeRef, lang.Final):
    python_type: str


@dc.dataclass(frozen=True)
class RefTypeRef(TypeRef, lang.Final):
    name: str


@dc.dataclass(frozen=True)
class ArrayTypeRef(TypeRef, lang.Final):
    item: TypeRef


@dc.dataclass(frozen=True)
class NullableTypeRef(TypeRef, lang.Final):
    inner: TypeRef


class AnyTypeRef(TypeRef, lang.Final):
    pass


class MapTypeRef(TypeRef, lang.Final):
    pass


@dc.dataclass(frozen=True)
class UnionTypeRef(TypeRef, lang.Final):
    members: ta.Sequence[TypeRef]


##
# IR: Definitions


@dc.dataclass(frozen=True, kw_only=True)
class FieldDef(lang.Final):
    json_name: str
    python_name: str
    type_ref: TypeRef
    required: bool
    default: ta.Any = MISSING


@dc.dataclass(frozen=True, kw_only=True)
class ObjectTypeDef(lang.Final):
    name: str
    description: str | None = None
    fields: ta.Sequence[FieldDef] = ()


@dc.dataclass(frozen=True, kw_only=True)
class StringEnumTypeDef(lang.Final):
    name: str
    description: str | None = None
    values: ta.Sequence[str] = ()


@dc.dataclass(frozen=True, kw_only=True)
class DiscriminatedUnionVariant(lang.Final):
    tag_value: str
    ref_name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class DiscriminatedUnionTypeDef(lang.Final):
    name: str
    description: str | None = None
    discriminator_field: str = ''
    variants: ta.Sequence[DiscriminatedUnionVariant] = ()


@dc.dataclass(frozen=True, kw_only=True)
class AnyOfUnionTypeDef(lang.Final):
    name: str
    description: str | None = None
    members: ta.Sequence[TypeRef] = ()


@dc.dataclass(frozen=True, kw_only=True)
class TypeAliasTypeDef(lang.Final):
    name: str
    description: str | None = None
    target: TypeRef | None = None


@dc.dataclass(frozen=True, kw_only=True)
class EmptyTypeDef(lang.Final):
    name: str
    description: str | None = None


TypeDef: ta.TypeAlias = ta.Union[
    ObjectTypeDef,
    StringEnumTypeDef,
    DiscriminatedUnionTypeDef,
    AnyOfUnionTypeDef,
    TypeAliasTypeDef,
    EmptyTypeDef,
]


##


@dc.dataclass(frozen=True, kw_only=True)
class VariantWrapperDef(lang.Final):
    class_name: str
    union_name: str
    tag_field_json: str
    tag_field_python: str
    tag_value: str
    source_fields: ta.Sequence[FieldDef] = ()


##


class JsonSchemaCodeGen:
    def __init__(self, root_kws: js.Keywords) -> None:
        super().__init__()

        self._defs: dict[str, js.Keywords] = dict(root_kws[js.Defs].m)
        self._type_defs: dict[str, TypeDef] = {}
        self._disc_unions: dict[str, DiscriminatedUnionTypeDef] = {}
        self._variant_wrappers: list[VariantWrapperDef] = []

        self._classify_all()
        self._build_variant_wrappers()

    # Classification

    def _classify_all(self) -> None:
        for name, kws in self._defs.items():
            td = self._classify_def(name, kws)
            self._type_defs[name] = td
            if isinstance(td, DiscriminatedUnionTypeDef):
                self._disc_unions[name] = td

    def _classify_def(self, name: str, kws: js.Keywords) -> TypeDef:
        by_type = kws.by_type
        by_tag = kws.by_tag

        desc_kw = by_type.get(js.Description)
        desc_str = desc_kw.s if desc_kw else None

        disc_kw = by_tag.get('discriminator')
        if disc_kw is not None and js.OneOf in by_type:
            return self._classify_disc_union(name, desc_str, kws, disc_kw)

        one_of_kw = by_type.get(js.OneOf)
        if one_of_kw is not None and self._is_string_const_one_of(one_of_kw):
            values = [m[js.Const].v for m in one_of_kw.kws]
            return StringEnumTypeDef(name=name, description=desc_str, values=values)

        enum_kw = by_type.get(js.Enum)
        if enum_kw is not None:
            return StringEnumTypeDef(name=name, description=desc_str, values=list(enum_kw.vs))

        if js.Properties in by_type:
            return self._classify_object(name, desc_str, kws)

        any_of_kw = by_type.get(js.AnyOf)
        if any_of_kw is not None:
            return self._classify_any_of(name, desc_str, any_of_kw)

        type_kw = by_type.get(js.Type)
        if type_kw is not None:
            target = self._resolve_type_from_type_kw(type_kw, kws)
            return TypeAliasTypeDef(name=name, description=desc_str, target=target)

        return EmptyTypeDef(name=name, description=desc_str)

    @staticmethod
    def _is_string_const_one_of(one_of: js.OneOf) -> bool:
        if not one_of.kws:
            return False
        for m in one_of.kws:
            if js.Const not in m.by_type:
                return False
            type_kw = m.by_type.get(js.Type)
            if type_kw is None or type_kw.ss != 'string':
                return False
        return True

    @staticmethod
    def _classify_disc_union(
            name: str,
            desc_str: str | None,
            kws: js.Keywords,
            disc_kw: js.UnknownKeyword,
    ) -> DiscriminatedUnionTypeDef:
        prop_name = disc_kw.value['propertyName']
        one_of = kws.by_type[js.OneOf]

        variants: list[DiscriminatedUnionVariant] = []
        for variant_kws in one_of.kws:
            props = variant_kws.by_type.get(js.Properties)
            if props is None or prop_name not in props.m:
                continue
            tag_kws = props.m[prop_name]
            const_kw = tag_kws.by_type.get(js.Const)
            if const_kw is None:
                continue

            ref_name_str: str | None = None
            all_of = variant_kws.by_type.get(js.AllOf)
            if all_of is not None and len(all_of.kws) == 1:
                ref_kw = all_of.kws[0].by_type.get(js.Ref)
                if ref_kw is not None:
                    ref_name_str = _ref_name(ref_kw.s)

            variants.append(DiscriminatedUnionVariant(tag_value=const_kw.v, ref_name=ref_name_str))

        return DiscriminatedUnionTypeDef(
            name=name,
            description=desc_str,
            discriminator_field=prop_name,
            variants=variants,
        )

    def _classify_object(self, name: str, desc_str: str | None, kws: js.Keywords) -> ObjectTypeDef:
        props = kws.by_type[js.Properties]
        req_kw = kws.by_type.get(js.Required)
        required_names: ta.AbstractSet[str]
        if req_kw is not None:
            required_names = {req_kw.ss} if isinstance(req_kw.ss, str) else set(req_kw.ss)
        else:
            required_names = frozenset()

        fields: list[FieldDef] = []
        for json_name, field_kws in props.m.items():
            fields.append(self._classify_field(json_name, field_kws, json_name in required_names))

        return ObjectTypeDef(name=name, description=desc_str, fields=fields)

    def _classify_field(self, json_name: str, kws: js.Keywords, required: bool) -> FieldDef:
        python_name = _snake_name(json_name)
        type_ref = self._resolve_field_type(kws)

        default: ta.Any = MISSING
        default_kw = kws.by_type.get(js.Default)
        if default_kw is not None:
            dv = default_kw.v
            if isinstance(dv, (str, int, float, bool, type(None))):
                default = dv
            else:
                if not isinstance(type_ref, NullableTypeRef):
                    type_ref = NullableTypeRef(inner=type_ref)
                default = None

        if not required and default is MISSING:
            if not isinstance(type_ref, NullableTypeRef):
                type_ref = NullableTypeRef(inner=type_ref)
            default = None

        return FieldDef(
            json_name=json_name,
            python_name=python_name,
            type_ref=type_ref,
            required=required,
            default=default,
        )

    def _classify_any_of(
            self,
            name: str,
            desc_str: str | None,
            any_of: js.AnyOf,
    ) -> TypeDef:
        all_const = all(js.Const in m.by_type for m in any_of.kws)
        if all_const:
            types = set()
            for m in any_of.kws:
                type_kw = m.by_type.get(js.Type)
                if type_kw and isinstance(type_kw.ss, str):
                    types.add(type_kw.ss)
            if len(types) == 1:
                t = types.pop()
                if t in JSON_TYPE_MAP:
                    return TypeAliasTypeDef(
                        name=name, description=desc_str, target=PrimitiveTypeRef(JSON_TYPE_MAP[t]),
                    )

        non_const = [m for m in any_of.kws if js.Const not in m.by_type]
        if non_const and len(non_const) < len(any_of.kws):
            members = [self._resolve_field_type(m) for m in non_const]
            if len(members) == 1:
                return TypeAliasTypeDef(name=name, description=desc_str, target=members[0])
            return AnyOfUnionTypeDef(name=name, description=desc_str, members=members)

        members = [self._resolve_field_type(m) for m in any_of.kws]
        if len(members) == 1:
            return TypeAliasTypeDef(name=name, description=desc_str, target=members[0])

        return AnyOfUnionTypeDef(name=name, description=desc_str, members=members)

    # Type reference resolution

    def _resolve_field_type(self, kws: js.Keywords) -> TypeRef:
        by_type = kws.by_type

        all_of = by_type.get(js.AllOf)
        if all_of is not None and len(all_of.kws) == 1:
            ref_kw = all_of.kws[0].by_type.get(js.Ref)
            if ref_kw is not None:
                return RefTypeRef(_ref_name(ref_kw.s))

        ref_kw = by_type.get(js.Ref)
        if ref_kw is not None:
            return RefTypeRef(_ref_name(ref_kw.s))

        any_of = by_type.get(js.AnyOf)
        if any_of is not None:
            return self._resolve_any_of_type(any_of)

        type_kw = by_type.get(js.Type)
        if type_kw is not None:
            return self._resolve_type_from_type_kw(type_kw, kws)

        return AnyTypeRef()

    def _resolve_any_of_type(self, any_of: js.AnyOf) -> TypeRef:
        refs: list[TypeRef] = []
        has_null = False

        for m in any_of.kws:
            type_kw = m.by_type.get(js.Type)
            if type_kw is not None and type_kw.ss == 'null':
                has_null = True
                continue
            refs.append(self._resolve_field_type(m))

        inner: TypeRef
        if not refs:
            inner = PrimitiveTypeRef('None')
        elif len(refs) == 1:
            inner = refs[0]
        elif not all(isinstance(r, PrimitiveTypeRef) for r in refs):
            # Unions of multiple complex types can't be marshaled without explicit polymorphism registration.
            inner = AnyTypeRef()
        else:
            inner = UnionTypeRef(members=refs)

        if has_null:
            return NullableTypeRef(inner=inner)
        return inner

    def _resolve_type_from_type_kw(self, type_kw: js.Type, kws: js.Keywords) -> TypeRef:
        ss = type_kw.ss
        items_kw = kws.by_type.get(js.Items)

        if isinstance(ss, str):
            return self._resolve_single_type(ss, items_kw)

        types = list(ss)
        has_null = 'null' in types
        non_null = [t for t in types if t != 'null']

        inner: TypeRef
        if not non_null:
            inner = PrimitiveTypeRef('None')
        elif len(non_null) == 1:
            inner = self._resolve_single_type(non_null[0], items_kw)
        else:
            inner = UnionTypeRef(members=[self._resolve_single_type(t, items_kw) for t in non_null])

        if has_null:
            return NullableTypeRef(inner=inner)
        return inner

    def _resolve_single_type(self, type_str: str, items_kw: js.Items | None = None) -> TypeRef:
        if type_str in JSON_TYPE_MAP:
            return PrimitiveTypeRef(JSON_TYPE_MAP[type_str])
        if type_str == 'object':
            return MapTypeRef()
        if type_str == 'array':
            if items_kw is not None:
                return ArrayTypeRef(item=self._resolve_field_type(items_kw.kw))
            return ArrayTypeRef(item=AnyTypeRef())
        if type_str == 'null':
            return PrimitiveTypeRef('None')
        return AnyTypeRef()

    # Variant wrapper generation

    def _build_variant_wrappers(self) -> None:
        for union_name, union_td in self._disc_unions.items():
            tag_json = union_td.discriminator_field
            tag_python = _snake_name(tag_json)

            for variant in union_td.variants:
                wrapper_name = _tag_to_camel(variant.tag_value) + union_name

                source_fields: ta.Sequence[FieldDef] = ()
                if variant.ref_name is not None:
                    ref_td = self._type_defs.get(variant.ref_name)
                    if isinstance(ref_td, ObjectTypeDef):
                        source_fields = ref_td.fields

                self._variant_wrappers.append(VariantWrapperDef(
                    class_name=wrapper_name,
                    union_name=union_name,
                    tag_field_json=tag_json,
                    tag_field_python=tag_python,
                    tag_value=variant.tag_value,
                    source_fields=source_fields,
                ))

    # Code generation

    def _render_type_ann(self, ref: TypeRef, *, quote_refs: bool = True) -> str:
        if isinstance(ref, PrimitiveTypeRef):
            return ref.python_type
        if isinstance(ref, RefTypeRef):
            return f"'{ref.name}'" if quote_refs else ref.name
        if isinstance(ref, ArrayTypeRef):
            return f'ta.Sequence[{self._render_type_ann(ref.item, quote_refs=quote_refs)}]'
        if isinstance(ref, NullableTypeRef):
            return f'ta.Optional[{self._render_type_ann(ref.inner, quote_refs=quote_refs)}]'
        if isinstance(ref, AnyTypeRef):
            return 'ta.Any'
        if isinstance(ref, MapTypeRef):
            return 'ta.Mapping[str, ta.Any]'
        if isinstance(ref, UnionTypeRef):
            parts = ', '.join(self._render_type_ann(m, quote_refs=quote_refs) for m in ref.members)
            return f'ta.Union[{parts}]'
        raise TypeError(ref)

    def _gen_field_lines(self, field: FieldDef) -> list[str]:
        ann = self._render_type_ann(field.type_ref)

        if field.json_name == '_meta':
            return [
                f'    {field.python_name}: {ann} = dc.field(',
                f'        default=None,',
                f"        metadata={{msh.FieldOptions: msh.FieldOptions(name='_meta')}},",
                f'    )',
            ]

        if field.default is MISSING:
            return [f'    {field.python_name}: {ann}']

        if field.default is None:
            return [f'    {field.python_name}: {ann} = None']

        return [f'    {field.python_name}: {ann} = {field.default!r}']

    def _gen_class_lines(
            self,
            name: str,
            fields: ta.Sequence[FieldDef],
            bases: str = 'lang.Final',
            *,
            tag_field: tuple[str, str] | None = None,
    ) -> list[str]:
        lines: list[str] = [
            '@dc.dataclass(frozen=True, kw_only=True)',
            '@_set_class_marshal_options',
            f'class {name}({bases}):',
        ]

        if not fields and tag_field is None:
            lines.append('    pass')
            return lines

        req = [f for f in fields if f.default is MISSING]
        opt = [f for f in fields if f.default is not MISSING and f.json_name != '_meta']
        meta = [f for f in fields if f.json_name == '_meta']

        for f in req:
            lines.extend(self._gen_field_lines(f))

        if tag_field is not None:
            py_name, value = tag_field
            lines.append(f"    {py_name}: ta.Literal[{value!r}] = dc.xfield({value!r}, repr=False)")

        for f in opt:
            lines.extend(self._gen_field_lines(f))

        for f in meta:
            lines.extend(self._gen_field_lines(f))

        return lines

    #

    class _Writer:
        def __init__(self, out: io.TextIOBase) -> None:
            self.out = out

        def __call__(self, s: str = '') -> None:
            self.out.write(s + '\n')

        def lines(self, ls: ta.Sequence[str]) -> None:
            for l in ls:  # noqa: E741
                self(l)

        def sep(self) -> None:
            self()
            self()
            self('##')

    def _write_header(self, w: _Writer) -> None:
        w('# @omlish-generated')
        w('# ruff: noqa: UP007')
        w('import typing as ta')
        w()
        w('from omlish import dataclasses as dc')
        w('from omlish import lang')
        w('from omlish import marshal as msh')
        w()
        w()
        w('##')
        w()
        w()
        w('def _set_class_marshal_options(cls):')
        w('    msh.update_object_options(')
        w('        cls,')
        w('        field_naming=msh.Naming.LOW_CAMEL,')
        w('        field_defaults=msh.FieldOptions(')
        w('            omit_if=lang.is_none,')
        w('        ),')
        w('    )')
        w('    return cls')

    def _write_discriminated_union_base_classes(self, w: _Writer) -> None:
        if self._disc_unions:
            w.sep()
            for name in sorted(self._disc_unions):
                w()
                w()
                w(f'class {name}(lang.Abstract, lang.Sealed):')
                w('    pass')

    def _write_object_types(self, w: _Writer) -> None:
        objects = sorted(
            (n, td)
            for n, td in self._type_defs.items()
            if isinstance(td, ObjectTypeDef)
        )
        if objects:
            w.sep()
            for name, td in objects:
                w()
                w()
                w.lines(self._gen_class_lines(name, td.fields))

    def _write_empties(self, w: _Writer) -> None:
        empties = sorted(
            (n, td)
            for n, td in self._type_defs.items()
            if isinstance(td, EmptyTypeDef)
        )
        if empties:
            w.sep()
            for name, td in empties:
                w()
                w()
                w('@dc.dataclass(frozen=True, kw_only=True)')
                w('@_set_class_marshal_options')
                w(f'class {name}(lang.Final):')
                w('    pass')

    def _write_variant_wrapper_types(self, w: _Writer) -> None:
        if self._variant_wrappers:
            w.sep()
            for vw in sorted(self._variant_wrappers, key=lambda v: v.class_name):
                w()
                w()
                w.lines(self._gen_class_lines(
                    vw.class_name,
                    vw.source_fields,
                    f'{vw.union_name}, lang.Final',
                    tag_field=(vw.tag_field_python, vw.tag_value),
                ))

    def _write_type_aliases(self, w: _Writer) -> None:
        # Emitted after object types so unquoted refs resolve
        aliases = sorted(
            (n, td)
            for n, td in self._type_defs.items()
            if isinstance(td, TypeAliasTypeDef)
        )
        if aliases:
            w.sep()
            for name, td in aliases:
                w()
                w()
                if td.target is not None:
                    w(f'{name}: ta.TypeAlias = {self._render_type_ann(td.target, quote_refs=False)}')
                else:
                    w(f'{name}: ta.TypeAlias = ta.Any')

    def _write_string_enum_type_aliases(self, w: _Writer) -> None:
        enums = sorted(
            (n, td)
            for n, td in self._type_defs.items()
            if isinstance(td, StringEnumTypeDef)
        )
        if enums:
            w.sep()
            for name, td in enums:
                w()
                w()
                vals_str = ', '.join(f'{v!r}' for v in td.values)
                line = f'{name}: ta.TypeAlias = ta.Literal[{vals_str}]'
                if len(line) <= 120:
                    w(line)
                else:
                    w(f'{name}: ta.TypeAlias = ta.Literal[')
                    for v in td.values:
                        w(f'    {v!r},')
                    w(']')

    def _write_any_of_union_type_aliases(self, w: _Writer) -> None:
        unions = sorted(
            (n, td)
            for n, td in self._type_defs.items()
            if isinstance(td, AnyOfUnionTypeDef)
        )
        if unions:
            w.sep()
            for name, td in unions:
                w()
                w()
                # Unions of multiple complex types can't be marshaled without explicit polymorphism registration. Fall
                # back to ta.Any unless all members are primitives.
                all_primitive = all(isinstance(m, PrimitiveTypeRef) for m in td.members)
                if not all_primitive:
                    w(f'{name}: ta.TypeAlias = ta.Any')
                else:
                    parts = ', '.join(self._render_type_ann(m, quote_refs=False) for m in td.members)
                    line = f'{name}: ta.TypeAlias = ta.Union[{parts}]'
                    if len(line) <= 120:
                        w(line)
                    else:
                        w(f'{name}: ta.TypeAlias = ta.Union[')
                        for m in td.members:
                            w(f'    {self._render_type_ann(m, quote_refs=False)},')
                        w(']')

    def _write_polymorphism_registration(self, w: _Writer) -> None:
        if self._disc_unions:
            w.sep()
            w()
            w()
            w('@lang.static_init')
            w('def _install_marshaling() -> None:')
            items = sorted(self._disc_unions.items())
            for i, (union_name, union_td) in enumerate(items):
                w(f'    msh.install_standard_factories(*msh.standard_polymorphism_factories(')
                w(f'        msh.polymorphism_from_subclasses(')
                w(f'            {union_name},')
                w(f'            naming=msh.Naming.SNAKE,')
                w(f'            strip_suffix=msh.AutoStripSuffix,')
                w(f'        ),')
                w(f"        msh.FieldTypeTagging({union_td.discriminator_field!r}),")
                w(f'    ))')
                if i < len(items) - 1:
                    w()

    def gen_module(self) -> str:
        out = io.StringIO()
        w = self._Writer(out)

        self._write_header(w)
        self._write_discriminated_union_base_classes(w)
        self._write_object_types(w)
        self._write_empties(w)
        self._write_variant_wrapper_types(w)
        self._write_type_aliases(w)
        self._write_string_enum_type_aliases(w)
        self._write_any_of_union_type_aliases(w)
        self._write_polymorphism_registration(w)

        return out.getvalue()
