"""
TODO:
 - Rewrite lol
 - Enum - enforce Abstract or Final
"""
import abc
import dataclasses as dc
import typing as ta

from ... import lang
from ..api.classes.decorator import dataclass
from .confer import CONFER_METACLASS_PARAMS
from .confer import confer_kwargs
from .specs import MetaclassSpec
from .specs import get_metaclass_spec


T = ta.TypeVar('T')


##


class DataMeta(abc.ABCMeta):
    def __new__(
            mcls,
            name,
            bases,
            namespace,
            *,

            abstract=False,
            sealed=False,
            final=False,

            metadata=None,
            **kwargs,
    ):
        ckw = confer_kwargs(bases, kwargs)
        nkw = {**kwargs, **ckw}

        mcp = MetaclassSpec(**{
            mpa: nkw.pop(mpa)
            for mpa in CONFER_METACLASS_PARAMS
            if mpa in nkw
        })

        metadata = [
            *([metadata] if metadata is not None else []),
            mcp,
        ]

        #

        xbs: list[type] = []

        if any(
                get_metaclass_spec(b).abstract_immediate_subclasses  # type: ignore[arg-type]
                for b in bases
                if dc.is_dataclass(b)
        ):
            abstract = True

        final |= (mcp.final_subclasses and not abstract)

        if final and abstract:
            raise TypeError(f'Class cannot be abstract and final: {name!r}')

        if abstract:
            xbs.append(lang.Abstract)
        if sealed:
            xbs.append(lang.Sealed)
        if final:
            xbs.append(lang.Final)

        if xbs:
            if bases and bases[-1] is ta.Generic:
                bases = (*bases[:-1], *xbs, bases[-1])
            else:
                bases = (*bases, *xbs)
            if ob := namespace.get('__orig_bases__'):
                if getattr(ob[-1], '__origin__', None) is ta.Generic:
                    namespace['__orig_bases__'] = (*ob[:-1], *xbs, ob[-1])
                else:
                    namespace['__orig_bases__'] = (*ob, *xbs)

        #

        ofs: set[str] = set()
        if any(issubclass(b, lang.Abstract) for b in bases) and nkw.get('override'):
            ofs.update(a for a in namespace.get('__annotations__', []) if a not in namespace)
            namespace.update((a, dc.MISSING) for a in ofs)

        #

        cls = lang.super_meta(
            super(),
            mcls,
            name,
            bases,
            namespace,
        )

        #

        for a in ofs:
            delattr(cls, a)

        #

        return dataclass(
            cls,
            metadata=metadata,
            **nkw,
        )
