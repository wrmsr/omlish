"""
TODO:
 - FIXME: types - generics
"""
import collections.abc
import enum
import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from .core import serde
from .core import serde_gen
from .types import InstanceSerdeGen
from .types import PRIMITIVE_TYPES_TUPLE


T = ta.TypeVar('T')


@serde_gen()
class OptionalSerdeGen(InstanceSerdeGen):

    def match(self, spec: rfl.Spec) -> bool:
        return isinstance(spec, rfl.UnionSpec) and spec.optional_arg is not None

    class Instance(InstanceSerdeGen.Instance):

        def __init__(self, spec: rfl.Spec) -> None:
            super().__init__(spec)

            spec = check.isinstance(spec, rfl.UnionSpec)
            self._child = serde(spec.optional_arg)

        def serialize(self, obj: T) -> ta.Any:
            return None if obj is None else self._child.serialize(obj)

        def deserialize(self, ser: ta.Any) -> T:
            return None if ser is None else self._child.deserialize(ser)


@serde_gen()
class AnySerdeGen(InstanceSerdeGen):

    def match(self, spec: rfl.Spec) -> bool:
        return isinstance(spec, rfl.AnySpec)

    class Instance(InstanceSerdeGen.Instance):

        def serialize(self, obj: T) -> ta.Any:
            if isinstance(obj, PRIMITIVE_TYPES_TUPLE):
                return obj
            else:
                raise TypeError(obj)

        def deserialize(self, ser: ta.Any) -> T:
            if isinstance(ser, PRIMITIVE_TYPES_TUPLE):
                return ser
            else:
                raise TypeError(ser)


@serde_gen()
class MappingSerdeGen(InstanceSerdeGen):

    def match(self, spec: rfl.Spec) -> bool:
        return isinstance(spec, rfl.GenericTypeSpec) and spec.erased_cls is collections.abc.Mapping

    class Instance(InstanceSerdeGen.Instance):

        def __init__(self, spec: rfl.Spec) -> None:
            super().__init__(spec)

            spec = check.isinstance(spec, rfl.GenericTypeSpec)
            kspec, vspec = spec.args
            self._kchild = serde(kspec)
            self._vchild = serde(vspec)

        def serialize(self, obj: T) -> ta.Any:
            return [[self._kchild.serialize(k), self._vchild.serialize(v)] for k, v in obj.items()]

        def deserialize(self, ser: ta.Any) -> T:
            dct = {}
            if isinstance(ser, str):
                raise TypeError(ser)
            elif isinstance(ser, collections.abc.Mapping):
                for kser, vser in ser.items():
                    k, v = self._kchild.deserialize(kser), self._vchild.deserialize(vser)
                    if k in dct:
                        raise KeyError(k)
                    dct[k] = v
            elif isinstance(ser, collections.abc.Sequence):
                for e in ser:
                    if not isinstance(e, collections.abc.Sequence) or isinstance(e, str):
                        raise TypeError(e)
                    kser, vser = e
                    k, v = self._kchild.deserialize(kser), self._vchild.deserialize(vser)
                    if k in dct:
                        raise KeyError(k)
                    dct[k] = v
            else:
                raise TypeError(ser)
            return dct


@serde_gen()
class SequenceSerdeGen(InstanceSerdeGen):

    def match(self, spec: rfl.Spec) -> bool:
        return isinstance(spec, rfl.GenericTypeSpec) and spec.erased_cls is collections.abc.Sequence

    class Instance(InstanceSerdeGen.Instance):

        def __init__(self, spec: rfl.Spec) -> None:
            super().__init__(spec)

            spec = check.isinstance(spec, rfl.GenericTypeSpec)
            [espec] = spec.args
            self._child = serde(espec)

        def serialize(self, obj: T) -> ta.Any:
            return [self._child.serialize(e) for e in obj]

        def deserialize(self, ser: ta.Any) -> T:
            if not isinstance(ser, collections.abc.Sequence) or isinstance(ser, str):
                raise TypeError(ser)
            return [self._child.deserialize(e) for e in ser]


@serde_gen()
class SetSerdeGen(InstanceSerdeGen):

    def match(self, spec: rfl.Spec) -> bool:
        return isinstance(spec, rfl.GenericTypeSpec) and spec.erased_cls is collections.abc.Set

    class Instance(InstanceSerdeGen.Instance):

        def __init__(self, spec: rfl.Spec) -> None:
            super().__init__(spec)

            spec = check.isinstance(spec, rfl.GenericTypeSpec)
            [espec] = spec.args
            self._child = serde(espec)

        def serialize(self, obj: T) -> ta.Any:
            return [self._child.serialize(e) for e in obj]

        def deserialize(self, ser: ta.Any) -> T:
            return {self._child.deserialize(e) for e in ser}


@serde_gen()
class TupleSerdeGen(InstanceSerdeGen):

    def match(self, spec: rfl.Spec) -> bool:
        return isinstance(spec, rfl.TupleTypeSpec)

    class Instance(InstanceSerdeGen.Instance):

        def __init__(self, spec: rfl.Spec) -> None:
            super().__init__(spec)

            spec = check.isinstance(spec, rfl.TupleTypeSpec)
            self._children = [serde(e) for e in spec.args]

        def serialize(self, obj: T) -> ta.Any:
            if not isinstance(obj, tuple) or len(obj) != self._children:
                raise TypeError(obj)
            return[c.serialize(e) for c, e in zip(self._children, obj)]

        def deserialize(self, ser: ta.Any) -> T:
            if isinstance(ser, str) or len(ser) != self._children:
                raise TypeError(ser)
            return[c.deserialize(e) for c, e in zip(self._children, ser)]


@serde_gen()
class EnumSerdeGen(InstanceSerdeGen):

    def match(self, spec: rfl.Spec) -> bool:
        return isinstance(spec, rfl.NonGenericTypeSpec) and issubclass(spec.erased_cls, enum.Enum)

    class Instance(InstanceSerdeGen.Instance):

        def __init__(self, spec: rfl.Spec) -> None:
            super().__init__(spec)

            spec = check.isinstance(spec, rfl.TypeSpec)
            self._cls = check.isinstance(spec.erased_cls, enum.EnumMeta)

        def serialize(self, obj: T) -> ta.Any:
            return obj.name

        def deserialize(self, ser: ta.Any) -> T:
            return self._cls.__members__[check.isinstance(ser, str)]


@serde_gen()
class PrimitiveSerdeGen(InstanceSerdeGen):

    def match(self, spec: rfl.Spec) -> bool:
        return isinstance(spec, rfl.NonGenericTypeSpec) and issubclass(spec.erased_cls, PRIMITIVE_TYPES_TUPLE)

    class Instance(InstanceSerdeGen.Instance):

        def __init__(self, spec: rfl.Spec) -> None:
            super().__init__(spec)

            spec = check.isinstance(spec, rfl.NonGenericTypeSpec)
            self._cls = spec.erased_cls

            self.serialize = lang.identity

        def serialize(self, obj: T) -> ta.Any:
            return obj

        def deserialize(self, ser: ta.Any) -> T:
            if isinstance(ser, self._cls):
                return ser
            elif isinstance(ser, str):
                return self._cls(ser)
            else:
                raise TypeError(ser)


@serde_gen()
class CallableSerdeGen(InstanceSerdeGen):

    def match(self, spec: rfl.Spec) -> bool:
        return (
                isinstance(spec, rfl.SpecialParameterizedGenericTypeSpec)
                and spec.erased_cls is collections.abc.Callable
        )

    class Instance(InstanceSerdeGen.Instance):

        def serialize(self, obj: T) -> ta.Any:
            raise TypeError

        def deserialize(self, ser: ta.Any) -> T:
            return check.callable(ser)


@serde_gen()
class RedactedSerdeGen(InstanceSerdeGen):

    def match(self, spec: rfl.Spec) -> bool:
        return isinstance(spec, rfl.GenericTypeSpec) and spec.erased_cls is lang.Redacted

    class Instance(InstanceSerdeGen.Instance):

        def __init__(self, spec: rfl.Spec) -> None:
            super().__init__(spec)

            spec = check.isinstance(spec, rfl.GenericTypeSpec)
            [espec] = spec.args
            self._child = serde(espec)

        def serialize(self, obj: T) -> ta.Any:
            return self._child.serialize(obj.value)

        def deserialize(self, ser: ta.Any) -> T:
            return lang.redact(self._child.deserialize(ser))
