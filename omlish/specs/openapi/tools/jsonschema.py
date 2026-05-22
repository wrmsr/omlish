import re
import typing as ta

from .... import check
from .... import dataclasses as dc
from ... import jsonschema as jsch
from ..openapi import Header
from ..openapi import MediaType
from ..openapi import Openapi
from ..openapi import Operation
from ..openapi import Parameter
from ..openapi import ParameterCommon
from ..openapi import PathItem
from ..openapi import Reference
from ..openapi import RequestBody
from ..openapi import Response
from ..openapi import Schema


##


DEFAULT_SCHEMA_DIALECT = 'https://json-schema.org/draft/2020-12/schema'

COMPONENTS_SCHEMA_REF_PREFIX = '#/components/schemas/'
DEFS_REF_PREFIX = '#/$defs/'

PATH_ITEM_METHODS: ta.Sequence[str] = (
    'get',
    'put',
    'post',
    'delete',
    'options',
    'head',
    'patch',
    'trace',
)


##


@dc.dataclass(frozen=True)
class OpenapiJsonschema:
    schema: ta.Mapping[str, ta.Any]
    names: ta.Mapping[str, Schema]


@dc.dataclass(frozen=True)
class _NamedSchema:
    name: str
    schema: Schema


##


def render_schema(sch: Schema) -> dict[str, ta.Any]:
    dct: dict[str, ta.Any] = {}

    if sch.keywords is not None:
        dct.update(jsch.render_keywords(sch.keywords))

    if sch.discriminator is not None:
        dct['discriminator'] = {
            'propertyName': sch.discriminator.property_name,
            **({'mapping': dict(sch.discriminator.mapping)} if sch.discriminator.mapping is not None else {}),
        }

    if sch.xml is not None:
        xml = {}
        for k in ('name', 'namespace', 'prefix', 'attribute', 'wrapped'):
            if (v := getattr(sch.xml, k)) is not None:
                xml[k] = v
        dct['xml'] = xml

    if sch.external_docs is not None:
        dct['externalDocs'] = {
            'url': sch.external_docs.url,
            **({'description': sch.external_docs.description} if sch.external_docs.description is not None else {}),
        }

    if sch.example is not None:
        dct['example'] = sch.example

    return dct


def build_jsonschema(api: Openapi) -> OpenapiJsonschema:
    namer = _SchemaNamer()
    named: list[_NamedSchema] = []

    def add(name_parts: ta.Iterable[str], schema: Schema) -> None:
        named.append(_NamedSchema(namer.name(name_parts), schema))

    components = api.components
    if components is not None:
        for n, s in (components.schemas or {}).items():
            add([n], s)

        for n, p in (components.parameters or {}).items():
            _collect_parameter(add, ['parameter', n], p)

        for n, h in (components.headers or {}).items():
            _collect_header(add, ['header', n], h)

        for n, rb in (components.requestbodies or {}).items():
            _collect_request_body(add, ['requestBody', n], rb)

        for n, r in (components.responses or {}).items():
            _collect_response(add, ['response', n], r)

        for n, cb in (components.callbacks or {}).items():
            _collect_callback(add, ['callback', n], cb)

        for n, pi in (components.path_items or {}).items():
            _collect_path_item(add, ['pathItem', n], pi)

    for path, pi in (api.paths or {}).items():
        _collect_path_item(add, ['path', path], pi)

    for path, pi in (api.webhooks or {}).items():
        _collect_path_item(add, ['webhook', path], pi)

    defs = {ns.name: _rewrite_refs(render_schema(ns.schema)) for ns in named}

    schema: dict[str, ta.Any] = {
        '$schema': api.json_schema_dialect or DEFAULT_SCHEMA_DIALECT,
        '$defs': defs,
    }

    if defs:
        schema['anyOf'] = [{'$ref': DEFS_REF_PREFIX + n} for n in defs]

    return OpenapiJsonschema(schema, {ns.name: ns.schema for ns in named})


def build_jsonschema_schema(api: Openapi) -> ta.Mapping[str, ta.Any]:
    return build_jsonschema(api).schema


##


class _SchemaNamer:
    def __init__(self) -> None:
        super().__init__()

        self._seen: set[str] = set()

    def name(self, parts: ta.Iterable[str]) -> str:
        base = ''.join(_name_part(p) for p in parts)
        if not base:
            base = 'Schema'
        if base[0].isdigit():
            base = 'Schema' + base

        name = base
        idx = 2
        while name in self._seen:
            name = f'{base}{idx}'
            idx += 1

        self._seen.add(name)
        return name


def _name_part(s: str) -> str:
    return ''.join(w[:1].upper() + w[1:] for w in re.findall(r'[A-Za-z0-9]+', s))


def _media_type_name(mt: str) -> str:
    if mt == '*/*':
        return 'Any'
    return _name_part(mt)


def _status_name(status: str) -> str:
    if status == 'default':
        return 'Default'
    return status


def _op_name(path: str, method: str, op: Operation) -> list[str]:
    if op.operation_id:
        return [op.operation_id]
    return [method, path]


##


def _collect_path_item(
        add: ta.Callable[[ta.Iterable[str], Schema], None],
        base: list[str],
        pi: PathItem | Reference,
) -> None:
    if isinstance(pi, Reference):
        return

    for p in pi.parameters or ():
        _collect_parameter(add, [*base, 'parameter'], p)

    for method in PATH_ITEM_METHODS:
        op = getattr(pi, method)
        if op is not None:
            _collect_operation(add, [*base, method], method, op)


def _collect_callback(
        add: ta.Callable[[ta.Iterable[str], Schema], None],
        base: list[str],
        cb: ta.Mapping[str, PathItem | Reference] | Reference,
) -> None:
    if isinstance(cb, Reference):
        return

    for expr, pi in cb.items():
        _collect_path_item(add, [*base, expr], pi)


def _collect_operation(
        add: ta.Callable[[ta.Iterable[str], Schema], None],
        base: list[str],
        method: str,
        op: Operation,
) -> None:
    op_base = _op_name(base[-2], method, op) if len(base) >= 2 and base[-2] != 'webhook' else base

    for p in op.parameters or ():
        _collect_parameter(add, [*op_base, 'parameter'], p)

    if op.request_body is not None:
        _collect_request_body(add, [*op_base, 'requestBody'], op.request_body)

    for status, r in (op.responses or {}).items():
        _collect_response(add, [*op_base, 'response', _status_name(status)], r)

    for name, cb in (op.callbacks or {}).items():
        if isinstance(cb, Reference):
            continue
        for expr, pi in cb.items():
            _collect_path_item(add, [*op_base, 'callback', name, expr], pi)


def _collect_parameter(
        add: ta.Callable[[ta.Iterable[str], Schema], None],
        base: list[str],
        p: Parameter | Reference,
) -> None:
    if isinstance(p, Reference):
        return

    _collect_parameter_common(add, [*base, p.in_, p.name], p.common)


def _collect_header(
        add: ta.Callable[[ta.Iterable[str], Schema], None],
        base: list[str],
        h: Header | Reference,
) -> None:
    if isinstance(h, Reference):
        return

    _collect_parameter_common(add, base, h.common)


def _collect_parameter_common(
        add: ta.Callable[[ta.Iterable[str], Schema], None],
        base: list[str],
        pc: ParameterCommon,
) -> None:
    if pc.schema is not None:
        _collect_schema_ref(add, [*base, 'schema'], pc.schema)

    for mt, m in (pc.content or {}).items():
        _collect_media_type(add, [*base, 'content', _media_type_name(mt)], m)


def _collect_request_body(
        add: ta.Callable[[ta.Iterable[str], Schema], None],
        base: list[str],
        rb: RequestBody | Reference,
) -> None:
    if isinstance(rb, Reference):
        return

    for mt, m in rb.content.items():
        _collect_media_type(add, [*base, _media_type_name(mt)], m)


def _collect_response(
        add: ta.Callable[[ta.Iterable[str], Schema], None],
        base: list[str],
        r: Response | Reference,
) -> None:
    if isinstance(r, Reference):
        return

    for h, hv in (r.headers or {}).items():
        _collect_header(add, [*base, 'header', h], hv)

    for mt, m in (r.content or {}).items():
        _collect_media_type(add, [*base, _media_type_name(mt)], m)


def _collect_media_type(
        add: ta.Callable[[ta.Iterable[str], Schema], None],
        base: list[str],
        m: MediaType,
) -> None:
    if m.schema is not None:
        _collect_schema_ref(add, [*base, 'schema'], m.schema)


def _collect_schema_ref(
        add: ta.Callable[[ta.Iterable[str], Schema], None],
        base: list[str],
        sr: Schema | Reference,
) -> None:
    if isinstance(sr, Reference):
        return

    add(base, sr)


##


def _rewrite_refs(v: ta.Any) -> ta.Any:
    if isinstance(v, ta.Mapping):
        ret = {k: _rewrite_refs(mv) for k, mv in v.items()}
        if (ref := ret.get('$ref')) is not None:
            ret['$ref'] = _rewrite_ref(check.isinstance(ref, str))
        return ret

    elif isinstance(v, ta.Sequence) and not isinstance(v, (str, bytes, bytearray)):
        return [_rewrite_refs(e) for e in v]

    else:
        return v


def _rewrite_ref(ref: str) -> str:
    if ref.startswith(COMPONENTS_SCHEMA_REF_PREFIX):
        return DEFS_REF_PREFIX + ref[len(COMPONENTS_SCHEMA_REF_PREFIX):]

    else:
        return ref
