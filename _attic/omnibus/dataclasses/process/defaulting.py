"""
TODO:
 - *overlap with resolve.rb...*
  - .. overlap with dimensional...
"""
import dataclasses as dc
import typing as ta

from ... import check
from ... import collections as ocol
from ... import lang
from ... import properties
from ..types import Deriver
from ..types import ExtraFieldParams
from .bootstrap import Fields
from .types import Aspect
from .types import attach
from .utils import get_flat_fn_args


class _HasFactory(lang.Final):

    def __repr__(self) -> str:
        return '<factory>'


HasFactory = _HasFactory()


class Pure(ta.NamedTuple):
    fn: ta.Callable


class DeriverNode(ta.NamedTuple):
    fn: ta.Callable
    ias: ta.FrozenSet[str]
    oas: ta.FrozenSet[str]


class DerivationFailedException(TypeError):
    pass


class Defaulting(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    def check(self) -> None:
        if not self.ctx.spec.extra_params.kwonly:
            # Make sure we don't have fields without defaults following fields with defaults.  This actually would be
            # caught when exec-ing the function source code, but catching it here gives a better error message, and
            # future-proofs us in case we build up the function using ast.
            seen_default = False
            for f in self.ctx.spec.fields.init:
                # Only consider fields in the __init__ call.
                if f.init:
                    if not (f.default is dc.MISSING and f.default_factory is dc.MISSING):
                        seen_default = True
                    elif seen_default:
                        raise TypeError(f'non-default argument {f.name!r} follows default argument')

    @properties.cached
    def deriver_nodes(self) -> ta.Sequence[DeriverNode]:
        nodes: ta.List[DeriverNode] = []

        field_derivers_by_field = {
            f: efp.derive
            for f in self.ctx.spec.fields
            if ExtraFieldParams in f.metadata
            for efp in [f.metadata[ExtraFieldParams]]
            if efp.derive is not None
        }
        for f, fd in field_derivers_by_field.items():
            ias = get_flat_fn_args(fd)
            for ia in ias:
                check.in_(ia, self.ctx.spec.fields)
            nodes.append(DeriverNode(fd, frozenset(ias), frozenset([f.name])))

        extra_derivers = self.ctx.spec.rmro_extras_by_cls[Deriver]
        for ed in extra_derivers:
            ias = get_flat_fn_args(ed.fn)
            for ia in ias:
                check.in_(ia, self.ctx.spec.fields)
            if isinstance(ed.attrs, str):
                oas = [ed.attrs]
            elif isinstance(ed.attrs, ta.Iterable):
                oas = ed.attrs
            else:
                raise TypeError(ed)
            for oa in oas:
                check.isinstance(oa, str)
                check.in_(oa, self.ctx.spec.fields)
            nodes.append(DeriverNode(ed.fn, frozenset(ias), frozenset(oas)))

        return tuple(nodes)

    @properties.cached
    def derivable_field_names(self) -> ta.AbstractSet[str]:
        return frozenset(a for dn in self.deriver_nodes for a in dn.oas)

    @properties.cached
    def deriver_supersteps(self):
        if not self.deriver_nodes:
            return []

        nodes_by_oa = {}
        for n in self.deriver_nodes:
            for oa in n.oas:
                if oa in nodes_by_oa:
                    raise AttributeError('Duplicate deriver output', n, nodes_by_oa[oa])
                nodes_by_oa[oa] = n

        return list(ocol.toposort({oa: set(n.ias) for oa, n in nodes_by_oa.items()}))

    @properties.cached
    def deriver_node_ordering(self) -> ta.Sequence[DeriverNode]:
        fno = [a for ss in self.deriver_supersteps for a in sorted(ss) if a in self.derivable_field_names]
        fni = dict(map(reversed, enumerate(fno)))

        def kt(s):
            return tuple(sorted(a for a in s for i in [fni.get(a)] if i is not None))
        return sorted(self.deriver_nodes, key=lambda dn: (kt(dn.oas), kt(dn.ias)))

    @attach('init')
    class Init(Aspect.Function['Defaulting']):

        @properties.cached
        def default_names_by_field_name(self) -> ta.Mapping[str, str]:
            return {
                f.name: self.fctx.nsb.put(f.default, f'_{f.name}_default')
                for f in self.fctx.ctx.spec.fields.init
                if f.default is not dc.MISSING
            }

        @properties.cached
        def default_factory_names_by_field_name(self) -> ta.Mapping[str, str]:
            return {
                f.name: self.fctx.nsb.put(f.default_factory, f'_{f.name}_default_factory')
                for f in self.fctx.ctx.spec.fields.init
                if f.default_factory is not dc.MISSING
            }

        @properties.cached
        def deriver_fn_names_by_deiver_node(self) -> ta.Mapping[DeriverNode, str]:
            return ocol.IdentityKeyDict(
                (dn, self.fctx.nsb.put(dn.fn, f'_deriver_{i}'))
                for i, dn in enumerate(self.aspect.deriver_nodes)
            )

        @properties.cached
        def has_factory_name(self) -> str:
            return self.fctx.nsb.put(HasFactory, '_has_factory')

        @properties.cached
        def derivation_failed_exception_name(self) -> str:
            return self.fctx.nsb.put(DerivationFailedException, '_DerivationFailedException')

        @attach(Aspect.Function.Phase.DEFAULT)
        def build_default_lines(self) -> ta.List[str]:
            ret = []

            for f in self.fctx.ctx.spec.fields.init:
                if not f.init:
                    if f.default is not dc.MISSING:
                        ret.append(f'{f.name} = {self.default_names_by_field_name[f.name]}')
                    elif f.default_factory is not dc.MISSING:
                        ret.append(f'{f.name} = {self.default_factory_names_by_field_name[f.name]}()')
                elif f.default_factory is not dc.MISSING:
                    default_factory_name = self.default_factory_names_by_field_name[f.name]
                    ret.append(f'if {f.name} is {self.has_factory_name}: {f.name} = {default_factory_name}()')

            if self.aspect.deriver_nodes:
                for dn in self.aspect.deriver_node_ordering:
                    s0 = ' and '.join(f'{a} is not {self.has_factory_name}' for a in dn.ias)
                    s1 = ' and '.join(f'{a} is {self.has_factory_name}' for a in dn.oas)
                    s2 = f'{s0} and {s1}' if s0 and s1 else (s0 or s1)
                    check.not_empty(s2)
                    s3 = (', '.join(dn.oas) + ' =') if dn.oas else ''
                    fnn = self.deriver_fn_names_by_deiver_node[dn]
                    s4 = ", ".join(f'{a}={a}' for a in dn.ias)
                    ret.append(f'if {s2}: {s3} {fnn}({s4})')
                for a in self.aspect.derivable_field_names:
                    ret.append(
                        f'if {a} is {self.has_factory_name}: '
                        f'raise {self.derivation_failed_exception_name}("{a}")'
                    )

            return ret
