import typing as ta

from omlish import check

from .errors import UnresolvedRefError
from .ir import TYPE_DEF_TYPES
from .ir import AllOfIntersectionTypeDef
from .ir import DiscriminatedUnionTypeDef
from .ir import FieldDef
from .ir import ModuleDef
from .ir import ObjectTypeDef
from .ir import RefTypeRef
from .ir import TypeDef
from .ir import TypeRef
from .ir import VariantWrapperDef
from .names import python_field_name
from .names import tag_to_camel


##


class JsonSchemaIrTransformer:
    def __init__(self, type_defs: ta.Mapping[str, TypeDef]) -> None:
        super().__init__()

        self._type_defs = dict(type_defs)
        self._disc_unions: dict[str, DiscriminatedUnionTypeDef] = {
            n: td
            for n, td in self._type_defs.items()
            if isinstance(td, DiscriminatedUnionTypeDef)
        }
        self._variant_wrappers: list[VariantWrapperDef] = []

    def transform(self) -> ModuleDef:
        self._build_intersection_types()
        self._build_variant_wrappers()

        return ModuleDef(
            type_defs=self._type_defs,
            disc_unions=self._disc_unions,
            variant_wrappers=self._variant_wrappers,
        )

    def _build_variant_wrappers(self) -> None:
        for union_name, union_td in self._disc_unions.items():
            tag_json = union_td.discriminator_field
            tag_python = python_field_name(tag_json)

            for variant in union_td.variants:
                wrapper_name = tag_to_camel(variant.tag_value) + union_name

                source_fields: ta.Sequence[FieldDef] = ()
                if variant.ref_name is not None:
                    try:
                        ref_td = self._type_defs[variant.ref_name]
                    except KeyError:
                        raise UnresolvedRefError(message=f'Unresolved ref {variant.ref_name!r}') from None

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

    def _build_intersection_types(self) -> None:
        intersection_type_names = {
            n
            for n, td in self._type_defs.items()
            if isinstance(td, AllOfIntersectionTypeDef)
        }
        if not intersection_type_names:
            return

        def rec(n: str) -> ObjectTypeDef:
            intersection_type_names.remove(n)

            fields: list[FieldDef] = []
            nested_defs: list[ObjectTypeDef] = []
            td = check.isinstance(self._type_defs[n], AllOfIntersectionTypeDef)

            for m in td.members:
                if isinstance(m, TYPE_DEF_TYPES):
                    om = check.isinstance(m, ObjectTypeDef)
                    fields.extend(om.fields)
                    nested_defs.extend(om.nested_defs)

                elif isinstance(m, TypeRef):
                    m = check.isinstance(m, RefTypeRef)

                    try:
                        md = self._type_defs[m.name]
                    except KeyError:
                        raise UnresolvedRefError(message=f'Unresolved ref {m.name!r}') from None

                    if isinstance(md, AllOfIntersectionTypeDef):
                        md = rec(m.name)

                    om = check.isinstance(md, ObjectTypeDef)
                    fields.extend(om.fields)
                    nested_defs.extend(om.nested_defs)

                else:
                    raise TypeError(m)

            otd = ObjectTypeDef(
                name=td.name,
                fields=tuple(fields),
                nested_defs=tuple(nested_defs),
            )

            self._type_defs[n] = otd

            return otd

        while intersection_type_names:
            rec(next(iter(intersection_type_names)))
