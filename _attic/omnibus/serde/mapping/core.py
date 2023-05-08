"""
TODO:
 - ** (serializers|deserializers)_by_spec
 - strict mode
 - replace with builtin omni generic impl
 - extensible serde Contexts? want pluggable datatypes, -> Datatype.of
 - recursive custom serde?
 - allow_empty? system: {{}}


Jackson:
USE_ANNOTATIONS
AUTO_DETECT_CREATORS
AUTO_DETECT_FIELDS
AUTO_DETECT_GETTERS
AUTO_DETECT_IS_GETTERS
AUTO_DETECT_SETTERS
REQUIRE_SETTERS_FOR_GETTERS
USE_GETTERS_AS_SETTERS
INFER_CREATOR_FROM_CONSTRUCTOR_PROPERTIES
INFER_PROPERTY_MUTATORS
ALLOW_FINAL_FIELDS_AS_MUTATORS
ALLOW_VOID_VALUED_PROPERTIES
CAN_OVERRIDE_ACCESS_MODIFIERS
OVERRIDE_PUBLIC_ACCESS_MODIFIERS
SORT_PROPERTIES_ALPHABETICALLY
USE_WRAPPER_NAME_AS_PROPERTY_NAME
ACCEPT_CASE_INSENSITIVE_ENUMS
ACCEPT_CASE_INSENSITIVE_PROPERTIES
ACCEPT_CASE_INSENSITIVE_VALUES
ALLOW_EXPLICIT_PROPERTY_RENAMING
USE_STD_BEAN_NAMING
ALLOW_COERCION_OF_SCALARS
DEFAULT_VIEW_INCLUSION
IGNORE_DUPLICATE_MODULE_REGISTRATIONS
IGNORE_MERGE_FOR_UNMERGEABLE
USE_BASE_TYPE_AS_DEFAULT_IMPL
USE_STATIC_TYPING
BLOCK_UNSAFE_POLYMORPHIC_BASE_TYPES
"""
import typing as ta
import weakref

from ... import check
from ... import defs
from ... import reflect as rfl
from .types import DeserializationException
from .types import Serde
from .types import SerdeGen
from .types import Serialized


T = ta.TypeVar('T')


class _ProxySerde(Serde):

    def __init__(self, spec: rfl.Spec) -> None:
        super().__init__()

        self._spec = spec
        self._child: ta.Optional[Serde] = None

    defs.repr('_spec')

    def set(self, child: Serde) -> None:
        check.none(self._child)
        self._child = child

    def serialize(self, obj: T) -> ta.Any:
        return self._child.serialize(obj)

    def deserialize(self, ser: ta.Any) -> T:
        return self._child.deserialize(ser)


class _SerdeState:

    def __init__(self) -> None:
        super().__init__()

        self._priority_serde_gens: ta.MutableSequence[SerdeGen] = []
        self._serde_gens: ta.MutableSequence[SerdeGen] = []

        self._serdes_by_spec: ta.MutableMapping[rfl.Spec, Serde] = weakref.WeakKeyDictionary()
        self._proxies_by_spec: ta.MutableMapping[rfl.Spec, _ProxySerde] = {}

    def register_serde_gen(self, serde_gen: SerdeGen, priority: bool = False) -> None:
        check.callable(serde_gen)
        if priority:
            self._priority_serde_gens.append(serde_gen)
        else:
            self._serde_gens.append(serde_gen)

    def _gen_serde(self, spec: rfl.Spec) -> Serde:
        check.isinstance(spec, rfl.Spec)

        for g in self._priority_serde_gens:
            s = g(spec)
            if s:
                return s

        matches = [s for g in self._serde_gens for s in [g(spec)] if s is not None]
        if matches:
            return check.single(matches)

        raise TypeError(spec)

    def serde(self, spec: ta.Optional[ta.Any]) -> Serde:
        spec = rfl.spec(spec)

        try:
            return self._serdes_by_spec[spec]
        except KeyError:
            pass

        try:
            return self._proxies_by_spec[spec]
        except KeyError:
            pass

        try:
            prx = self._proxies_by_spec[spec] = _ProxySerde(spec)
            sd = self._gen_serde(spec)
            self._serdes_by_spec[spec] = sd
            prx.set(sd)
        finally:
            del self._proxies_by_spec[spec]

        return sd

    def serialize(self, obj: T, spec: ta.Optional[ta.Any] = None) -> Serialized:
        return self.serde(spec if spec is not None else type(obj)).serialize(obj)

    _NO_RERAISE = False
    # _NO_RERAISE = True

    def deserialize(self, ser: Serialized, spec: ta.Any, no_reraise: bool = False) -> T:
        spec = rfl.spec(spec)
        if no_reraise or self._NO_RERAISE:
            return self.serde(spec).deserialize(ser)
        else:
            try:
                return self.serde(spec).deserialize(ser)
            except Exception as e:
                raise DeserializationException(spec=spec, ser=ser) from e


_STATE = _SerdeState()


def serde_gen(*, priority: bool = False):
    def inner(obj):
        if isinstance(obj, type):
            sd = obj()
        else:
            sd = obj
        _STATE.register_serde_gen(sd, priority=priority)
        return obj
    return inner


serde = _STATE.serde
serialize = _STATE.serialize
deserialize = _STATE.deserialize
