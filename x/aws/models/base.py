"""
TODO:
 - ** GEN FROM BOTO SHAPES **
  - keep hand-written base, hand-written overrides (tags)
  - don't gen full trees?
 - add:
  - s3
  - sqs
  - lambda
 - mapping <> boto model
 - make nodal? add optional 'MISSING' support?
"""
import abc
import datetime
import typing as ta
import weakref

from omnibus import check
from omnibus import collections as col
from omnibus import dataclasses as dc
from omnibus import lang
from omnibus import nodal


ModelT = ta.TypeVar('ModelT', bound='Model')
ParsableT = ta.TypeVar('ParsableT', bound='Parsable')
StrMap = ta.Mapping[str, ta.Any]
T = ta.TypeVar('T')


class MISSING(lang.Marker):
    pass


class MEMBER_NAME(lang.Marker):  # noqa
    pass


class SHAPE_NAME(lang.Marker):  # noqa
    pass


PRIM_TYPES = (int, bool, str, datetime.datetime)


class Parsable(lang.Abstract):
    @abc.abstractclassmethod
    def parse(cls: ParsableT, raw: StrMap) -> ParsableT:
        raise NotImplementedError


class StrMapBox(dc.Frozen, Parsable, ta.Mapping[str, T], abstract=True):
    dct: ta.Mapping[str, T] = dc.field(default=(), coerce=col.map_of(check.non_empty_str, lang.identity))

    def __getitem__(self, k: str) -> T:
        return self.dct[k]

    def __len__(self) -> int:
        return len(self.dct)

    def __iter__(self) -> ta.Iterator[str]:
        return iter(self.dct)

    @classmethod
    def of(cls, obj: ta.Union['Tags', ta.Mapping[str, T], ta.Iterable[ta.Tuple[str, T]]]) -> 'Tags':
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, ta.Iterable):
            return cls(obj)
        else:
            raise TypeError(obj)

    @classmethod
    def parse(cls: ta.Type['StrMapBox[T]'], dct: ta.Mapping[str, T]) -> T:
        return cls(dct)


class Tags(StrMapBox[str], final=True):
    pass


class Raw(StrMapBox[ta.Any], final=True):
    pass


_MODEL_FIELDS_BY_CLS: ta.Mapping[ta.Type['Model'], nodal.Fields] = weakref.WeakKeyDictionary()


def get_model_cls_fields(cls: ta.Type['Model']) -> nodal.Fields:
    check.issubclass(cls, Model)
    try:
        return _MODEL_FIELDS_BY_CLS[cls]
    except KeyError:
        pass
    fis = nodal.build_nodal_fields(cls, Model, strict=True)
    for f in fis.flds.values():
        if not f.peer and not issubclass(f.spec.erased_cls, Parsable) and f.spec.erased_cls not in PRIM_TYPES:
            raise TypeError(f)
    ta.cast(ta.MutableMapping, _MODEL_FIELDS_BY_CLS)[cls] = fis
    return fis


class Model(dc.Enum, Parsable, kwonly=True):
    raw: ta.Optional[Raw] = dc.field(None, repr=False)

    @classmethod
    def new_missing(cls: ta.Type[ModelT], **kwargs) -> ModelT:
        return cls(**{
            **{f.name: MISSING for f in get_model_cls_fields(cls).flds.values()},
            **kwargs,
        })

    @classmethod
    def new_empty(cls: ta.Type[ModelT], **kwargs) -> ModelT:
        dct = {**kwargs}

        for f in get_model_cls_fields(cls).flds.values():
            if f.name in dct:
                continue
            if f.opt:
                v = None
            elif f.seq:
                v = []
            elif issubclass(f.spec.erased_cls, Model):
                v = f.spec.erased_cls.new_empty()  # noqa
            elif f.spec.erased_cls in PRIM_TYPES:
                v = f.spec.erased_cls()
            else:
                raise TypeError(f.spec.erased_cls)
            dct[f.name] = v

        return cls(**{
            **{f.name: (f.type()) for f in dc.fields(cls)},
            **kwargs,
        })

    @classmethod
    def parse(cls: ta.Type[ModelT], raw: StrMap) -> ModelT:
        check.isinstance(raw, ta.Mapping)
        flds = get_model_cls_fields(cls).flds
        dct = {
            **{f.name: MISSING for f in flds.values()},
            'raw': Raw.of(raw),
        }

        for k, val in raw.items():
            fld = flds.get(lang.decamelize(k))
            if fld is not None:
                if issubclass(fld.spec.erased_cls, Parsable):
                    if fld.opt and val is None:
                        pass
                    elif fld.seq:
                        if not isinstance(val, ta.Sequence) or isinstance(val, str):
                            raise TypeError(val)
                        val = [fld.spec.erased_cls.parse(e) for e in val]
                    else:
                        val = fld.spec.erased_cls.parse(val)

                dct[fld.name] = nodal.check_nodal_field_value(val, fld)

        return cls(**dct)
