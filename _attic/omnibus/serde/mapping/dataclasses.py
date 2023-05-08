import typing as ta
import weakref

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from .core import serde
from .core import serde_gen
from .simple import get_simple_serde
from .types import Deserializer
from .types import FnSerde
from .types import Serde
from .types import Serialized
from .types import Serializer


T = ta.TypeVar('T')


class Ignore(lang.Marker):
    pass


class GetType(lang.Marker):
    pass


class Name(lang.Marker):
    pass


class Aliases(lang.Marker):
    pass


class _DataclassFieldSerde(dc.Pure):
    cls: ta.Any
    ignore_if: ta.Optional[ta.Callable[[ta.Any], bool]] = dc.field(None, kwonly=True)


SubclassMap = ta.Mapping[ta.Union[str, type], ta.Union[type, str]]  # FIXME: gross


_DataclassFieldSerdeMap = ta.Mapping[str, _DataclassFieldSerde]


class _DataclassSerdeState:

    def __init__(self) -> None:
        super().__init__()

        self._subclass_map_resolvers_by_cls: ta.MutableMapping[type, ta.Callable[[type], SubclassMap]] = weakref.WeakKeyDictionary()  # noqa
        self._subclass_maps_by_cls: ta.MutableMapping[type, SubclassMap] = weakref.WeakKeyDictionary()
        self._is_monomorphic_dataclass_by_cls: ta.MutableMapping[type, bool] = weakref.WeakKeyDictionary()
        self._field_type_maps_by_dataclass: ta.MutableMapping[type, _DataclassFieldSerdeMap] = weakref.WeakKeyDictionary()  # noqa

    def subclass_map_resolver_for(self, *clss):
        def inner(fn):
            check.callable(fn)
            for c in clss:
                check.not_in(c, self._subclass_map_resolvers_by_cls)
                self._subclass_map_resolvers_by_cls[c] = fn
            return fn
        check.arg(all(isinstance(c, type) for c in clss))
        return inner

    def format_subclass_name(self, cls: type) -> str:
        check.isinstance(cls, type)
        return lang.decamelize(cls.__name__)

    def build_subclass_map(
            self,
            cls: type,
            *,
            name_formatter: ta.Optional[ta.Callable[[type], str]] = None,
    ) -> SubclassMap:
        if name_formatter is None:
            name_formatter = self.format_subclass_name

        dct = {}
        todo = {cls}
        seen = set()
        while todo:
            cur = todo.pop()
            if cur in seen:
                continue

            seen.add(cur)
            if lang.Abstract not in cur.__bases__:
                n = None
                if dc.is_dataclass(cur):
                    n = dc.metadatas_dict(cur).get(Name)
                    if callable(n):
                        n = n(cur)
                if n is None:
                    n = name_formatter(cur)

                check.isinstance(n, str)
                check.not_empty(n)

                try:
                    existing = dct[n]
                except KeyError:
                    pass
                else:
                    if existing is not cur:
                        raise NameError(n)

                dct[n] = cur
                dct[cur] = n

            todo.update(cur.__subclasses__())

        return dct

    def get_subclass_map(self, cls: type) -> SubclassMap:
        if not isinstance(cls, type):
            raise TypeError(cls)

        try:
            return self._subclass_maps_by_cls[cls]
        except KeyError:
            pass

        try:
            bld = self._subclass_map_resolvers_by_cls[cls]
        except KeyError:
            bld = self.build_subclass_map

        dct = self._subclass_maps_by_cls[cls] = bld(cls)
        return dct

    def _is_monomorphic_dataclass(self, cls: type) -> bool:
        try:
            return self._is_monomorphic_dataclass_by_cls[cls]
        except KeyError:
            pass

        scm = self.get_subclass_map(cls)
        scmcls = {k: v for k, v in scm.items() if isinstance(k, type)}

        ret = False
        if len(scmcls) == 1 and list(scmcls) == [cls] and lang.Final in cls.__bases__:
            ret = True

        self._is_monomorphic_dataclass_by_cls[cls] = ret
        return ret

    def _get_dataclass_field_type_map(self, dcls: type) -> _DataclassFieldSerdeMap:
        if not isinstance(dcls, type) or not dc.is_dataclass(dcls):
            raise TypeError(dcls)

        try:
            return self._field_type_maps_by_dataclass[dcls]
        except KeyError:
            pass

        th = ta.get_type_hints(dcls)
        dct = {}
        for f in dc.fields(dcls):
            ignore_if = None
            try:
                ig = f.metadata[Ignore]
            except KeyError:
                ignore_if = None
            else:
                if callable(ig):
                    ignore_if = ig
                elif ig:
                    continue

            if GetType in f.metadata:
                fcls = f.metadata[GetType](dcls)
            else:
                fcls = th[f.name]
            dct[f.name] = _DataclassFieldSerde(fcls, ignore_if=ignore_if)

        self._field_type_maps_by_dataclass[dcls] = dct
        return dct

    def gen_dataclass_fields_serializer(self, cls: type) -> Serializer:
        sers = {}

        for fn, fs in self._get_dataclass_field_type_map(cls).items():
            sers[fn] = (fs, serde(fs.cls).serialize)

        def ser(obj):  # noqa
            dct = {}
            for fn, (fs, fser) in sers.items():
                v = getattr(obj, fn)
                if fs.ignore_if is not None and fs.ignore_if(v):
                    continue
                dct[fn] = fser(v)
            return dct

        return ser

    def serialize_dataclass_fields(self, obj: T) -> Serialized:
        return self.gen_dataclass_fields_serializer(type(obj))(obj)

    def gen_dataclass_fields_deserializer(self, dcls: type) -> Deserializer:
        fdct = self._get_dataclass_field_type_map(dcls)
        desers = {fn: serde(fs.cls).deserialize for fn, fs in fdct.items()}

        def des(ser):
            check.isinstance(ser, ta.Mapping)
            kw = {}
            for k, v in ser.items():
                fd = desers[k]
                kw[k] = fd(v)
            try:
                return dcls(**kw)
            except Exception as e:  # noqa
                raise

        return des

    def deserialize_dataclass_fields(self, ser: ta.Mapping[str, ta.Any], dcls: type) -> T:
        return self.gen_dataclass_fields_deserializer(dcls)(ser)

    def gen_dataclass_serde(self, cls: type, *, no_custom: bool = False) -> Serde:
        custom = get_simple_serde(cls) if not no_custom else None
        if custom is not None and custom.handles_polymorphism:
            return custom

        if self._is_monomorphic_dataclass(cls):
            if custom is not None:
                return custom
            else:
                return FnSerde(
                    self.gen_dataclass_fields_serializer(cls),
                    self.gen_dataclass_fields_deserializer(cls),
                )

        ser_scm = {}
        des_scm = {}
        for scls, snam in self.get_subclass_map(cls).items():
            if not isinstance(scls, type):
                continue

            custom = get_simple_serde(scls) if not no_custom else None

            if custom is not None and custom.handles_polymorphism:
                ser = custom.serialize
            else:
                sser = custom.serialize if custom is not None else self.gen_dataclass_fields_serializer(scls)
                ser = (lambda snam, sser: lambda obj: {snam: sser(obj)})(snam, sser)

            if custom is not None:
                des = custom.deserialize
            else:
                des = self.gen_dataclass_fields_deserializer(scls)

            ser_scm[scls] = ser
            des_scm[snam] = des

        def ser(obj):
            return ser_scm[type(obj)](obj)

        def des(ser):
            [[n, ser]] = check.isinstance(ser, ta.Mapping).items()
            return des_scm[n](ser)

        return FnSerde(ser, des)


_STATE = _DataclassSerdeState()


subclass_map_resolver_for = _STATE.subclass_map_resolver_for
format_subclass_name = _STATE.format_subclass_name
build_subclass_map = _STATE.build_subclass_map
get_subclass_map = _STATE.get_subclass_map
serialize_dataclass_fields = _STATE.serialize_dataclass_fields
deserialize_dataclass_fields = _STATE.deserialize_dataclass_fields
gen_dataclass_serde = _STATE.gen_dataclass_serde


@serde_gen(priority=True)
class DataclassSerdeGen:

    def __call__(self, spec: rfl.Spec) -> ta.Optional[Serde]:
        if isinstance(spec, rfl.TypeSpec) and dc.is_dataclass(spec.erased_cls):
            return gen_dataclass_serde(spec.erased_cls)
        else:
            return None
