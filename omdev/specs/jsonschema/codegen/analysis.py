import typing as ta

from omcore import check
from omcore.specs import jsonschema as jsch

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
from .ir import LiteralTypeRef
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
from .names import tag_to_camel


##


JSON_TYPE_MAP: ta.Mapping[str, str] = {
    'string': 'str',
    'integer': 'int',
    'number': 'float',
    'boolean': 'bool',
}

LITERAL_VALUE_TYPES: tuple[type, ...] = (
    str,
    int,
    float,
    bool,
    type(None),
)


class JsonSchemaAnalyzer:
    def __init__(
            self,
            defs: jsch.Keywords | ta.Mapping[str, jsch.Keywords],
            *,
            config: JsonSchemaCodeGenConfig | None = None,
    ) -> None:
        super().__init__()

        if isinstance(defs, jsch.Keywords):
            defs = defs[jsch.Defs].m

        self._defs = dict(defs)
        self._extra_type_defs: dict[str, TypeDef] = {}
        self._config = config if config is not None else JsonSchemaCodeGenConfig()

    ##

    def analyze(self) -> dict[str, TypeDef]:
        type_defs: dict[str, TypeDef] = {}
        for name, kws in self._defs.items():
            class_name = python_class_name(name)
            type_defs[class_name] = self._classify_def(class_name, kws, ('$defs', name))

        for name, type_def in self._extra_type_defs.items():
            if name in type_defs:
                raise UnsupportedSchemaError(message=f'Duplicate generated type name {name!r}')
            type_defs[name] = type_def

        return type_defs

    ##

    def _add_extra_type_def(self, name: str, type_def: TypeDef, path: SchemaPath) -> None:
        if name in self._extra_type_defs:
            raise UnsupportedSchemaError(message=f'Duplicate generated type name {name!r}', path=path)
        self._extra_type_defs[name] = type_def

    def _check_unhandled(
            self,
            kws: jsch.Keywords,
            *,
            handled_types: ta.AbstractSet[type[jsch.Keyword]] = frozenset(),
            path: SchemaPath,
    ) -> None:
        if self._config.non_strict:
            return

        allowed_types = handled_types | self._config.ignored_keyword_types
        for kw in kws.lst:
            if isinstance(kw, jsch.UnknownKeyword):
                if (
                        (not self._config.forbid_unknown_x and kw.tag.startswith('x-')) or
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

    def _has_only_ignored_keywords(self, kws: jsch.Keywords) -> bool:
        if not kws.lst:
            return False

        for kw in kws.lst:
            if isinstance(kw, jsch.UnknownKeyword):
                if (
                        (not self._config.forbid_unknown_x and kw.tag.startswith('x-')) or
                        kw.tag in self._config.allowed_unknown_tags
                ):
                    continue
                return False

            elif type(kw) not in self._config.ignored_keyword_types:
                return False

        return True

    @staticmethod
    def _is_string_const_one_of(one_of: jsch.OneOf) -> bool:
        if not one_of.kws:
            return False
        for m in one_of.kws:
            if jsch.Const not in m.by_type:
                return False
            type_kw = m.by_type.get(jsch.Type)
            if type_kw is None or type_kw.ss != 'string':
                return False
        return True

    def _string_enum_values(self, values: ta.Sequence[ta.Any], path: SchemaPath) -> tuple[str, ...]:
        literals = self._literal_values(values, path)
        if not all(isinstance(v, str) for v in literals):
            raise UnsupportedSchemaError(message='Unsupported non-string enum', path=path)
        return literals

    def _any_fallback(self, message: str, path: SchemaPath) -> AnyTypeRef:
        if self._config.allow_any_fallbacks:
            return AnyTypeRef()

        raise UnsupportedSchemaError(message=message, path=path)

    def _ref_name(self, ref_str: str, path: SchemaPath) -> str:
        try:
            return ref_name(ref_str)
        except ValueError:
            raise UnsupportedSchemaError(message=f'Unsupported JSON Schema ref {ref_str!r}', path=path) from None

    ##

    def _literal_value(self, value: ta.Any, path: SchemaPath) -> ta.Any:
        if not isinstance(value, LITERAL_VALUE_TYPES):
            raise UnsupportedSchemaError(message=f'Unsupported literal value {value!r}', path=path)
        return value

    def _literal_values(self, values: ta.Sequence[ta.Any], path: SchemaPath) -> tuple[ta.Any, ...]:
        if not values:
            raise UnsupportedSchemaError(message='Unsupported empty enum', path=path)

        literals = tuple(self._literal_value(v, path) for v in values)
        value_types = {type(v) for v in literals}
        if len(value_types) > 1:
            raise UnsupportedSchemaError(message='Unsupported mixed-type enum', path=path)

        return literals

    ##

    def _build_def_candidates(self, name: str, kws: jsch.Keywords, path: SchemaPath) -> list[str]:
        by_type = kws.by_type
        by_tag = kws.by_tag

        candidates: list[str] = []

        if by_tag.get('discriminator') is not None and jsch.OneOf in by_type:
            candidates.append('discriminated_union')

        if (
                not candidates and
                (one_of_kw := by_type.get(jsch.OneOf)) is not None and
                self._is_string_const_one_of(one_of_kw)
        ):
            candidates.append('string_const_one_of')

        if not candidates and jsch.Enum in by_type:
            candidates.append('enum')

        if not candidates and (props_kw := by_type.get(jsch.Properties)) is not None:
            addl_kw = by_type.get(jsch.AdditionalProperties)
            if props_kw.m or addl_kw is None or addl_kw.bk is False:
                candidates.append('object')

        if not candidates and jsch.AnyOf in by_type:
            candidates.append('any_of')

        if not candidates and jsch.AllOf in by_type:
            candidates.append('all_of')

        if not candidates and jsch.Ref in by_type:
            candidates.append('ref_alias')

        if jsch.Type in by_type and not candidates:
            candidates.append('type_alias')

        return candidates

    def _classify_def(self, name: str, kws: jsch.Keywords, path: SchemaPath) -> TypeDef:
        by_type = kws.by_type
        by_tag = kws.by_tag

        candidates = self._build_def_candidates(name, kws, path)

        if len(candidates) > 1:
            raise AmbiguousSchemaError(
                message=f'Ambiguous JSON Schema definition {name!r}: {candidates!r}',
                path=path,
            )

        if not candidates:
            self._check_unhandled(kws, path=path)
            return EmptyTypeDef(name=name)

        #

        [candidate] = candidates

        if candidate == 'discriminated_union':
            return self._classify_disc_union(
                name,
                kws,
                check.isinstance(by_tag['discriminator'], jsch.UnknownKeyword),
                path,
            )

        if candidate == 'string_const_one_of':
            one_of_kw = check.isinstance(by_type[jsch.OneOf], jsch.OneOf)
            self._check_unhandled(kws, handled_types={jsch.OneOf}, path=path)
            values = [
                *self._string_enum_values([
                    m[jsch.Const].v
                    for m in one_of_kw.kws
                ], path),
            ]
            return StringEnumTypeDef(name=name, values=values)

        if candidate == 'enum':
            enum_kw = check.isinstance(by_type[jsch.Enum], jsch.Enum)
            self._check_unhandled(kws, handled_types={jsch.Enum, jsch.Type}, path=path)
            return StringEnumTypeDef(name=name, values=self._string_enum_values(enum_kw.vs, path))

        if candidate == 'object':
            return self._classify_object(name, kws, path)

        if candidate == 'any_of':
            return self._classify_any_of(name, check.isinstance(by_type[jsch.AnyOf], jsch.AnyOf), path)

        if candidate == 'type_alias':
            type_kw = check.isinstance(by_type[jsch.Type], jsch.Type)
            target = self._resolve_type_from_type_kw(type_kw, kws, path)
            self._check_unhandled(
                kws,
                handled_types={
                    jsch.Type,
                    jsch.Items,
                    jsch.AdditionalProperties,
                },
                path=path,
            )
            return TypeAliasTypeDef(name=name, target=target)

        if candidate == 'ref_alias':
            target = self._resolve_field_type(kws, path)
            return TypeAliasTypeDef(name=name, target=target)

        if candidate == 'all_of':
            return self._classify_all_of(name, check.isinstance(by_type[jsch.AllOf], jsch.AllOf), path)

        raise TypeError(candidate)

    #

    def _classify_disc_union(
            self,
            name: str,
            kws: jsch.Keywords,
            disc_kw: jsch.UnknownKeyword,
            path: SchemaPath,
    ) -> DiscriminatedUnionTypeDef:
        if not isinstance(disc_kw.value, ta.Mapping):
            raise UnsupportedSchemaError(message='Unsupported discriminator shape', path=path)

        disc_value = disc_kw.value
        prop_name_obj = disc_value.get('propertyName')
        if not isinstance(prop_name_obj, str):
            raise UnsupportedSchemaError(message='Unsupported discriminator propertyName', path=path)
        prop_name = prop_name_obj

        one_of = kws.by_type[jsch.OneOf]

        variants: list[DiscriminatedUnionVariant] = []
        for i, variant_kws in enumerate(one_of.kws):
            v_path = (*path, 'oneOf', i)
            props = variant_kws.by_type.get(jsch.Properties)
            if props is None or prop_name not in props.m:
                raise UnsupportedSchemaError(
                    message=f'Discriminator property {prop_name!r} missing from variant',
                    path=v_path,
                )

            tag_kws = props.m[prop_name]
            const_kw = tag_kws.by_type.get(jsch.Const)
            if const_kw is None:
                raise UnsupportedSchemaError(
                    message=f'Discriminator property {prop_name!r} variant lacks const',
                    path=(*v_path, 'properties', prop_name),
                )

            ref_name_str: str | None = None
            all_of = variant_kws.by_type.get(jsch.AllOf)
            if all_of is not None:
                if len(all_of.kws) != 1:
                    raise UnsupportedSchemaError(message='Unsupported discriminator allOf variant', path=v_path)
                ref_kw = all_of.kws[0].by_type.get(jsch.Ref)
                if ref_kw is None:
                    raise UnsupportedSchemaError(message='Unsupported discriminator allOf variant', path=v_path)
                ref_name_str = python_class_name(self._ref_name(ref_kw.s, (*v_path, 'allOf', 0)))

            self._check_unhandled(
                variant_kws,
                handled_types={
                    jsch.Type,
                    jsch.Properties,
                    jsch.Required,
                    jsch.AllOf,
                },
                path=v_path,
            )
            self._check_unhandled(
                tag_kws,
                handled_types={jsch.Const, jsch.Type},
                path=(*v_path, 'properties', prop_name),
            )

            tag_value = self._literal_value(const_kw.v, (*v_path, 'properties', prop_name))
            if not isinstance(tag_value, str):
                raise UnsupportedSchemaError(
                    message=f'Discriminator property {prop_name!r} const must be string',
                    path=(*v_path, 'properties', prop_name),
                )

            variants.append(DiscriminatedUnionVariant(
                tag_value=tag_value,
                ref_name=ref_name_str,
            ))

        self._check_unhandled(
            kws,
            handled_types={
                jsch.Type,
                jsch.Properties,
                jsch.Required,
                jsch.OneOf,
                jsch.AdditionalProperties,
            },
            path=path,
        )

        return DiscriminatedUnionTypeDef(
            name=name,
            discriminator_field=prop_name,
            variants=variants,
        )

    #

    def _classify_object(
            self,
            name: str,
            kws: jsch.Keywords,
            path: SchemaPath,
            *,
            qual_name: str | None = None,
            extra_handled_types: ta.AbstractSet[type[jsch.Keyword]] = frozenset(),
    ) -> ObjectTypeDef:
        if qual_name is None:
            qual_name = name

        props = kws.by_type[jsch.Properties]
        addl_kw = kws.by_type.get(jsch.AdditionalProperties)
        ignore_unknown = False
        if props.m and addl_kw is not None and addl_kw.bk is not False:
            if not (
                    addl_kw.bk is True or
                    (isinstance(addl_kw.bk, jsch.Keywords) and not addl_kw.bk.lst)
            ):
                raise UnsupportedSchemaError(
                    message='Unsupported additionalProperties with declared properties',
                    path=path,
                )
            ignore_unknown = True

        req_kw = kws.by_type.get(jsch.Required)
        required_names: ta.AbstractSet[str]
        if req_kw is not None:
            required_seq = (req_kw.ss,) if isinstance(req_kw.ss, str) else tuple(req_kw.ss)
            required_names = set(required_seq)
            if len(required_names) != len(required_seq):
                raise UnsupportedSchemaError(message='Duplicate required property', path=path)

            missing_required_names = required_names.difference(props.m)
            if missing_required_names:
                raise UnsupportedSchemaError(
                    message=f'Required properties missing from properties: {sorted(missing_required_names)!r}',
                    path=path,
                )
        else:
            required_names = frozenset()

        fields: list[FieldDef] = []
        nested_defs: list[ObjectTypeDef] = []
        for json_name, field_kws in props.m.items():
            field, field_nested_defs = self._classify_field(
                json_name,
                field_kws,
                json_name in required_names,
                (*path, 'properties', json_name),
                qual_name=qual_name,
            )
            fields.append(field)
            nested_defs.extend(field_nested_defs)

        seen_python_names: set[str] = set()
        for field in fields:
            if field.python_name in seen_python_names:
                raise UnsupportedSchemaError(
                    message=f'Duplicate Python field name {field.python_name!r}',
                    path=path,
                )
            seen_python_names.add(field.python_name)

        seen_nested_names: set[str] = set()
        for nested_def in nested_defs:
            if nested_def.name in seen_nested_names:
                raise UnsupportedSchemaError(
                    message=f'Duplicate nested class name {nested_def.name!r}',
                    path=path,
                )
            seen_nested_names.add(nested_def.name)

        self._check_unhandled(
            kws,
            handled_types={
                jsch.Type,
                jsch.Properties,
                jsch.Required,
                jsch.AdditionalProperties,
            } | extra_handled_types,
            path=path,
        )

        naming = infer_naming(props.m)
        return ObjectTypeDef(
            name=name,
            fields=fields,
            nested_defs=nested_defs,
            field_naming=naming.name if naming is not None else None,
            ignore_unknown=ignore_unknown,
        )

    #

    def _classify_field(
            self,
            json_name: str,
            kws: jsch.Keywords,
            required: bool,
            path: SchemaPath,
            *,
            qual_name: str,
    ) -> tuple[FieldDef, ta.Sequence[ObjectTypeDef]]:
        python_name = python_field_name(json_name)
        nested_defs: list[ObjectTypeDef] = []
        type_ref: TypeRef

        addl_kw = kws.by_type.get(jsch.AdditionalProperties)
        items_kw = kws.by_type.get(jsch.Items)
        if (
                addl_kw is not None and
                isinstance(addl_kw.bk, jsch.Keywords) and
                (addl_props := addl_kw.bk.by_type.get(jsch.Properties)) is not None and
                addl_props.m
        ):
            nested_name = python_class_name(json_name) + 'Value'
            nested_qual_name = f'{qual_name}.{nested_name}'
            nested_defs.append(self._classify_object(
                nested_name,
                addl_kw.bk,
                (*path, 'additionalProperties'),
                qual_name=nested_qual_name,
            ))
            type_ref = MapTypeRef(value=RefTypeRef(nested_qual_name))
            self._check_unhandled(
                kws,
                handled_types={
                    jsch.Type,
                    jsch.AdditionalProperties,
                    jsch.Default,
                },
                path=path,
            )

        elif (
                items_kw is not None and
                (item_props := items_kw.kw.by_type.get(jsch.Properties)) is not None and
                item_props.m
        ):
            nested_name = python_class_name(json_name) + 'Item'
            nested_qual_name = f'{qual_name}.{nested_name}'
            nested_defs.append(self._classify_object(
                nested_name,
                items_kw.kw,
                (*path, 'items'),
                qual_name=nested_qual_name,
            ))
            type_ref = ArrayTypeRef(item=RefTypeRef(nested_qual_name))
            self._check_unhandled(
                kws,
                handled_types={
                    jsch.Type,
                    jsch.Items,
                    jsch.Default,
                },
                path=path,
            )

        elif (props_kw := kws.by_type.get(jsch.Properties)) is not None and props_kw.m:
            nested_name = python_class_name(json_name)
            nested_qual_name = f'{qual_name}.{nested_name}'
            nested_defs.append(self._classify_object(nested_name, kws, path, qual_name=nested_qual_name))
            type_ref = RefTypeRef(nested_qual_name)

        else:
            type_ref = self._resolve_field_type(kws, path)

        const_kw = kws.by_type.get(jsch.Const)
        const: ta.Any = MISSING
        if const_kw is not None:
            const = self._literal_value(const_kw.v, path)

        default: ta.Any = MISSING
        default_kw = kws.by_type.get(jsch.Default)
        if default_kw is not None:
            dv = default_kw.v
            if not isinstance(dv, LITERAL_VALUE_TYPES):
                if not isinstance(type_ref, NullableTypeRef):
                    type_ref = NullableTypeRef(inner=type_ref)
                default = None
            else:
                default = dv

        if const is not MISSING and default is not MISSING and const != default:
            raise UnsupportedSchemaError(message='Const and default disagree', path=path)

        if not required and default is MISSING:
            if not isinstance(type_ref, NullableTypeRef):
                type_ref = NullableTypeRef(inner=type_ref)
            default = None

        return (
            FieldDef(
                json_name=json_name,
                python_name=python_name,
                type_ref=type_ref,
                required=required,
                default=default,
                const=const,
            ),
            tuple(nested_defs),
        )

    #

    @staticmethod
    def _any_of_member_name(owner_name: str, kws: jsch.Keywords, index: int) -> str:
        title_kw = kws.by_type.get(jsch.Title)
        if title_kw is not None:
            return python_class_name(f'{owner_name}_{title_kw.s}')

        props_kw = kws.by_type.get(jsch.Properties)
        if props_kw is not None:
            type_kws = props_kw.m.get('type')
            if type_kws is not None:
                const_kw = type_kws.by_type.get(jsch.Const)
                if const_kw is not None and isinstance(const_kw.v, str):
                    return tag_to_camel(const_kw.v) + owner_name

        return python_class_name(f'{owner_name}_Member{index}')

    def _resolve_any_of_member_type(
            self,
            kws: jsch.Keywords,
            path: SchemaPath,
            *,
            owner_name: str | None = None,
            index: int | None = None,
    ) -> TypeRef:
        if jsch.Properties in kws.by_type:
            if owner_name is not None and index is not None:
                member_name = self._any_of_member_name(owner_name, kws, index)
                if (all_of := kws.by_type.get(jsch.AllOf)) is not None:
                    members: list[TypeDef | TypeRef] = []
                    for i, member_kws in enumerate(all_of.kws):
                        member_path = (*path, 'allOf', i)
                        if member_kws.by_type.get(jsch.Ref) is not None:
                            members.append(self._resolve_field_type(member_kws, member_path))
                        else:
                            raise UnsupportedSchemaError(message='Unsupported allOf member', path=member_path)
                    members.append(self._classify_object(
                        member_name,
                        kws,
                        path,
                        qual_name=member_name,
                        extra_handled_types={jsch.AllOf},
                    ))
                    self._add_extra_type_def(
                        member_name,
                        AllOfIntersectionTypeDef(name=member_name, members=members),
                        path,
                    )
                else:
                    self._add_extra_type_def(
                        member_name,
                        self._classify_object(member_name, kws, path, qual_name=member_name),
                        path,
                    )
                return RefTypeRef(member_name)

            self._check_unhandled(
                kws,
                handled_types={
                    jsch.Type,
                    jsch.Properties,
                    jsch.Required,
                    jsch.AdditionalProperties,
                    jsch.AllOf,
                },
                path=path,
            )
            return self._any_fallback('Unsupported object anyOf member', path)

        return self._resolve_field_type(kws, path)

    def _classify_any_of(self, name: str, any_of: jsch.AnyOf, path: SchemaPath) -> TypeDef:
        all_const = all(jsch.Const in m.by_type for m in any_of.kws)
        if all_const:
            types = set()
            for m in any_of.kws:
                type_kw = m.by_type.get(jsch.Type)
                if type_kw and isinstance(type_kw.ss, str):
                    types.add(type_kw.ss)
            if len(types) == 1:
                t = types.pop()
                if t in JSON_TYPE_MAP:
                    return TypeAliasTypeDef(name=name, target=PrimitiveTypeRef(JSON_TYPE_MAP[t]))

        non_const = [m for m in any_of.kws if jsch.Const not in m.by_type]
        if non_const and len(non_const) < len(any_of.kws):
            members = [
                self._resolve_any_of_member_type(m, (*path, 'anyOf', i), owner_name=name, index=i)
                for i, m in enumerate(non_const)
            ]
            if len(members) == 1:
                return TypeAliasTypeDef(name=name, target=members[0])
            return AnyOfUnionTypeDef(name=name, members=members)

        members = [
            self._resolve_any_of_member_type(m, (*path, 'anyOf', i), owner_name=name, index=i)
            for i, m in enumerate(any_of.kws)
        ]
        if len(members) == 1:
            return TypeAliasTypeDef(name=name, target=members[0])

        return AnyOfUnionTypeDef(name=name, members=members)

    #

    def _classify_all_of(self, name: str, all_of: jsch.AllOf, path: SchemaPath) -> TypeDef:
        members: list[TypeDef | TypeRef] = []

        for i, kws in enumerate(all_of.kws):
            by_type = kws.by_type
            m_path = (*path, 'allOf', i)

            if by_type.get(jsch.Properties) is not None:
                members.append(self._classify_object(name, kws, m_path, qual_name=name))

            elif by_type.get(jsch.Ref) is not None:
                members.append(self._resolve_field_type(kws, m_path))

            else:
                raise UnsupportedSchemaError(message='Unsupported allOf member', path=m_path)

        return AllOfIntersectionTypeDef(name=name, members=members)

    ##

    def _resolve_any_of_type(self, any_of: jsch.AnyOf, path: SchemaPath) -> TypeRef:
        refs: list[TypeRef] = []
        has_null = False

        for i, m in enumerate(any_of.kws):
            type_kw = m.by_type.get(jsch.Type)
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

    def _resolve_type_from_type_kw(self, type_kw: jsch.Type, kws: jsch.Keywords, path: SchemaPath) -> TypeRef:
        ss = type_kw.ss
        items_kw = kws.by_type.get(jsch.Items)

        self._check_unhandled(
            kws,
            handled_types={
                jsch.Type,
                jsch.Items,
                jsch.AdditionalProperties,
                jsch.Default,
                jsch.Const,
                jsch.Properties,
            },
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
            kws: jsch.Keywords,
            items_kw: jsch.Items | None,
            path: SchemaPath,
    ) -> TypeRef:
        if type_str in JSON_TYPE_MAP:
            return PrimitiveTypeRef(JSON_TYPE_MAP[type_str])

        if type_str == 'object':
            props = kws.by_type.get(jsch.Properties)
            if props is not None and props.m:
                raise UnsupportedSchemaError(message='Unsupported inline object type', path=path)

            addl = kws.by_type.get(jsch.AdditionalProperties)
            if addl is not None and isinstance(addl.bk, jsch.Keywords):
                return MapTypeRef(value=self._resolve_field_type(addl.bk, (*path, 'additionalProperties')))
            return MapTypeRef()

        if type_str == 'array':
            if items_kw is not None:
                return ArrayTypeRef(item=self._resolve_field_type(items_kw.kw, (*path, 'items')))
            return ArrayTypeRef(item=AnyTypeRef())

        if type_str == 'null':
            return PrimitiveTypeRef('None')

        raise UnsupportedSchemaError(message=f'Unsupported JSON Schema type {type_str!r}', path=path)

    def _resolve_field_type(self, kws: jsch.Keywords, path: SchemaPath) -> TypeRef:
        by_type = kws.by_type

        all_of = by_type.get(jsch.AllOf)
        if all_of is not None and len(all_of.kws) == 1:
            ref_kw = all_of.kws[0].by_type.get(jsch.Ref)
            if ref_kw is not None:
                self._check_unhandled(kws, handled_types={jsch.AllOf, jsch.Default}, path=path)
                return RefTypeRef(python_class_name(self._ref_name(ref_kw.s, (*path, 'allOf', 0))))

        ref_kw = by_type.get(jsch.Ref)
        if ref_kw is not None:
            self._check_unhandled(kws, handled_types={jsch.Ref, jsch.Default}, path=path)
            return RefTypeRef(python_class_name(self._ref_name(ref_kw.s, path)))

        enum_kw = by_type.get(jsch.Enum)
        if enum_kw is not None:
            self._check_unhandled(kws, handled_types={jsch.Type, jsch.Enum, jsch.Default}, path=path)
            return LiteralTypeRef(self._literal_values(enum_kw.vs, path))

        any_of = by_type.get(jsch.AnyOf)
        if any_of is not None:
            self._check_unhandled(kws, handled_types={jsch.AnyOf, jsch.Default}, path=path)
            return self._resolve_any_of_type(any_of, path)

        type_kw = by_type.get(jsch.Type)
        if type_kw is not None:
            return self._resolve_type_from_type_kw(type_kw, kws, path)

        if not kws.lst:
            return AnyTypeRef()

        if self._has_only_ignored_keywords(kws):
            return AnyTypeRef()

        if self._config.allow_any_fallbacks:
            return AnyTypeRef()

        self._check_unhandled(kws, handled_types={jsch.Default}, path=path)
        return self._any_fallback('Unsupported unconstrained non-empty schema', path)
