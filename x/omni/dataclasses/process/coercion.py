"""
TODO:
 - make defaults w/ coerce dc.MISSING in argspec, only coerce if not default or default_factory
 - support 'bool' coercion
"""
import typing as ta

from ..types import ExtraFieldParams
from .defaulting import Defaulting
from .types import Aspect
from .types import attach


class Coercion(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Defaulting]

    @attach('init')
    class Init(Aspect.Function['Coercion']):

        @attach(Aspect.Function.Phase.COERCE)
        def build_coercion_lines(self) -> ta.List[str]:
            ret = []
            for fld in self.fctx.ctx.spec.fields.init:
                if not fld.init:
                    continue
                cmd = fld.metadata.get(ExtraFieldParams, ExtraFieldParams()).coerce
                if cmd is None:
                    continue
                ret.append(f'{fld.name} = {self.fctx.nsb.put(cmd)}({fld.name})')
            return ret

    @attach('pre_set')
    class PreSet(Aspect.Function['Coercion']):

        @attach(Aspect.Function.Phase.COERCE)
        def build_coercion_lines(self) -> ta.List[str]:
            fld = self.fctx.field
            if not fld.init:
                return []
            cmd = fld.metadata.get(ExtraFieldParams, ExtraFieldParams()).coerce
            if cmd is None:
                return []
            return [f'{fld.name} = {self.fctx.nsb.put(cmd)}({fld.name})']
