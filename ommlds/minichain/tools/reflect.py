"""
TODO:
 - ta.Annotated
 - @dataclass class Params
  - params desc options:
   - dc.field(metadata=dict(ToolParam: ToolParam(desc=...
   - @tool_spec_override(params=...
   - omdev.py.attrdocs
   - ta.Annotated[ToolSpecParam(...
 - strict mode - must get params docstring block somewhat like the fn params
"""
import collections.abc
import inspect
import textwrap
import types
import typing as ta

from omdev.py import docstrings
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import metadata as md
from omlish import reflect as rfl
from omlish.lite.cached import cached_nullary

from .types import EnumToolDtype
from .types import MappingToolDtype
from .types import NullableToolDtype
from .types import PrimitiveToolDtype
from .types import SequenceToolDtype
from .types import ToolDtype
from .types import ToolParam
from .types import ToolSpec
from .types import TupleToolDtype
from .types import UnionToolDtype


##


@dc.dataclass(frozen=True)
class _ToolSpecAttach(ToolSpec, md.FunctionDecoratorObjectMetadata):
    pass


tool_spec_attach = _ToolSpecAttach


@dc.dataclass(frozen=True)
class _ToolSpecOverride(ToolSpec, md.FunctionDecoratorObjectMetadata):
    pass


tool_spec_override = _ToolSpecOverride


def tool_param_metadata(**kwargs: ta.Any) -> dict:
    return {ToolParam: ToolParam(**kwargs)}


##


class ToolReflector:
    def reflect_union_type(self, *args: rfl.Type) -> ToolDtype:
        check.unique(args)

        if types.NoneType in args:
            is_nullable = True
            args = tuple(a for a in args if a is not types.NoneType)
        else:
            is_nullable = False

        check.not_empty(args)

        ret: ToolDtype
        if len(args) == 1:
            ret = self.reflect_type(check.single(args))

        else:
            ret = UnionToolDtype(tuple(
                self.reflect_type(a_rty)
                for a_rty in args
            ))

        if is_nullable:
            ret = NullableToolDtype(ret)

        return ret

    SEQUENCE_TYPES: ta.Container[type] = frozenset([
        collections.abc.Sequence,
        list,
    ])

    MAPPING_TYPES: ta.Container[type] = frozenset([
        collections.abc.Mapping,
        dict,
    ])

    def reflect_type(self, rty: rfl.Type) -> ToolDtype:
        if isinstance(rty, (type, rfl.Any)):
            return PrimitiveToolDtype.of(rty)

        if isinstance(rty, rfl.Union):
            return self.reflect_union_type(*rty.args)

        if isinstance(rty, rfl.Generic):
            g_cls = rty.cls

            if g_cls in self.SEQUENCE_TYPES:
                a_rty = check.single(rty.args)
                return SequenceToolDtype(self.reflect_type(a_rty))

            if g_cls in self.MAPPING_TYPES:
                k_rty, v_rty = rty.args
                return MappingToolDtype(
                    self.reflect_type(k_rty),
                    self.reflect_type(v_rty),
                )

            if g_cls is tuple:
                return TupleToolDtype(tuple(
                    self.reflect_type(a_rty)
                    for a_rty in rty.args
                ))

        if isinstance(rty, rfl.Literal):
            return EnumToolDtype(
                self.reflect_union_type(*col.unique(
                    rfl.type_(type(a))
                    for a in rty.args
                )),
                rty.args,
            )

        raise TypeError(rty)

    #

    def reflect_function(self, fn: ta.Callable) -> ToolSpec:
        if (sts := md.get_object_metadata(fn, type=_ToolSpecAttach)):
            return check.isinstance(check.single(sts), ToolSpec)

        #

        ts_ovr: dict[str, ta.Any] = {}
        for o in md.get_object_metadata(fn, type=_ToolSpecOverride):
            # TODO: better params handling / merging
            ts_ovr.update({
                k: v
                for k, v in dc.asdict(o).items()
                if v is not None
            })

        #

        ts_kw: dict[str, ta.Any] = dict(ts_ovr)

        if 'name' not in ts_kw:
            ts_kw.update(name=fn.__name__)

        #

        ds: docstrings.Docstring | None = None
        if (doc := inspect.getdoc(fn)) is not None:
            ds = docstrings.parse(doc)

        if ds is not None:
            if 'desc' not in ts_kw:
                ts_kw.update(desc=ds.description)

            if 'returns_desc' not in ts_kw and ds.returns is not None:
                ts_kw.update(returns_desc=ds.returns.description)

        #

        @cached_nullary
        def th() -> ta.Mapping[str, ta.Any]:
            return ta.get_type_hints(fn)

        if 'returns_type' not in ts_kw and 'return' in th():
            ts_kw.update(returns_type=self.reflect_type(rfl.type_(th()['return'])))

        #

        @cached_nullary
        def sig() -> inspect.Signature:
            return inspect.signature(fn)

        if 'params' not in ts_kw:
            ds_p_dct = {
                ds_p.arg_name: ds_p
                for ds_p in (ds.params if ds is not None else [])
            }

            params: dict[str, ToolParam] = {}
            for sig_p in sig().parameters.values():
                check.not_in(sig_p.name, params)

                ds_p = ds_p_dct.get(sig_p.name)

                params[sig_p.name] = ToolParam(
                    sig_p.name,

                    desc=ds_p.description if ds_p is not None else None,

                    type=self.reflect_type(rfl.type_(th()[sig_p.name])) if sig_p.name in th() else None,

                    required=sig_p.default is inspect.Parameter.empty,
                )

            ts_kw.update(params=tuple(params.values()) if params else None)

        #

        return ToolSpec(**ts_kw)

    #

    def reflect_params_dataclass(self, cls: type) -> ta.Sequence[ToolParam]:
        check.isinstance(cls, type)
        check.arg(dc.is_dataclass(cls))

        dc_rfl = dc.reflect(cls)

        params: dict[str, ToolParam] = {}
        for f in dc_rfl.fields.values():
            tp_kw = dict(
                name=f.name,
            )

            md_tp = f.metadata.get(ToolParam)
            if md_tp is not None:
                tp_kw.update({
                    k: v
                    for k, v in dc.asdict(md_tp).items()
                    if v is not None
                })

            if 'desc' in tp_kw:
                tp_kw.update(desc=textwrap.dedent(tp_kw['desc']))

            if 'type' not in tp_kw:
                tp_kw.update(type=dc_rfl.type_hints[f.name])

            if 'required' not in tp_kw:
                tp_kw.update(required=f.default is dc.MISSING)

            tpn = check.non_empty_str(tp_kw['name'])
            check.not_in(tpn, params)
            params[tpn] = ToolParam(**tp_kw)

        return tuple(params.values())  # noqa

##


def reflect_tool_spec(fn: ta.Callable) -> ToolSpec:
    return ToolReflector().reflect_function(fn)
