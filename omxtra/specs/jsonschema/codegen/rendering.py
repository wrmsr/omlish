import io
import typing as ta

from .config import JsonSchemaCodeGenConfig
from .ir import MISSING
from .ir import AnyOfUnionTypeDef
from .ir import EmptyTypeDef
from .ir import FieldDef
from .ir import ModuleDef
from .ir import ObjectTypeDef
from .ir import PrimitiveTypeRef
from .ir import StringEnumTypeDef
from .ir import TypeAliasTypeDef
from .ir import VariantWrapperDef
from .typing import TypeAnnotationRenderer


##


class ModuleRenderer:
    def __init__(self, *, config: JsonSchemaCodeGenConfig | None = None) -> None:
        super().__init__()

        self._config = config if config is not None else JsonSchemaCodeGenConfig()
        self._types = TypeAnnotationRenderer()

    class _Writer:
        def __init__(self, out: io.TextIOBase) -> None:
            super().__init__()

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

    def render(self, module: ModuleDef) -> str:
        out = io.StringIO()
        w = self._Writer(out)

        self._write_header(w)
        self._write_discriminated_union_base_classes(w, module)
        self._write_object_types(w, module)
        self._write_empties(w, module)
        self._write_variant_wrapper_types(w, module)
        self._write_type_aliases(w, module)
        self._write_string_enum_type_aliases(w, module)
        self._write_any_of_union_type_aliases(w, module)
        self._write_polymorphism_registration(w, module)

        return out.getvalue()

    def _render_type_ann(self, ref, *, quote_refs: bool = True) -> str:
        return self._types.render(ref, quote_refs=quote_refs)

    @staticmethod
    def _indent(level: int) -> str:
        return '    ' * level

    def _gen_field_lines(self, field: FieldDef, *, level: int = 1) -> list[str]:
        ind = self._indent(level)
        ann = self._render_type_ann(field.type_ref)

        if field.const is not MISSING:
            return [
                f'{ind}{field.python_name}: ta.Literal[{field.const!r}] = dc.xfield({field.const!r}, repr=False)',
            ]

        if field.json_name == '_meta':
            return [
                f'{ind}{field.python_name}: {ann} = dc.field(',
                f'{ind}    default=None,',
                f"{ind}    metadata={{msh.FieldOptions: msh.FieldOptions(name='_meta')}},",
                f'{ind})',
            ]

        if field.default is MISSING:
            return [f'{ind}{field.python_name}: {ann}']

        if field.default is None:
            return [f'{ind}{field.python_name}: {ann} = None']

        return [f'{ind}{field.python_name}: {ann} = {field.default!r}']

    def _gen_class_lines(
            self,
            name: str,
            fields: ta.Sequence[FieldDef],
            bases: str = 'lang.Final',
            *,
            nested_defs: ta.Sequence[ObjectTypeDef] = (),
            tag_field: tuple[str, str] | None = None,
            field_naming: str | None = None,
            level: int = 0,
    ) -> list[str]:
        ind = self._indent(level)
        body_ind = self._indent(level + 1)
        lines: list[str] = [
            f'{ind}@dc.dataclass(frozen=True, kw_only=True)',
        ]
        if field_naming is None or field_naming == 'LOW_CAMEL':
            lines.append(f'{ind}@_set_class_marshal_options')
        else:
            lines.append(f'{ind}@_set_class_marshal_options(field_naming=msh.Naming.{field_naming})')
        lines.append(f'{ind}class {name}({bases}):')

        if not nested_defs and not fields and tag_field is None:
            lines.append(f'{body_ind}pass')
            return lines

        for i, nested_def in enumerate(nested_defs):
            if i:
                lines.append('')
            lines.extend(self._gen_class_lines(
                nested_def.name,
                nested_def.fields,
                nested_defs=nested_def.nested_defs,
                field_naming=nested_def.field_naming,
                level=level + 1,
            ))

        if nested_defs and (fields or tag_field is not None):
            lines.append('')

        req = [f for f in fields if f.default is MISSING and f.const is MISSING]
        opt = [f for f in fields if (f.default is not MISSING or f.const is not MISSING) and f.json_name != '_meta']
        meta = [f for f in fields if f.json_name == '_meta']

        for f in req:
            lines.extend(self._gen_field_lines(f, level=level + 1))

        if tag_field is not None:
            py_name, value = tag_field
            lines.append(f'{body_ind}{py_name}: ta.Literal[{value!r}] = dc.xfield({value!r}, repr=False)')

        for f in opt:
            lines.extend(self._gen_field_lines(f, level=level + 1))

        for f in meta:
            lines.extend(self._gen_field_lines(f, level=level + 1))

        return lines

    def _write_header(self, w: _Writer) -> None:
        if self._config.generated_marker:
            w('# @omlish-generated')
        w('# ruff: noqa: UP007 UP037 UP045')
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
        w('def _set_class_marshal_options(cls=None, *, field_naming=msh.Naming.LOW_CAMEL):')
        w('    def inner(c):')
        w('        msh.update_object_options(')
        w('            field_naming=field_naming,')
        w('            field_defaults=msh.FieldOptions(')
        w('                omit_if=lang.is_none,')
        w('            ),')
        w('        )(c)')
        w()
        w('        return c')
        w()
        w('    if cls is not None:')
        w('        return inner(cls)')
        w('    return inner')

    def _write_discriminated_union_base_classes(self, w: _Writer, module: ModuleDef) -> None:
        if module.disc_unions:
            w.sep()
            for name in sorted(module.disc_unions):
                w()
                w()
                w(f'class {name}(lang.Abstract, lang.Sealed):')
                w('    pass')

    def _write_object_types(self, w: _Writer, module: ModuleDef) -> None:
        objects = sorted(
            (n, td)
            for n, td in module.type_defs.items()
            if isinstance(td, ObjectTypeDef)
        )
        if objects:
            w.sep()
            for name, td in objects:
                w()
                w()
                w.lines(self._gen_class_lines(
                    name,
                    td.fields,
                    nested_defs=td.nested_defs,
                    field_naming=td.field_naming,
                ))

    def _write_empties(self, w: _Writer, module: ModuleDef) -> None:
        empties = sorted(
            (n, td)
            for n, td in module.type_defs.items()
            if isinstance(td, EmptyTypeDef)
        )
        if empties:
            w.sep()
            for name, _td in empties:
                w()
                w()
                w('@dc.dataclass(frozen=True, kw_only=True)')
                w('@_set_class_marshal_options')
                w(f'class {name}(lang.Final):')
                w('    pass')

    def _write_variant_wrapper_types(self, w: _Writer, module: ModuleDef) -> None:
        if module.variant_wrappers:
            w.sep()
            for vw in sorted(module.variant_wrappers, key=lambda v: v.class_name):
                w()
                w()
                w.lines(self._gen_variant_wrapper_lines(vw))

    def _gen_variant_wrapper_lines(self, vw: VariantWrapperDef) -> list[str]:
        return self._gen_class_lines(
            vw.class_name,
            vw.source_fields,
            f'{vw.union_name}, lang.Final',
            tag_field=(vw.tag_field_python, vw.tag_value),
        )

    def _write_type_aliases(self, w: _Writer, module: ModuleDef) -> None:
        aliases = sorted(
            (n, td)
            for n, td in module.type_defs.items()
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

    def _write_string_enum_type_aliases(self, w: _Writer, module: ModuleDef) -> None:
        enums = sorted(
            (n, td)
            for n, td in module.type_defs.items()
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

    def _write_any_of_union_type_aliases(self, w: _Writer, module: ModuleDef) -> None:
        unions = sorted(
            (n, td)
            for n, td in module.type_defs.items()
            if isinstance(td, AnyOfUnionTypeDef)
        )
        if unions:
            w.sep()
            for name, td in unions:
                w()
                w()
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

    def _write_polymorphism_registration(self, w: _Writer, module: ModuleDef) -> None:
        if module.disc_unions:
            w.sep()
            w()
            w()
            w('@lang.static_init')
            w('def _install_marshaling() -> None:')
            items = sorted(module.disc_unions.items())
            for i, (union_name, union_td) in enumerate(items):
                w(f'    msh.install_global_standard_factories(*msh.standard_polymorphism_factories(')
                w(f'        msh.polymorphism_from_subclasses(')
                w(f'            {union_name},')
                w(f'            naming=msh.Naming.SNAKE,')
                w(f'            strip_suffix=msh.AUTO_STRIP_SUFFIX,')
                w(f'        ),')
                w(f'        msh.FieldTypeTagging({union_td.discriminator_field!r}),')
                w(f'    ))')
                if i < len(items) - 1:
                    w()
