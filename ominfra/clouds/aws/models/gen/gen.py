"""
TODO:
 - default values? nullability? maybe a new_default helper?
 - relative import base
"""
import builtins
import dataclasses as dc
import io
import keyword
import typing as ta

from omlish import check
from omlish import lang
from omlish.algorithm import all as alg
from omlish.lite.strings import snake_case


if ta.TYPE_CHECKING:
    import botocore.loaders
    import botocore.mode2
    import botocore.session
else:
    botocore = lang.proxy_import('botocore', extras=[
        'loaders',
        'model',
        'session',
    ])


##


ServiceTypeName: ta.TypeAlias = ta.Literal[
    'service-2',
    'paginators-1',
    'waiters-2',
]


class ModelGen:
    def __init__(
            self,
            service_model: 'botocore.model.ServiceModel',
            *,
            shape_names: ta.Iterable[str] = (),
            operation_names: ta.Iterable[str] = (),
    ) -> None:
        super().__init__()

        self._service_model = service_model
        self._shape_names = list(check.not_isinstance(shape_names, str))
        self._operation_names = list(check.not_isinstance(operation_names, str))

    @property
    def service_model(self) -> 'botocore.model.ServiceModel':
        return self._service_model

    @property
    def shape_names(self) -> ta.Sequence[str]:
        return self._shape_names

    @property
    def operation_names(self) -> ta.Sequence[str]:
        return self._operation_names

    #

    @classmethod
    def create_data_loader(cls) -> 'botocore.loaders.Loader':
        session = botocore.session.get_session()
        return session.get_component('data_loader')

    @classmethod
    def list_available_services(
            cls,
            *,
            type_name: ServiceTypeName = 'service-2',
    ) -> list[str]:
        loader = cls.create_data_loader()
        return list(loader.list_available_services(type_name))

    @classmethod
    def load_service_model(
            cls,
            service_name: str,
            *,
            type_name: ServiceTypeName = 'service-2',
            api_version: str | None = None,
    ) -> 'botocore.model.ServiceModel':
        loader = cls.create_data_loader()
        json_model = loader.load_service_model(service_name, type_name, api_version=api_version)
        return botocore.model.ServiceModel(json_model, service_name=service_name)

    @classmethod
    def get_referenced_shape_names(
            cls,
            service_model: 'botocore.model.ServiceModel',
            *,
            shape_names: ta.Iterable[str] = (),
            operation_names: ta.Iterable[str] = (),
    ) -> list[str]:
        todo = set(check.not_isinstance(shape_names, str))

        for on in operation_names:
            op = service_model.operation_model(on)
            for osh in [
                op.input_shape,
                op.output_shape,
                *op.error_shapes,
            ]:
                if osh is not None:
                    todo.add(osh.name)

        seen = set(cls.BASE_TYPE_ANNS)

        dct: dict[str, set[str]] = {}
        while todo:
            cur = todo.pop()
            seen.add(cur)

            shape: botocore.model.Shape = service_model.shape_for(cur)

            if isinstance(shape, botocore.model.StructureShape):
                deps = {m.name for m in shape.members.values()}

            elif isinstance(shape, botocore.model.MapShape):
                deps = {shape.key.name, shape.value.name}

            elif isinstance(shape, botocore.model.ListShape):
                deps = {shape.member.name}

            else:
                deps = set()

            dct[shape.name] = deps
            todo.update(deps - seen)

        return list(lang.flatten(sorted(s - cls.BASE_SHAPE_NAMES) for s in alg.mut_toposort(dct)))

    #

    PRIMITIVE_SHAPE_TYPES: ta.ClassVar[ta.Mapping[str, str]] = {
        'boolean': 'bool',

        'integer': 'int',
        'long': 'int',

        'double': 'float',

        'blob': 'bytes',

        'timestamp': '_base.Timestamp',
    }

    #

    BASE_TYPE_ANNS: ta.ClassVar[ta.Mapping[str, str]] = {
        'Boolean': 'bool',

        'Integer': 'int',
        'Long': 'int',

        'String': 'str',

        'DateTime': '_base.DateTime',
        'MillisecondDateTime': '_base.MillisecondDateTime',

        'Tag': '_base.Tag',
        'TagList': '_base.TagList',
    }

    BASE_SHAPE_NAMES: ta.ClassVar[ta.AbstractSet[str]] = set(BASE_TYPE_ANNS)

    #

    def get_type_ann(
            self,
            name: str | None,
            *,
            unquoted_names: bool = False,
    ) -> str | None:
        if name is None:
            return None

        try:
            return self.BASE_TYPE_ANNS[name]
        except KeyError:
            pass

        if name in self._shape_names:
            name = self.sanitize_global_name(name, upper=True)
            if not unquoted_names:
                return f"'{name}'"
            else:
                return name

        return None

    #

    NAME_REPLACEMENTS: ta.ClassVar[ta.Sequence[tuple[str, str]]] = [
        *[
            (p + l, p + r)
            for p in 'KMGTP '
            for l, r in [
                ('bps', 'bips'),
                ('Bps', 'bps'),
                ('ibps', 'ibips'),
                ('iBps', 'ibps'),
            ]
        ],
    ]

    DEMANGLE_PREFIXES: ta.ClassVar[ta.Sequence[str]] = [

        'AAAA',
        'ACL',
        'ACP',
        'AES',
        'AES256',
        'AZ',
        'CA',
        'CRC32',
        'CRC32C',
        'CRC64',
        'CRC64C',
        'DB',
        'EFS',
        'ETag',
        'FQDN',
        'GB',
        'IAM',
        'IO',
        'IP',
        'JSON',
        'KMS',
        'MD5',
        'MFA',
        'NVME',
        'OU',
        'SHA1',
        'SHA256',
        'SSE',
        'TTL',

    ]

    def demangle_name(self, n: str) -> str:
        for l, r in self.NAME_REPLACEMENTS:
            n = n.replace(l, r)

        ps: list[str] = []
        while n:
            ms: list[tuple[str, int]] = []

            for pfx in self.DEMANGLE_PREFIXES:
                if (i := n.find(pfx)) >= 0:
                    ms.append((pfx, i))

            if not ms:
                ps.append(n)
                break

            if len(ms) > 1:
                m = sorted(ms, key=lambda t: (t[1], -len(t[0])))[0]
            else:
                m = ms[0]

            pfx, i = m
            l, r = n[:i], n[i + len(pfx):]

            if l:
                ps.append(l)
            ps.append(pfx.lower())

            n = r

        return '_'.join(snake_case(p) for p in ps)

    #

    def sanitize_local_name(self, n: str) -> str:
        if n in keyword.kwlist:
            n += '_'
        return n

    def sanitize_global_name(self, n: str, *, upper: bool = False) -> str:
        if hasattr(builtins, n):
            n += '_'
        if upper:
            n = n[0].upper() + n[1:]
        return n

    #

    PREAMBLE_LINES: ta.Sequence[str] = [
        '# flake8: noqa: E501',
        '# ruff: noqa: N801 S105',
        '# fmt: off',
        '# @omlish-generated',
        'import enum as _enum  # noqa',
        'import typing as _ta  # noqa',
        '',
        'from omlish import dataclasses as _dc  # noqa',
        '',
        'from .. import base as _base  # noqa',
        '',
        '',
        '##',
        '',
        '',
    ]

    def gen_preamble(self) -> str:
        return '\n'.join(self.PREAMBLE_LINES)

    #

    @dc.dataclass(frozen=True)
    class ShapeSrc:
        src: str

        class_name: str | None = dc.field(default=None, kw_only=True)
        double_space: bool = False

    def gen_shape(
            self,
            name: str,
            *,
            unquoted_names: bool = False,
    ) -> ShapeSrc:
        shape: botocore.model.Shape = self._service_model.shape_for(name)

        san_name = self.sanitize_global_name(shape.name, upper=True)

        if isinstance(shape, botocore.model.StructureShape):
            rms = frozenset(shape.required_members or [])

            lines: list[str] = []

            mds = [
                f'shape_name={shape.name!r}',
            ]

            lines.extend([
                '@_dc.dataclass(frozen=True, kw_only=True)',
                f'class {san_name}(',
                '    _base.Shape,',
                *[f'    {dl},' for dl in mds],
                '):',
            ])

            if not shape.members:
                lines.append('    pass')

            ms: botocore.model.Shape
            seen_fns: set[str] = set()

            for i, (mn, ms) in enumerate(shape.members.items()):
                mds = [
                    f'member_name={mn!r}',
                ]

                if msn := ms.serialization.get('name'):
                    mds.append(f'serialization_name={msn!r}')

                if isinstance(ms, botocore.model.MapShape):
                    ka = self.get_type_ann(
                        ms.key.name,
                        unquoted_names=unquoted_names,
                    ) or ms.key.name
                    va = self.get_type_ann(
                        ms.value.name,
                        unquoted_names=unquoted_names,
                    ) or ms.value.name
                    mds.append(f'value_type=_base.MapValueType({ka}, {va})')

                elif isinstance(ms, botocore.model.ListShape):
                    ea = self.get_type_ann(
                        ms.member.name,
                        unquoted_names=unquoted_names,
                    ) or ms.member.name
                    mds.append(f'value_type=_base.ListValueType({ea})')

                mds.append(f'shape_name={ms.name!r}')

                ma = self.get_type_ann(
                    ms.name,
                    unquoted_names=unquoted_names,
                )

                #

                if i:
                    lines.append('')

                fr = mn in rms
                fa = ma or ms.name
                if fr:
                    fd = ''
                else:
                    fa += ' | None'
                    fd = 'default=None, '

                fn = self.sanitize_local_name(self.demangle_name(mn))
                check.not_in(fn, seen_fns)
                seen_fns.add(fn)

                fls = [
                    f'{fn}: {fa} = _dc.field({fd}metadata=_base.field_metadata(',
                    *[f'    {dl},' for dl in mds],
                    '))',
                ]

                if ma is None:
                    fls = ['# ' + fl for fl in fls]

                lines.append('\n'.join('    ' + fl for fl in fls))

            return self.ShapeSrc(
                '\n'.join(lines),
                class_name=san_name,
                double_space=True,
            )

        elif isinstance(shape, botocore.model.ListShape):
            mn = shape.member.name
            ma = self.get_type_ann(
                mn,
                unquoted_names=unquoted_names,
            )
            l = f'{san_name}: _ta.TypeAlias = _ta.Sequence[{ma or mn}]'
            if ma is None:
                l = '# ' + l
            return self.ShapeSrc(l)

        elif isinstance(shape, botocore.model.MapShape):
            # shape.key, shape.value
            kn = shape.key.name
            ka2 = self.get_type_ann(
                kn,
                unquoted_names=unquoted_names,
            )
            vn = shape.key.name
            va2 = self.get_type_ann(
                vn,
                unquoted_names=unquoted_names,
            )
            l = f'{san_name}: _ta.TypeAlias = _ta.Mapping[{ka2 or kn}, {va2 or vn}]'
            if ka2 is None or va2 is None:
                l = '# ' + l
            return self.ShapeSrc(l)

        elif isinstance(shape, botocore.model.StringShape):
            if shape.enum:
                ls = [
                    f'class {san_name}(_enum.Enum):',
                ]
                all_caps = all(v == v.upper() for v in shape.enum)
                for v in shape.enum:
                    n = v
                    if not all_caps:
                        n = self.demangle_name(n)
                    n = n.upper()
                    for c in '.-:':
                        n = n.replace(c, '_')
                    ls.append(f'    {n} = {v!r}')
                return self.ShapeSrc(
                    '\n'.join(ls),
                    double_space=True,
                )

            else:
                return self.ShapeSrc(f"{san_name} = _ta.NewType('{san_name}', str)")

        elif (pt := self.PRIMITIVE_SHAPE_TYPES.get(shape.type_name)) is not None:
            return self.ShapeSrc(f'{san_name} = _ta.NewType({san_name!r}, {pt})')

        else:
            raise TypeError(shape.type_name)

    def gen_all_shapes(
            self,
            out: ta.TextIO,
            *,
            unquoted_names: bool = False,
    ) -> None:
        shape_srcs = [
            self.gen_shape(
                shape_name,
                unquoted_names=unquoted_names,
            )
            for shape_name in self.shape_names
        ]

        all_shapes: list[str] = []

        prev_shape_src: ModelGen.ShapeSrc | None = None
        for shape_src in shape_srcs:
            if prev_shape_src is not None:
                out.write('\n')
                if shape_src.double_space or prev_shape_src.double_space:
                    out.write('\n')
            out.write(shape_src.src)
            out.write('\n')
            if shape_src.class_name is not None:
                all_shapes.append(shape_src.class_name)
            prev_shape_src = shape_src

        out.write('\n\n')
        out.write('ALL_SHAPES: frozenset[type[_base.Shape]] = frozenset([\n')
        for n in sorted(all_shapes):
            out.write(f'    {n},\n')
        out.write('])\n')

    #

    @dc.dataclass(frozen=True)
    class OperationSrc:
        src: str
        name: str

    def gen_operation(
            self,
            name: str,
    ) -> OperationSrc:
        operation: botocore.model.OperationModel = self._service_model.operation_model(name)

        dcn = self.demangle_name(operation.name).upper()

        fls = [
            f'name={operation.name!r},',
        ]

        if operation.input_shape is not None:
            fls.append(f'input={operation.input_shape.name},')
        if operation.output_shape is not None:
            fls.append(f'output={operation.output_shape.name},')

        if operation.error_shapes:
            fls.append('errors=[')
            for osn in sorted(es.name for es in operation.error_shapes):
                fls.append(f'    {osn},')
            fls.append('],')

        lines = [
            f'{dcn} = _base.Operation(',
            *[f'    {fl}' for fl in fls],
            ')',
        ]

        return self.OperationSrc('\n'.join(lines), dcn)

    def gen_all_operations(
            self,
            out: ta.TextIO,
    ) -> None:
        all_operations: list[str] = []

        for i, name in enumerate(sorted(self._operation_names)):
            if i:
                out.write('\n')
            ops = self.gen_operation(
                name,
            )
            all_operations.append(ops.name)
            out.write(ops.src)
            out.write('\n')
        out.write('\n')

        out.write('\n')
        out.write('ALL_OPERATIONS: frozenset[_base.Operation] = frozenset([\n')
        for n in sorted(all_operations):
            out.write(f'    {n},\n')
        out.write('])\n')

    #

    def gen_module(self) -> str:
        out = io.StringIO()

        out.write(self.gen_preamble())
        out.write('\n')

        self.gen_all_shapes(
            out,
            unquoted_names=True,
        )

        if self._operation_names:
            out.write('\n\n##\n\n\n')

            self.gen_all_operations(out)

        return out.getvalue()


if __name__ == '__main__':
    raise RuntimeError('Use cli')
