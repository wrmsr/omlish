import typing as ta

from omlish import check
from omlish.specs import jsonschema as js

from .config import JsonSchemaCodeGenConfig
from .errors import AmbiguousSchemaError
from .errors import SchemaPath
from .errors import UnsupportedSchemaError
from .ir import MISSING
from .ir import AllOfIntersectionTypeDef
from .ir import AnyOfUnionTypeDef
from .ir import AnyTypeRef
from .ir import ArrayTypeRef
from .ir import DiscriminatedUnionTypeDef
from .ir import DiscriminatedUnionVariant
from .ir import EmptyTypeDef
from .ir import FieldDef
from .ir import MapTypeRef
from .ir import NullableTypeRef
from .ir import ObjectTypeDef
from .ir import PrimitiveTypeRef
from .ir import RefTypeRef
from .ir import StringEnumTypeDef
from .ir import TypeAliasTypeDef
from .ir import TypeDef
from .ir import TypeRef
from .ir import UnionTypeRef
from .names import infer_naming
from .names import python_class_name
from .names import python_field_name
from .names import ref_name


##


JSON_TYPE_MAP: ta.Mapping[str, str] = {
    'string': 'str',
    'integer': 'int',
    'number': 'float',
    'boolean': 'bool',
}


class JsonSchemaAnalyzer:
    def __init__(
            self,
            defs: js.Keywords | ta.Mapping[str, js.Keywords],
            *,
            config: JsonSchemaCodeGenConfig | None = None,
    ) -> None:
        super().__init__()

        if isinstance(defs, js.Keywords):
            defs = defs[js.Defs].m

        self._defs = dict(defs)
        self._config = config if config is not None else JsonSchemaCodeGenConfig()

    def analyze(self) -> dict[str, TypeDef]:
        type_defs: dict[str, TypeDef] = {}
        for name, kws in self._defs.items():
            class_name = python_class_name(name)
            type_defs[class_name] = self._classify_def(class_name, kws, ('$defs', name))
        return type_defs

    def _check_unhandled(
            self,
            kws: js.Keywords,
            *,
            handled_types: ta.AbstractSet[type[js.Keyword]] = frozenset(),
            path: SchemaPath,
    ) -> None:
        if not self._config.strict:
            return

        allowed_types = handled_types | self._config.ignored_keyword_types
        for kw in kws.lst:
            if isinstance(kw, js.UnknownKeyword):
                if (
                        (self._config.allow_unknown_x and kw.tag.startswith('x-')) or
                        kw.tag in self._config.allowed_unknown_tags
                ):
                    continue
                raise UnsupportedSchemaError(
                    message=f'Unsupported unknown JSON Schema keyword {kw.tag!r}',
                    path=path,
                )

            if type(kw) not in allowed_types:
                raise UnsupportedSchemaError(
                    message=f'Unsupported JSON Schema keyword {kw.tag!r}',
                    path=path,
                )

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

    def _classify_def(self, name: str, kws: js.Keywords, path: SchemaPath) -> TypeDef:
        by_type = kws.by_type
        by_tag = kws.by_tag

        candidates: list[str] = []
        if by_tag.get('discriminator') is not None and js.OneOf in by_type:
            candidates.append('discriminated_union')
        if (
                not candidates and
                (one_of_kw := by_type.get(js.OneOf)) is not None and
                self._is_string_const_one_of(one_of_kw)
        ):
            candidates.append('string_const_one_of')
        if not candidates and js.Enum in by_type:
            candidates.append('enum')
        if not candidates and js.Properties in by_type:
            candidates.append('object')
        if not candidates and js.AnyOf in by_type:
            candidates.append('any_of')
        if not candidates and js.AllOf in by_type:
            candidates.append('all_of')
        if js.Type in by_type and not candidates:
            candidates.append('type_alias')

        if len(candidates) > 1:
            raise AmbiguousSchemaError(
                message=f'Ambiguous JSON Schema definition {name!r}: {candidates!r}',
                path=path,
            )

        if not candidates:
            self._check_unhandled(kws, path=path)
            return EmptyTypeDef(name=name)

        [candidate] = candidates

        if candidate == 'discriminated_union':
            return self._classify_disc_union(
                name,
                kws,
                check.isinstance(by_tag['discriminator'], js.UnknownKeyword),
                path,
            )

        if candidate == 'string_const_one_of':
            one_of_kw = check.isinstance(by_type[js.OneOf], js.OneOf)
            self._check_unhandled(kws, handled_types={js.OneOf}, path=path)
            values = [check.isinstance(m[js.Const].v, str) for m in one_of_kw.kws]
            return StringEnumTypeDef(name=name, values=values)

        if candidate == 'enum':
            enum_kw = check.isinstance(by_type[js.Enum], js.Enum)
            self._check_unhandled(kws, handled_types={js.Enum, js.Type}, path=path)
            return StringEnumTypeDef(name=name, values=[check.isinstance(v, str) for v in enum_kw.vs])

        if candidate == 'object':
            return self._classify_object(name, kws, path)

        if candidate == 'any_of':
            return self._classify_any_of(name, check.isinstance(by_type[js.AnyOf], js.AnyOf), path)

        if candidate == 'type_alias':
            type_kw = check.isinstance(by_type[js.Type], js.Type)
            target = self._resolve_type_from_type_kw(type_kw, kws, path)
            self._check_unhandled(
                kws,
                handled_types={js.Type, js.Items, js.AdditionalProperties},
                path=path,
            )
            return TypeAliasTypeDef(name=name, target=target)

        if candidate == 'all_of':
            return self._classify_all_of(name, check.isinstance(by_type[js.AllOf], js.AllOf), path)

        raise TypeError(candidate)

    def _classify_disc_union(
            self,
            name: str,
            kws: js.Keywords,
            disc_kw: js.UnknownKeyword,
            path: SchemaPath,
    ) -> DiscriminatedUnionTypeDef:
        disc_value = check.isinstance(disc_kw.value, ta.Mapping)
        prop_name = check.isinstance(disc_value['propertyName'], str)
        one_of = kws.by_type[js.OneOf]

        variants: list[DiscriminatedUnionVariant] = []
        for i, variant_kws in enumerate(one_of.kws):
            v_path = (*path, 'oneOf', i)
            props = variant_kws.by_type.get(js.Properties)
            if props is None or prop_name not in props.m:
                raise UnsupportedSchemaError(
                    message=f'Discriminator property {prop_name!r} missing from variant',
                    path=v_path,
                )

            tag_kws = props.m[prop_name]
            const_kw = tag_kws.by_type.get(js.Const)
            if const_kw is None:
                raise UnsupportedSchemaError(
                    message=f'Discriminator property {prop_name!r} variant lacks const',
                    path=(*v_path, 'properties', prop_name),
                )

            ref_name_str: str | None = None
            all_of = variant_kws.by_type.get(js.AllOf)
            if all_of is not None:
                if len(all_of.kws) != 1:
                    raise UnsupportedSchemaError(message='Unsupported discriminator allOf variant', path=v_path)
                ref_kw = all_of.kws[0].by_type.get(js.Ref)
                if ref_kw is None:
                    raise UnsupportedSchemaError(message='Unsupported discriminator allOf variant', path=v_path)
                ref_name_str = python_class_name(ref_name(ref_kw.s))

            self._check_unhandled(
                variant_kws,
                handled_types={js.Type, js.Properties, js.Required, js.AllOf},
                path=v_path,
            )
            self._check_unhandled(
                tag_kws,
                handled_types={js.Const, js.Type},
                path=(*v_path, 'properties', prop_name),
            )

            variants.append(DiscriminatedUnionVariant(
                tag_value=check.isinstance(const_kw.v, str),
                ref_name=ref_name_str,
            ))

        self._check_unhandled(
            kws,
            handled_types={js.Type, js.Properties, js.Required, js.OneOf, js.AdditionalProperties},
            path=path,
        )

        return DiscriminatedUnionTypeDef(
            name=name,
            discriminator_field=prop_name,
            variants=variants,
        )

    def _classify_object(self, name: str, kws: js.Keywords, path: SchemaPath) -> ObjectTypeDef:
        props = kws.by_type[js.Properties]
        req_kw = kws.by_type.get(js.Required)
        required_names: ta.AbstractSet[str]
        if req_kw is not None:
            required_names = {req_kw.ss} if isinstance(req_kw.ss, str) else set(req_kw.ss)
        else:
            required_names = frozenset()

        fields: list[FieldDef] = []
        for json_name, field_kws in props.m.items():
            fields.append(self._classify_field(
                json_name,
                field_kws,
                json_name in required_names,
                (*path, 'properties', json_name),
            ))

        self._check_unhandled(
            kws,
            handled_types={js.Type, js.Properties, js.Required, js.AdditionalProperties},
            path=path,
        )

        naming = infer_naming(props.m)
        return ObjectTypeDef(
            name=name,
            fields=fields,
            field_naming=naming.name if naming is not None else None,
        )

    def _classify_field(
            self,
            json_name: str,
            kws: js.Keywords,
            required: bool,
            path: SchemaPath,
    ) -> FieldDef:
        python_name = python_field_name(json_name)
        type_ref = self._resolve_field_type(kws, path)

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

    def _classify_any_of(self, name: str, any_of: js.AnyOf, path: SchemaPath) -> TypeDef:
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
                    return TypeAliasTypeDef(name=name, target=PrimitiveTypeRef(JSON_TYPE_MAP[t]))

        non_const = [m for m in any_of.kws if js.Const not in m.by_type]
        if non_const and len(non_const) < len(any_of.kws):
            members = [self._resolve_any_of_member_type(m, (*path, 'anyOf', i)) for i, m in enumerate(non_const)]
            if len(members) == 1:
                return TypeAliasTypeDef(name=name, target=members[0])
            return AnyOfUnionTypeDef(name=name, members=members)

        members = [self._resolve_any_of_member_type(m, (*path, 'anyOf', i)) for i, m in enumerate(any_of.kws)]
        if len(members) == 1:
            return TypeAliasTypeDef(name=name, target=members[0])

        return AnyOfUnionTypeDef(name=name, members=members)

    def _resolve_any_of_member_type(self, kws: js.Keywords, path: SchemaPath) -> TypeRef:
        if js.Properties in kws.by_type:
            self._check_unhandled(
                kws,
                handled_types={js.Type, js.Properties, js.Required, js.AdditionalProperties, js.AllOf},
                path=path,
            )
            return AnyTypeRef()

        return self._resolve_field_type(kws, path)

    def _classify_all_of(self, name: str, all_of: js.AllOf, path: SchemaPath) -> TypeDef:
        members: list[TypeDef | TypeRef] = []

        for i, kws in enumerate(all_of.kws):
            by_type = kws.by_type
            m_path = (*path, 'allOf', i)

            if by_type.get(js.Properties) is not None:
                members.append(self._classify_def('?', kws, m_path))

            elif by_type.get(js.Ref) is not None:
                members.append(self._resolve_field_type(kws, m_path))

            else:
                raise UnsupportedSchemaError(message='Unsupported allOf member', path=m_path)

        return AllOfIntersectionTypeDef(name=name, members=members)

    def _resolve_field_type(self, kws: js.Keywords, path: SchemaPath) -> TypeRef:
        by_type = kws.by_type

        all_of = by_type.get(js.AllOf)
        if all_of is not None and len(all_of.kws) == 1:
            ref_kw = all_of.kws[0].by_type.get(js.Ref)
            if ref_kw is not None:
                self._check_unhandled(kws, handled_types={js.AllOf, js.Default}, path=path)
                return RefTypeRef(python_class_name(ref_name(ref_kw.s)))

        ref_kw = by_type.get(js.Ref)
        if ref_kw is not None:
            self._check_unhandled(kws, handled_types={js.Ref, js.Default}, path=path)
            return RefTypeRef(python_class_name(ref_name(ref_kw.s)))

        any_of = by_type.get(js.AnyOf)
        if any_of is not None:
            self._check_unhandled(kws, handled_types={js.AnyOf, js.Default}, path=path)
            return self._resolve_any_of_type(any_of, path)

        type_kw = by_type.get(js.Type)
        if type_kw is not None:
            return self._resolve_type_from_type_kw(type_kw, kws, path)

        if not kws.lst:
            return AnyTypeRef()

        if self._config.allow_any_fallbacks:
            return AnyTypeRef()

        self._check_unhandled(kws, handled_types={js.Default}, path=path)
        return AnyTypeRef()

    def _resolve_any_of_type(self, any_of: js.AnyOf, path: SchemaPath) -> TypeRef:
        refs: list[TypeRef] = []
        has_null = False

        for i, m in enumerate(any_of.kws):
            type_kw = m.by_type.get(js.Type)
            if type_kw is not None and type_kw.ss == 'null':
                has_null = True
                continue
            refs.append(self._resolve_field_type(m, (*path, 'anyOf', i)))

        inner: TypeRef
        if not refs:
            inner = PrimitiveTypeRef('None')
        elif len(refs) == 1:
            inner = refs[0]
        elif not all(isinstance(r, PrimitiveTypeRef) for r in refs):
            inner = AnyTypeRef()
        else:
            inner = UnionTypeRef(members=refs)

        if has_null:
            return NullableTypeRef(inner=inner)
        return inner

    def _resolve_type_from_type_kw(self, type_kw: js.Type, kws: js.Keywords, path: SchemaPath) -> TypeRef:
        ss = type_kw.ss
        items_kw = kws.by_type.get(js.Items)

        self._check_unhandled(
            kws,
            handled_types={js.Type, js.Items, js.AdditionalProperties, js.Default},
            path=path,
        )

        if isinstance(ss, str):
            return self._resolve_single_type(ss, kws, items_kw, path)

        types = list(ss)
        has_null = 'null' in types
        non_null = [t for t in types if t != 'null']

        inner: TypeRef
        if not non_null:
            inner = PrimitiveTypeRef('None')
        elif len(non_null) == 1:
            inner = self._resolve_single_type(non_null[0], kws, items_kw, path)
        else:
            inner = UnionTypeRef(members=[
                self._resolve_single_type(t, kws, items_kw, path)
                for t in non_null
            ])

        if has_null:
            return NullableTypeRef(inner=inner)
        return inner

    def _resolve_single_type(
            self,
            type_str: str,
            kws: js.Keywords,
            items_kw: js.Items | None,
            path: SchemaPath,
    ) -> TypeRef:
        if type_str in JSON_TYPE_MAP:
            return PrimitiveTypeRef(JSON_TYPE_MAP[type_str])

        if type_str == 'object':
            addl = kws.by_type.get(js.AdditionalProperties)
            if addl is not None and isinstance(addl.bk, js.Keywords):
                return MapTypeRef(value=self._resolve_field_type(addl.bk, (*path, 'additionalProperties')))
            return MapTypeRef()

        if type_str == 'array':
            if items_kw is not None:
                return ArrayTypeRef(item=self._resolve_field_type(items_kw.kw, (*path, 'items')))
            return ArrayTypeRef(item=AnyTypeRef())

        if type_str == 'null':
            return PrimitiveTypeRef('None')

        raise UnsupportedSchemaError(message=f'Unsupported JSON Schema type {type_str!r}', path=path)
