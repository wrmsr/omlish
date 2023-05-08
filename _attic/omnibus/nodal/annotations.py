import collections.abc
import operator
import threading
import typing as ta
import weakref

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from ..serde import mapping as sm


AnnotationT = ta.TypeVar('AnnotationT', bound='Annotation')


class Annotation(dc.Enum, confer=dc.get_cls_spec(dc.Enum).extra_params.confer):
    pass


def _coerce_anns(
        obj: ta.Union[ta.Mapping[ta.Type[Annotation], ta.Optional[Annotation]], ta.Iterable[Annotation]],
) -> ta.Sequence[Annotation]:
    if isinstance(obj, collections.abc.Mapping):
        ret = []
        seen = set()
        for c, a in obj.items():
            if a is not None and type(a) is not c:
                raise TypeError((c, a))
            if c in seen:
                raise KeyError(c)
            seen.add(c)
            if a is not None:
                ret.append(a)
        return ret
    else:
        return [check.isinstance(a, Annotation) for a in obj]


_ANNS_CLS_CACHE = weakref.WeakKeyDictionary()
_ANNS_CLS_CACHE_LOCK = threading.RLock()


class _AnnotationsMeta(dc.Meta):

    def __new__(mcls, name, bases, namespace, **kwargs):
        if name == 'Annotations' and namespace['__module__'] == __name__:
            return super().__new__(mcls, name, bases, namespace, **kwargs)

        check.not_in('_ann_cls', namespace)
        check.arg(list(bases) == [Annotations])

        s = check.isinstance(rfl.spec(check.single(namespace['__orig_bases__'])), rfl.ExplicitParameterizedGenericTypeSpec)  # noqa
        check.state(s.erased_cls is Annotations)

        ann_cls = check.issubclass(check.single(s.cls_args), Annotation)

        try:
            return _ANNS_CLS_CACHE[ann_cls]
        except KeyError:
            pass

        namespace['_ann_cls'] = ann_cls

        if lang.Final not in bases:
            bases = (*bases, lang.Final)

        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        try:
            return _ANNS_CLS_CACHE[ann_cls]
        except KeyError:
            with _ANNS_CLS_CACHE_LOCK:
                try:
                    return _ANNS_CLS_CACHE[ann_cls]
                except KeyError:
                    _ANNS_CLS_CACHE[ann_cls] = cls
                    return cls


class Annotations(
    dc.Frozen,
    ta.Generic[AnnotationT],
    collections.abc.Sized,
    ta.Iterable[AnnotationT],
    ta.Container[ta.Type[AnnotationT]],
    abstract=True,
    allow_setattr=True,
    metaclass=_AnnotationsMeta,
):
    anns: ta.Sequence[AnnotationT] = dc.field(
        (),
        coerce=_coerce_anns,
        metadata={
            sm.GetType: lambda cls: ta.Sequence[cls._ann_cls],
            sm.Ignore: operator.not_,
        },
    )

    _ann_cls: ta.ClassVar[ta.Type[Annotation]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        check.issubclass(cls._ann_cls, Annotation)

    def __post_init__(self) -> None:
        ann_cls = self._ann_cls
        for ann in self.anns:
            check.isinstance(ann, ann_cls)

        dct = {}
        for ann in self.anns:
            check.not_in(type(ann), dct)
            dct[type(ann)] = ann
        self._anns_by_cls: ta.Mapping[ta.Type[AnnotationT], AnnotationT] = dct

    def __bool__(self) -> bool:
        return bool(self.anns)

    def keys(self) -> ta.Iterator[ta.Type[AnnotationT]]:
        return iter(self._anns_by_cls.keys())

    def __getitem__(self, cls: ta.Type[AnnotationT]) -> AnnotationT:
        check.issubclass(cls, self._ann_cls)
        return self._anns_by_cls[cls]

    def __contains__(self, cls: ta.Type[AnnotationT]) -> bool:  # noqa
        check.issubclass(cls, self._ann_cls)
        return cls in self._anns_by_cls

    def __len__(self) -> int:
        return len(self._anns_by_cls)

    def __iter__(self) -> ta.Iterator[Annotation]:
        return iter(self._anns_by_cls.values())

    def filter(self, pred: ta.Callable[[AnnotationT], bool]) -> ta.Mapping[ta.Type[Annotation], Annotation]:
        return {type(a): a for a in self if pred(a)}
