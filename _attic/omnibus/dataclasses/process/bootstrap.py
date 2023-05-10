import dataclasses as dc
import sys
import typing as ta

from .. import construction as csn
from ... import check
from ..fields import build_cls_fields
from ..internals import DataclassParams
from ..internals import PARAMS
from ..kwargs import update_class_kwargs_metadata
from ..types import ExtraParams
from ..types import MetaclassParams
from ..types import METADATA_ATTR
from ..types import Original
from .types import Aspect


class FixVarAnnotations(Aspect):
    # https://github.com/python/cpython/blob/0dd98c2d00a75efbec19c2ed942923981bc06683/Lib/test/test_dataclasses.py#L2908
    # https://github.com/python/cpython/blob/0dd98c2d00a75efbec19c2ed942923981bc06683/Lib/dataclasses.py#L612

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return []

    EVAL_OBJS = {
        dc.InitVar,
        ta.ClassVar,
    }

    def process(self) -> ta.Sequence[csn.Action]:
        anns = self.ctx.cls.__dict__.get('__annotations__', {})
        if not anns:
            return []
        mod = sys.modules.get(self.ctx.cls.__dict__.get('__module__'))
        if mod is None:
            return []

        for name, ann in anns.items():
            if not isinstance(ann, str):
                continue
            prefix, _, suffix = ann.partition('[') if '[' in ann else (ann, None, '')
            obj = mod
            for part in prefix.split('.'):
                if obj in self.EVAL_OBJS:
                    break
                if not hasattr(obj, '__dict__') or part not in obj.__dict__:
                    break
                obj = obj.__dict__[part]
            if obj not in self.EVAL_OBJS:
                continue
            anns[name] = obj['[' + suffix] if suffix else obj

        return []


class Params(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [FixVarAnnotations]

    def process(self) -> ta.Sequence[csn.Action]:
        self.ctx.set_new_attribute(PARAMS, self.ctx.params, raise_=True)
        check.state(self.ctx.spec.params is self.ctx.params)

        if METADATA_ATTR in self.ctx.cls.__dict__:
            md = getattr(self.ctx.cls, METADATA_ATTR)
        else:
            md = {}
            self.ctx.set_new_attribute(METADATA_ATTR, md, raise_=True)
        check.state(self.ctx.spec._metadata is md)

        if self.ctx.extra_params.kwargs:
            kw_md = update_class_kwargs_metadata(self.ctx.cls, self.ctx.extra_params.kwargs)
            check.state(self.ctx.spec.shallow_extras[-1] is kw_md)

        md[ExtraParams] = self.ctx.extra_params
        md[MetaclassParams] = self.ctx.metaclass_params

        md[Original(DataclassParams)] = self.ctx.original_params
        md[Original(ExtraParams)] = self.ctx.original_extra_params
        md[Original(MetaclassParams)] = self.ctx.original_metaclass_params

        return []


class Fields(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Params]

    def process(self) -> ta.Sequence[csn.Action]:
        build_cls_fields(
            self.ctx.cls,
            reorder=self.ctx.extra_params.reorder,
            install=True,
        )
        return []


class Slots(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    @property
    def slots(self) -> ta.AbstractSet[str]:
        mcp = self.ctx.spec.metaclass_params
        return {'__weakref__'} if mcp is not None and not mcp.no_weakref else set()

    def check(self) -> None:
        seen = set()
        for a in self.ctx.aspects:
            for s in a.slots:
                if s in seen:
                    raise NameError(s)
                seen.add(s)
