# ruff: noqa: SLF001
import dataclasses as dc
import io
import typing as ta

from ..errors import ReflectionError
from ..errors import ReflectionRuntimeError
from ..errors import ReflectionTypeError
from .symbols import ArgKind
from .symbols import TypeAlias
from .types import AnnotatedType
from .types import AnyType
from .types import CallableArgument
from .types import CallableType
from .types import DeletedType
from .types import EllipsisType
from .types import ErasedType
from .types import Instance
from .types import LiteralType
from .types import NoneType
from .types import Overloaded
from .types import Parameters
from .types import ParamSpecType
from .types import PartialType
from .types import PlaceholderType
from .types import RawExpressionType
from .types import ReadOnlyType
from .types import RequiredType
from .types import TupleType
from .types import Type
from .types import TypeAliasType
from .types import TypedDictType
from .types import TypeGuardedType
from .types import TypeList
from .types import TypeOfAny
from .types import TypeType
from .types import TypeVarLikeType
from .types import TypeVarTupleType
from .types import TypeVarType
from .types import UnboundType
from .types import UninhabitedType
from .types import UnionType
from .types import UnpackType
from .typevisitor import DefaultTypeVisitor


TypeKey = ta.NewType('TypeKey', object)
TupleTypeKey: ta.TypeAlias = tuple[object, ...]


##


@dc.dataclass(frozen=True)
class TypeKeyPolicy:
    alpha: bool = False
    structural: bool = False
    include_annotated_metadata: bool = True
    preserve_alias_identity: bool = True
    preserve_newtype_identity: bool = True


_TYPE_KEY_POLICY: ta.Final = TypeKeyPolicy()
_ALPHA_TYPE_KEY_POLICY: ta.Final = dc.replace(_TYPE_KEY_POLICY, alpha=True)
_STRUCTURAL_TYPE_KEY_POLICY: ta.Final = TypeKeyPolicy(
    structural=True,
    include_annotated_metadata=False,
    preserve_alias_identity=False,
)
_ALPHA_STRUCTURAL_TYPE_KEY_POLICY: ta.Final = dc.replace(_STRUCTURAL_TYPE_KEY_POLICY, alpha=True)


##


def _is_hashable(obj: object) -> bool:
    try:
        hash(obj)
    except TypeError:
        return False
    return True


def type_key(typ: Type) -> TypeKey:
    key = type_key_or_none(typ)
    if key is None:
        raise ReflectionTypeError(f'Type key is not implemented for type: {typ!r}')
    return key


def type_key_or_none(typ: Type) -> TypeKey | None:
    return type_key_with_policy_or_none(typ, _TYPE_KEY_POLICY)


def type_key_with_policy(typ: Type, policy: TypeKeyPolicy) -> TypeKey:
    key = type_key_with_policy_or_none(typ, policy)
    if key is None:
        raise ReflectionTypeError(f'Type key is not implemented for type: {typ!r}')
    return key


def type_key_with_policy_or_none(typ: Type, policy: TypeKeyPolicy) -> TypeKey | None:
    return _TypeKeyBuilder(_StringTypeKeyWriter(), policy).key(typ)


def _type_key_with_policy_or_none(typ: Type, policy: TypeKeyPolicy) -> TypeKey | None:
    return type_key_with_policy_or_none(typ, policy)


def alpha_type_key(typ: Type) -> TypeKey:
    key = alpha_type_key_or_none(typ)
    if key is None:
        raise ReflectionTypeError(f'Alpha type key is not implemented for type: {typ!r}')
    return key


def alpha_type_key_or_none(typ: Type) -> TypeKey | None:
    return type_key_with_policy_or_none(typ, _ALPHA_TYPE_KEY_POLICY)


def structural_type_key(typ: Type) -> TypeKey:
    key = structural_type_key_or_none(typ)
    if key is None:
        raise ReflectionTypeError(f'Structural type key is not implemented for type: {typ!r}')
    return key


def structural_type_key_or_none(typ: Type) -> TypeKey | None:
    return type_key_with_policy_or_none(typ, _STRUCTURAL_TYPE_KEY_POLICY)


def alpha_structural_type_key(typ: Type) -> TypeKey:
    key = alpha_structural_type_key_or_none(typ)
    if key is None:
        raise ReflectionTypeError(f'Alpha structural type key is not implemented for type: {typ!r}')
    return key


def alpha_structural_type_key_or_none(typ: Type) -> TypeKey | None:
    return type_key_with_policy_or_none(typ, _ALPHA_STRUCTURAL_TYPE_KEY_POLICY)


def _tuple_type_key(typ: Type) -> TupleTypeKey:
    key = _tuple_type_key_or_none(typ)
    if key is None:
        raise ReflectionTypeError(f'Tuple type key is not implemented for type: {typ!r}')
    return key


def _tuple_type_key_or_none(typ: Type) -> TupleTypeKey | None:
    return tuple_type_key_with_policy_or_none(typ, _TYPE_KEY_POLICY)


def tuple_type_key_with_policy(typ: Type, policy: TypeKeyPolicy) -> TupleTypeKey:
    key = tuple_type_key_with_policy_or_none(typ, policy)
    if key is None:
        raise ReflectionTypeError(f'Tuple type key is not implemented for type: {typ!r}')
    return key


def tuple_type_key_with_policy_or_none(typ: Type, policy: TypeKeyPolicy) -> TupleTypeKey | None:
    return _TypeKeyBuilder(_TupleTypeKeyWriter(), policy).key(typ)


def _tuple_type_key_with_policy_or_none(typ: Type, policy: TypeKeyPolicy) -> TupleTypeKey | None:
    return tuple_type_key_with_policy_or_none(typ, policy)


##


class _TypeKeyWriter:
    def annotated_key(self, item_key: object, metadata: tuple[object, ...]) -> object | None:
        raise NotImplementedError

    def required_key(self, item_key: object, required: bool) -> object:
        raise NotImplementedError

    def readonly_key(self, item_key: object) -> object:
        raise NotImplementedError

    def type_var_like_key(self, tag: str, namespace: str, raw_id: int, meta_level: int) -> object:
        raise NotImplementedError

    def alpha_type_var_like_key(self, tag: str, index: int) -> object:
        raise NotImplementedError

    def unbound_key(self, name: str, arg_keys: tuple[object, ...]) -> object:
        raise NotImplementedError

    def callable_argument_key(self, item_key: object, name: str | None, constructor: str | None) -> object:
        raise NotImplementedError

    def type_list_key(self, item_keys: tuple[object, ...]) -> object:
        raise NotImplementedError

    def unpack_key(self, item_key: object) -> object:
        raise NotImplementedError

    def any_key(self, type_of_any: TypeOfAny) -> object:
        raise NotImplementedError

    def uninhabited_key(self) -> object:
        raise NotImplementedError

    def none_key(self) -> object:
        raise NotImplementedError

    def erased_key(self) -> object:
        raise NotImplementedError

    def deleted_key(self, source: str | None) -> object:
        raise NotImplementedError

    def instance_key(
            self,
            fullname: str,
            arg_keys: tuple[object, ...],
            last_known_value_key: object | None,
    ) -> object:
        raise NotImplementedError

    def parameters_key(
            self,
            arg_keys: tuple[object, ...],
            arg_kinds: list[ArgKind],
            arg_names: list[str | None],
    ) -> object:
        raise NotImplementedError

    def callable_key(
            self,
            arg_keys: tuple[object, ...],
            arg_kinds: list[ArgKind],
            arg_names: list[str | None],
            ret_key: object,
            fallback_key: object,
            variable_keys: tuple[object, ...],
            is_ellipsis_args: bool,
    ) -> object:
        raise NotImplementedError

    def overloaded_key(self, item_keys: tuple[object, ...]) -> object:
        raise NotImplementedError

    def tuple_key(self, item_keys: tuple[object, ...], fallback_key: object) -> object:
        raise NotImplementedError

    def typed_dict_key(
            self,
            item_keys: tuple[tuple[str, object], ...],
            required_keys: set[str],
            readonly_keys: set[str],
            fallback_key: object,
    ) -> object:
        raise NotImplementedError

    def literal_key(self, value: object, fallback_key: object) -> object | None:
        raise NotImplementedError

    def raw_expression_key(self, literal_value: object, base_type_name: str) -> object | None:
        raise NotImplementedError

    def union_key(self, item_keys: tuple[object, ...]) -> object | None:
        raise NotImplementedError

    def ellipsis_key(self) -> object:
        raise NotImplementedError

    def type_type_key(self, item_key: object) -> object:
        raise NotImplementedError

    def placeholder_key(self, fullname: str, arg_keys: tuple[object, ...]) -> object:
        raise NotImplementedError

    def alias_ref_key(self, index: int, arg_keys: tuple[object, ...]) -> object:
        raise NotImplementedError

    def type_alias_key(
            self,
            fullname: str,
            identity: object | None,
            arg_keys: tuple[object, ...],
            target_key: object,
    ) -> object | None:
        raise NotImplementedError

    def recursive_type_alias_key(self, arg_keys: tuple[object, ...], target_key: object) -> object:
        raise NotImplementedError


#


class _TypeKeyFragment:
    __slots__ = (
        'text',
        'refs',
    )

    def __init__(self, text: str, refs: tuple[object, ...] = ()) -> None:
        super().__init__()

        self.text = text
        self.refs = refs

    def finish(self) -> TypeKey:
        if not self.refs:
            return TypeKey(self.text)
        return TypeKey((self.text, *self.refs))


def _literal_scalar_text(value: object) -> str | None:
    if value is None:
        return 'None:'
    if isinstance(value, bool):
        return f'bool:{value!r}'
    if type(value) is int:
        return f'int:{value!r}'
    if type(value) is str:
        return f'str:{value!r}'
    if type(value) is bytes:
        return f'bytes:{value!r}'
    return None


def _fragment_sort_text(fragment: _TypeKeyFragment) -> str:
    text = fragment.text
    for index, tag in enumerate(('None', 'bool', 'int', 'str', 'bytes')):
        if text.startswith(f'L[{tag}:'):
            return f'L[{index}:{text}'
    return text


class _StringFragmentWriter:
    def __init__(self) -> None:
        super().__init__()

        self._buf = io.StringIO()
        self._refs: list[object] = []
        self._needs_sep: list[bool] = []

    def _sep(self) -> None:
        if self._needs_sep:
            if self._needs_sep[-1]:
                self._buf.write(',')
            else:
                self._needs_sep[-1] = True

    def begin(self, tag: str) -> None:
        self._sep()
        self._buf.write(tag)
        self._buf.write('[')
        self._needs_sep.append(False)

    def end(self) -> None:
        if not self._needs_sep:
            raise ReflectionRuntimeError('Type key writer stack underflow')
        self._buf.write(']')
        self._needs_sep.pop()

    def atom(self, value: str) -> None:
        self._sep()
        self._buf.write(value)

    def string(self, value: str) -> None:
        self.atom(repr(value))

    def fragment(self, fragment: _TypeKeyFragment) -> None:
        self._sep()
        self._buf.write(fragment.text)
        self._refs.extend(fragment.refs)

    def ref(self, obj: object) -> bool:
        if not _is_hashable(obj):
            return False
        self._sep()
        self._buf.write(f'${len(self._refs)}')
        self._refs.append(obj)
        return True

    def finish(self) -> _TypeKeyFragment:
        if self._needs_sep:
            raise ReflectionRuntimeError('Type key writer stack is not empty')
        return _TypeKeyFragment(self._buf.getvalue(), tuple(self._refs))


class _StringTypeKeyWriter(_TypeKeyWriter):
    def _node(self, tag: str, *items: object) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin(tag)
        for item in items:
            self._write_item(w, item)
        w.end()
        return w.finish()

    def _write_item(self, w: _StringFragmentWriter, item: object) -> None:
        if isinstance(item, _TypeKeyFragment):
            w.fragment(item)
        elif isinstance(item, str):
            w.atom(item)
        else:
            raise ReflectionTypeError(item)

    def annotated_key(self, item_key: object, metadata: tuple[object, ...]) -> _TypeKeyFragment | None:
        if not _is_hashable(metadata):
            return None
        w = _StringFragmentWriter()
        w.begin('Ann')
        w.fragment(ta.cast(_TypeKeyFragment, item_key))
        if not w.ref(metadata):
            return None
        w.end()
        return w.finish()

    def required_key(self, item_key: object, required: bool) -> _TypeKeyFragment:
        return self._node('Req', str(required), item_key)

    def readonly_key(self, item_key: object) -> _TypeKeyFragment:
        return self._node('RO', item_key)

    def type_var_like_key(self, tag: str, namespace: str, raw_id: int, meta_level: int) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin(tag)
        w.atom(str(raw_id))
        if namespace:
            w.atom('ns')
            w.string(namespace)
        if meta_level:
            w.atom('meta')
            w.atom(str(meta_level))
        w.end()
        return w.finish()

    def alpha_type_var_like_key(self, tag: str, index: int) -> _TypeKeyFragment:
        return _TypeKeyFragment(f'A{tag}[{index}]')

    def unbound_key(self, name: str, arg_keys: tuple[object, ...]) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin('Unbound')
        w.string(name)
        for arg_key in arg_keys:
            w.fragment(ta.cast(_TypeKeyFragment, arg_key))
        w.end()
        return w.finish()

    def callable_argument_key(
            self,
            item_key: object,
            name: str | None,
            constructor: str | None,
    ) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin('CA')
        w.fragment(ta.cast(_TypeKeyFragment, item_key))
        if name is not None:
            w.atom('name')
            w.string(name)
        if constructor is not None:
            w.atom('ctor')
            w.string(constructor)
        w.end()
        return w.finish()

    def type_list_key(self, item_keys: tuple[object, ...]) -> _TypeKeyFragment:
        return self._node('TL', *item_keys)

    def unpack_key(self, item_key: object) -> _TypeKeyFragment:
        return self._node('Unpack', item_key)

    def any_key(self, type_of_any: TypeOfAny) -> _TypeKeyFragment:
        return _TypeKeyFragment('Any' if type_of_any is TypeOfAny.EXPLICIT else f'Any[{type_of_any}]')

    def uninhabited_key(self) -> _TypeKeyFragment:
        return _TypeKeyFragment('Never')

    def none_key(self) -> _TypeKeyFragment:
        return _TypeKeyFragment('None')

    def erased_key(self) -> _TypeKeyFragment:
        return _TypeKeyFragment('Erased')

    def deleted_key(self, source: str | None) -> _TypeKeyFragment:
        if source is None:
            return _TypeKeyFragment('Deleted')
        w = _StringFragmentWriter()
        w.begin('Deleted')
        w.string(source)
        w.end()
        return w.finish()

    def instance_key(
            self,
            fullname: str,
            arg_keys: tuple[object, ...],
            last_known_value_key: object | None,
    ) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin('I')
        w.string(fullname)
        for arg_key in arg_keys:
            w.fragment(ta.cast(_TypeKeyFragment, arg_key))
        if last_known_value_key is not None:
            w.atom('lkv')
            w.fragment(ta.cast(_TypeKeyFragment, last_known_value_key))
        w.end()
        return w.finish()

    def parameters_key(
            self,
            arg_keys: tuple[object, ...],
            arg_kinds: list[ArgKind],
            arg_names: list[str | None],
    ) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin('P')
        for arg_key in arg_keys:
            w.fragment(ta.cast(_TypeKeyFragment, arg_key))
        w.begin('k')
        for kind in arg_kinds:
            w.atom(kind.name)
        w.end()
        w.begin('n')
        for name in arg_names:
            w.atom('None' if name is None else repr(name))
        w.end()
        w.end()
        return w.finish()

    def callable_key(
            self,
            arg_keys: tuple[object, ...],
            arg_kinds: list[ArgKind],
            arg_names: list[str | None],
            ret_key: object,
            fallback_key: object,
            variable_keys: tuple[object, ...],
            is_ellipsis_args: bool,
    ) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin('C')
        for arg_key in arg_keys:
            w.fragment(ta.cast(_TypeKeyFragment, arg_key))
        w.begin('k')
        for kind in arg_kinds:
            w.atom(kind.name)
        w.end()
        w.begin('n')
        for name in arg_names:
            w.atom('None' if name is None else repr(name))
        w.end()
        w.begin('r')
        w.fragment(ta.cast(_TypeKeyFragment, ret_key))
        w.end()
        w.begin('f')
        w.fragment(ta.cast(_TypeKeyFragment, fallback_key))
        w.end()
        if variable_keys:
            w.begin('v')
            for variable_key in variable_keys:
                w.fragment(ta.cast(_TypeKeyFragment, variable_key))
            w.end()
        if is_ellipsis_args:
            w.atom('ellipsis')
        w.end()
        return w.finish()

    def overloaded_key(self, item_keys: tuple[object, ...]) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin('O')
        for item_key in item_keys:
            w.fragment(ta.cast(_TypeKeyFragment, item_key))
        w.end()
        return w.finish()

    def tuple_key(self, item_keys: tuple[object, ...], fallback_key: object) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin('Tuple')
        for item_key in item_keys:
            w.fragment(ta.cast(_TypeKeyFragment, item_key))
        w.fragment(ta.cast(_TypeKeyFragment, fallback_key))
        w.end()
        return w.finish()

    def typed_dict_key(
            self,
            item_keys: tuple[tuple[str, object], ...],
            required_keys: set[str],
            readonly_keys: set[str],
            fallback_key: object,
    ) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin('TD')
        for name, item_key in item_keys:
            w.begin('i')
            w.string(name)
            w.fragment(ta.cast(_TypeKeyFragment, item_key))
            w.end()
        if required_keys:
            w.begin('req')
            for key in sorted(required_keys):
                w.string(key)
            w.end()
        if readonly_keys:
            w.begin('ro')
            for key in sorted(readonly_keys):
                w.string(key)
            w.end()
        w.begin('f')
        w.fragment(ta.cast(_TypeKeyFragment, fallback_key))
        w.end()
        w.end()
        return w.finish()

    def literal_key(self, value: object, fallback_key: object) -> _TypeKeyFragment | None:
        w = _StringFragmentWriter()
        w.begin('L')
        scalar_text = _literal_scalar_text(value)
        if scalar_text is None:
            if not w.ref(value):
                return None
        else:
            w.atom(scalar_text)
        w.fragment(ta.cast(_TypeKeyFragment, fallback_key))
        w.end()
        return w.finish()

    def raw_expression_key(self, literal_value: object, base_type_name: str) -> _TypeKeyFragment | None:
        w = _StringFragmentWriter()
        w.begin('Raw')
        if literal_value is None:
            w.atom('None')
        else:
            scalar_text = _literal_scalar_text(literal_value)
            if scalar_text is None:
                if not w.ref(literal_value):
                    return None
            else:
                w.atom(scalar_text)
        w.string(base_type_name)
        w.end()
        return w.finish()

    def union_key(self, item_keys: tuple[object, ...]) -> _TypeKeyFragment | None:
        fragments = tuple(ta.cast(_TypeKeyFragment, item_key) for item_key in item_keys)
        string_fragments = [fragment for fragment in fragments if not fragment.refs]
        opaque_fragment_keys = frozenset(
            fragment.finish()
            for fragment in fragments
            if fragment.refs
        )

        w = _StringFragmentWriter()
        w.begin('U')
        for fragment in sorted(string_fragments, key=_fragment_sort_text):
            w.fragment(fragment)
        if opaque_fragment_keys:
            w.begin('OU')
            if not w.ref(opaque_fragment_keys):
                return None
            w.end()
        w.end()
        return w.finish()

    def type_type_key(self, item_key: object) -> _TypeKeyFragment:
        return self._node('Type', item_key)

    def ellipsis_key(self) -> _TypeKeyFragment:
        return _TypeKeyFragment('Ellipsis')

    def placeholder_key(self, fullname: str, arg_keys: tuple[object, ...]) -> _TypeKeyFragment:
        w = _StringFragmentWriter()
        w.begin('Placeholder')
        w.string(fullname)
        for arg_key in arg_keys:
            w.fragment(ta.cast(_TypeKeyFragment, arg_key))
        w.end()
        return w.finish()

    def alias_ref_key(self, index: int, arg_keys: tuple[object, ...]) -> _TypeKeyFragment:
        return self._node('AR', str(index), *arg_keys)

    def type_alias_key(
            self,
            fullname: str,
            identity: object | None,
            arg_keys: tuple[object, ...],
            target_key: object,
    ) -> _TypeKeyFragment | None:
        w = _StringFragmentWriter()
        w.begin('A')
        w.string(fullname)
        if identity is not None:
            if not w.ref(identity):
                return None
        for arg_key in arg_keys:
            w.fragment(ta.cast(_TypeKeyFragment, arg_key))
        w.fragment(ta.cast(_TypeKeyFragment, target_key))
        w.end()
        return w.finish()

    def recursive_type_alias_key(self, arg_keys: tuple[object, ...], target_key: object) -> _TypeKeyFragment:
        return self._node('RA', *arg_keys, target_key)

    def finish(self, key: object) -> TypeKey:
        return ta.cast(_TypeKeyFragment, key).finish()


#


class _TupleTypeKeyWriter(_TypeKeyWriter):
    def annotated_key(self, item_key: object, metadata: tuple[object, ...]) -> TupleTypeKey | None:
        if not _is_hashable(metadata):
            return None
        return ('annotated', item_key, metadata)

    def required_key(self, item_key: object, required: bool) -> TupleTypeKey:
        return ('required', required, item_key)

    def readonly_key(self, item_key: object) -> TupleTypeKey:
        return ('readonly', item_key)

    def type_var_like_key(self, tag: str, namespace: str, raw_id: int, meta_level: int) -> TupleTypeKey:
        return (self._type_var_tag(tag), namespace, raw_id, meta_level)

    def alpha_type_var_like_key(self, tag: str, index: int) -> TupleTypeKey:
        return (self._type_var_tag(tag), index)

    def unbound_key(self, name: str, arg_keys: tuple[object, ...]) -> TupleTypeKey:
        return ('unbound', name, arg_keys)

    def callable_argument_key(
            self,
            item_key: object,
            name: str | None,
            constructor: str | None,
    ) -> TupleTypeKey:
        return ('callable_argument', item_key, name, constructor)

    def type_list_key(self, item_keys: tuple[object, ...]) -> TupleTypeKey:
        return ('type_list', item_keys)

    def unpack_key(self, item_key: object) -> TupleTypeKey:
        return ('unpack', item_key)

    def any_key(self, type_of_any: TypeOfAny) -> TupleTypeKey:
        return ('any', type_of_any)

    def uninhabited_key(self) -> TupleTypeKey:
        return ('uninhabited',)

    def none_key(self) -> TupleTypeKey:
        return ('none',)

    def erased_key(self) -> TupleTypeKey:
        return ('erased',)

    def deleted_key(self, source: str | None) -> TupleTypeKey:
        return ('deleted', source)

    def instance_key(
            self,
            fullname: str,
            arg_keys: tuple[object, ...],
            last_known_value_key: object | None,
    ) -> TupleTypeKey:
        return ('instance', fullname, arg_keys, () if last_known_value_key is None else last_known_value_key)

    def parameters_key(
            self,
            arg_keys: tuple[object, ...],
            arg_kinds: list[ArgKind],
            arg_names: list[str | None],
    ) -> TupleTypeKey:
        return ('parameters', arg_keys, tuple(arg_kinds), tuple(arg_names))

    def callable_key(
            self,
            arg_keys: tuple[object, ...],
            arg_kinds: list[ArgKind],
            arg_names: list[str | None],
            ret_key: object,
            fallback_key: object,
            variable_keys: tuple[object, ...],
            is_ellipsis_args: bool,
    ) -> TupleTypeKey:
        return (
            'callable',
            arg_keys,
            tuple(arg_kinds),
            tuple(arg_names),
            ret_key,
            fallback_key,
            variable_keys,
            is_ellipsis_args,
        )

    def overloaded_key(self, item_keys: tuple[object, ...]) -> TupleTypeKey:
        return ('overloaded', item_keys)

    def tuple_key(self, item_keys: tuple[object, ...], fallback_key: object) -> TupleTypeKey:
        return ('tuple', item_keys, fallback_key)

    def typed_dict_key(
            self,
            item_keys: tuple[tuple[str, object], ...],
            required_keys: set[str],
            readonly_keys: set[str],
            fallback_key: object,
    ) -> TupleTypeKey:
        return ('typed_dict', item_keys, frozenset(required_keys), frozenset(readonly_keys), fallback_key)

    def literal_key(self, value: object, fallback_key: object) -> TupleTypeKey | None:
        if not _is_hashable(value):
            return None
        return ('literal', type(value), value, fallback_key)

    def raw_expression_key(self, literal_value: object, base_type_name: str) -> TupleTypeKey | None:
        if not _is_hashable(literal_value):
            return None
        return ('raw_expression', literal_value, base_type_name)

    def union_key(self, item_keys: tuple[object, ...]) -> TupleTypeKey:
        return ('union', frozenset(item_keys))

    def ellipsis_key(self) -> TupleTypeKey:
        return ('ellipsis',)

    def type_type_key(self, item_key: object) -> TupleTypeKey:
        return ('type_type', item_key)

    def placeholder_key(self, fullname: str, arg_keys: tuple[object, ...]) -> TupleTypeKey:
        return ('placeholder', fullname, arg_keys)

    def alias_ref_key(self, index: int, arg_keys: tuple[object, ...]) -> TupleTypeKey:
        return ('type_alias_ref', index, arg_keys)

    def type_alias_key(
            self,
            fullname: str,
            identity: object | None,
            arg_keys: tuple[object, ...],
            target_key: object,
    ) -> TupleTypeKey:
        return ('type_alias', fullname, identity, arg_keys, target_key)

    def recursive_type_alias_key(self, arg_keys: tuple[object, ...], target_key: object) -> TupleTypeKey:
        return ('recursive_type_alias', arg_keys, target_key)

    def finish(self, key: object) -> TupleTypeKey:
        return ta.cast(TupleTypeKey, key)

    def _type_var_tag(self, tag: str) -> str:
        if tag == 'TV':
            return 'type_var'
        if tag == 'PS':
            return 'param_spec'
        if tag == 'TVT':
            return 'type_var_tuple'
        raise ReflectionTypeError(tag)


##


class _CollectRecursiveAliasTypesVisitor(DefaultTypeVisitor[None]):
    __slots__ = (
        'collected',
        'seen_aliases',
        'seen_types',
    )

    def __init__(self) -> None:
        super().__init__()

        self.collected: list[TypeAliasType] = []
        self.seen_aliases: set[TypeAlias] = set()
        self.seen_types: set[int] = set()

    def collect(self, typ: Type) -> None:
        type_id = id(typ)
        if type_id in self.seen_types:
            return
        self.seen_types.add(type_id)

        typ.accept(self)

    def collect_many(self, typs: ta.Iterable[Type]) -> None:
        for typ in typs:
            self.collect(typ)

    def visit_type(self, typ: Type) -> None:
        pass

    def visit_type_guarded_type(self, typ: TypeGuardedType) -> None:
        self.collect(typ._type_guard)

    def visit_annotated_type(self, typ: AnnotatedType) -> None:
        self.collect(typ._item)

    def visit_type_alias_type(self, typ: TypeAliasType) -> None:
        if typ._alias is not None and typ.is_recursive and typ._alias not in self.seen_aliases:
            self.seen_aliases.add(typ._alias)
            self.collected.append(typ)
        self.collect_many(typ._args)

    def visit_required_type(self, typ: RequiredType) -> None:
        self.collect(typ._item)

    def visit_read_only_type(self, typ: ReadOnlyType) -> None:
        self.collect(typ._item)

    def visit_type_type(self, typ: TypeType) -> None:
        self.collect(typ._item)

    def visit_unpack_type(self, typ: UnpackType) -> None:
        self.collect(typ._type)

    def visit_type_var(self, typ: TypeVarType) -> None:
        self.collect_many(typ._values)
        self.collect(typ._upper_bound)
        self.collect(typ._default)

    def visit_param_spec(self, typ: ParamSpecType) -> None:
        self.collect(typ._upper_bound)
        self.collect(typ._default)

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> None:
        self.collect(typ._upper_bound)
        self.collect(typ._default)
        self.collect(typ._tuple_fallback)

    def visit_unbound_type(self, typ: UnboundType) -> None:
        self.collect_many(typ._args)

    def visit_callable_argument(self, typ: CallableArgument) -> None:
        self.collect(typ._typ)

    def visit_type_list(self, typ: TypeList) -> None:
        self.collect_many(typ._items)

    def visit_instance(self, typ: Instance) -> None:
        self.collect_many(typ._args)
        if typ._last_known_value is not None:
            self.collect(typ._last_known_value)

    def visit_parameters(self, typ: Parameters) -> None:
        self.collect_many(typ._arg_types)

    def visit_callable_type(self, typ: CallableType) -> None:
        self.collect_many(typ._arg_types)
        self.collect(typ._ret_type)
        self.collect(typ._fallback)
        self.collect_many(typ._variables)

    def visit_overloaded(self, typ: Overloaded) -> None:
        self.collect_many(typ._items)

    def visit_tuple_type(self, typ: TupleType) -> None:
        self.collect_many(typ._items)
        self.collect(typ._partial_fallback)

    def visit_typeddict_type(self, typ: TypedDictType) -> None:
        for item in typ._items.values():
            self.collect(item)
        self.collect(typ._fallback)

    def visit_literal_type(self, typ: LiteralType) -> None:
        self.collect(typ._fallback)

    def visit_union_type(self, typ: UnionType) -> None:
        self.collect_many(typ._items)

    def visit_partial_type(self, typ: PartialType) -> None:
        if typ._value_type is not None:
            self.collect(typ._value_type)

    def visit_placeholder_type(self, typ: PlaceholderType) -> None:
        self.collect_many(typ._args)


##


class _TypeKeyBuilder(DefaultTypeVisitor[object | None]):
    def __init__(self, writer: _TypeKeyWriter, policy: TypeKeyPolicy) -> None:
        super().__init__()

        self.writer = writer
        self.policy = policy
        self._alias_stack: list[TypeAlias] = []
        self._type_var_keys: dict[tuple[str, int, int], int] = {}
        self._next_type_var_key = 0

    def key(self, typ: Type) -> ta.Any:
        key = self._key(typ)
        if key is None:
            return None
        return self.writer.finish(key)  # type: ignore[attr-defined]

    def _key(self, typ: Type) -> object | None:
        if isinstance(typ, AnnotatedType) and not self.policy.include_annotated_metadata:
            return self._key(typ._item)

        if self.policy.structural and not self.policy.preserve_alias_identity:
            if not isinstance(typ, TypeAliasType) and not self._alias_stack:
                alias_key = self.recursive_alias_canonical_key(typ)
                if alias_key is not None:
                    return alias_key

        return typ.accept(self)

    def visit_type(self, typ: Type) -> object | None:
        return None

    def visit_type_alias_type(self, typ: TypeAliasType) -> object | None:
        return self.type_alias_key(typ)

    def visit_type_guarded_type(self, typ: TypeGuardedType) -> object | None:
        return self._key(typ._type_guard)

    def visit_annotated_type(self, typ: AnnotatedType) -> object | None:
        item_key = self._key(typ._item)
        if item_key is None:
            return None
        return self.writer.annotated_key(item_key, typ._metadata)

    def visit_required_type(self, typ: RequiredType) -> object | None:
        item_key = self._key(typ._item)
        if item_key is None:
            return None
        return self.writer.required_key(item_key, typ._required)

    def visit_read_only_type(self, typ: ReadOnlyType) -> object | None:
        item_key = self._key(typ._item)
        if item_key is None:
            return None
        return self.writer.readonly_key(item_key)

    def visit_type_var(self, typ: TypeVarType) -> object | None:
        return self.type_var_like_key('TV', typ)

    def visit_param_spec(self, typ: ParamSpecType) -> object | None:
        return self.type_var_like_key('PS', typ)

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> object | None:
        return self.type_var_like_key('TVT', typ)

    def visit_unbound_type(self, typ: UnboundType) -> object | None:
        arg_keys = self.key_list(typ._args)
        if arg_keys is None:
            return None
        return self.writer.unbound_key(typ._name, arg_keys)

    def visit_callable_argument(self, typ: CallableArgument) -> object | None:
        item_key = self._key(typ._typ)
        if item_key is None:
            return None
        return self.writer.callable_argument_key(item_key, typ._name, typ._constructor)

    def visit_type_list(self, typ: TypeList) -> object | None:
        item_keys = self.key_list(typ._items)
        if item_keys is None:
            return None
        return self.writer.type_list_key(item_keys)

    def visit_unpack_type(self, typ: UnpackType) -> object | None:
        item_key = self._key(typ._type)
        if item_key is None:
            return None
        return self.writer.unpack_key(item_key)

    def visit_any(self, typ: AnyType) -> object | None:
        return self.writer.any_key(typ._type_of_any)

    def visit_uninhabited_type(self, typ: UninhabitedType) -> object | None:
        return self.writer.uninhabited_key()

    def visit_none_type(self, typ: NoneType) -> object | None:
        return self.writer.none_key()

    def visit_erased_type(self, typ: ErasedType) -> object | None:
        return self.writer.erased_key()

    def visit_deleted_type(self, typ: DeletedType) -> object | None:
        return self.writer.deleted_key(typ._source)

    def visit_instance(self, typ: Instance) -> object | None:
        return self.instance_key(typ)

    def visit_parameters(self, typ: Parameters) -> object | None:
        arg_keys = self.key_list(typ._arg_types)
        if arg_keys is None:
            return None
        return self.writer.parameters_key(arg_keys, typ._arg_kinds, typ._arg_names)

    def visit_callable_type(self, typ: CallableType) -> object | None:
        return self.callable_key(typ)

    def visit_overloaded(self, typ: Overloaded) -> object | None:
        item_keys = self.key_list(typ._items)
        if item_keys is None:
            return None
        return self.writer.overloaded_key(item_keys)

    def visit_tuple_type(self, typ: TupleType) -> object | None:
        item_keys = self.key_list(typ._items)
        fallback_key = self._key(typ._partial_fallback)
        if item_keys is None or fallback_key is None:
            return None
        return self.writer.tuple_key(item_keys, fallback_key)

    def visit_typeddict_type(self, typ: TypedDictType) -> object | None:
        item_keys = self.key_mapping(typ._items)
        fallback_key = self._key(typ._fallback)
        if item_keys is None or fallback_key is None:
            return None
        return self.writer.typed_dict_key(item_keys, typ._required_keys, typ._readonly_keys, fallback_key)

    def visit_raw_expression_type(self, typ: RawExpressionType) -> object | None:
        return self.writer.raw_expression_key(typ._literal_value, typ._base_type_name)

    def visit_literal_type(self, typ: LiteralType) -> object | None:
        fallback_key = self._key(typ._fallback)
        if fallback_key is None:
            return None
        return self.writer.literal_key(typ._value, fallback_key)

    def visit_union_type(self, typ: UnionType) -> object | None:
        item_keys = self.key_list(typ._items)
        if item_keys is None:
            return None
        return self.writer.union_key(item_keys)

    def visit_ellipsis_type(self, typ: EllipsisType) -> object | None:
        return self.writer.ellipsis_key()

    def visit_type_type(self, typ: TypeType) -> object | None:
        item_key = self._key(typ._item)
        if item_key is None:
            return None
        return self.writer.type_type_key(item_key)

    def visit_placeholder_type(self, typ: PlaceholderType) -> object | None:
        arg_keys = self.key_list(typ._args)
        if arg_keys is None:
            return None
        return self.writer.placeholder_key(typ._fullname, arg_keys)

    def type_var_like_key(self, tag: str, typ: TypeVarLikeType) -> object:
        id_key = (typ._id._namespace, typ._id._raw_id, typ._id._meta_level)
        if not self.policy.alpha:
            return self.writer.type_var_like_key(tag, *id_key)

        try:
            key = self._type_var_keys[id_key]
        except KeyError:
            key = self._next_type_var_key
            self._next_type_var_key += 1
            self._type_var_keys[id_key] = key

        return self.writer.alpha_type_var_like_key(tag, key)

    def key_list(self, typs: ta.Sequence[Type]) -> tuple[object, ...] | None:
        keys: list[object] = []
        for typ in typs:
            key = self._key(typ)
            if key is None:
                return None
            keys.append(key)
        return tuple(keys)

    def key_mapping(self, typs: ta.Mapping[str, Type]) -> tuple[tuple[str, object], ...] | None:
        keys: list[tuple[str, object]] = []
        for name in sorted(typs):
            key = self._key(typs[name])
            if key is None:
                return None
            keys.append((name, key))
        return tuple(keys)

    def instance_key(self, typ: Instance) -> object | None:
        if not self.policy.preserve_newtype_identity and typ._type._new_type_supertype is not None:
            return self._key(typ._type._new_type_supertype)

        arg_keys = self.key_list(typ._args)
        if arg_keys is None:
            return None

        last_known_value_key: object | None = None
        if typ._last_known_value is not None:
            last_known_value_key = self._key(typ._last_known_value)
            if last_known_value_key is None:
                return None

        return self.writer.instance_key(typ._type._fullname, arg_keys, last_known_value_key)

    def callable_key(self, typ: CallableType) -> object | None:
        arg_keys = self.key_list(typ._arg_types)
        ret_key = self._key(typ._ret_type)
        fallback_key = self._key(typ._fallback)
        variable_keys = self.key_list(typ._variables)
        if arg_keys is None or ret_key is None or fallback_key is None or variable_keys is None:
            return None
        return self.writer.callable_key(
            arg_keys,
            typ._arg_kinds,
            typ._arg_names,
            ret_key,
            fallback_key,
            variable_keys,
            typ._is_ellipsis_args,
        )

    def type_alias_key(self, typ: TypeAliasType) -> object | None:
        if typ._alias is None:
            return None

        arg_keys = self.key_list(typ._args)
        if arg_keys is None:
            return None

        if typ._alias in self._alias_stack:
            return self.writer.alias_ref_key(self._alias_stack.index(typ._alias), arg_keys)

        is_recursive = typ.is_recursive

        if not self.policy.preserve_alias_identity:
            if not is_recursive:
                target = self._alias_target(typ)
                if target is None:
                    return None
                return self._key(target)

            self._alias_stack.append(typ._alias)
            try:
                target = self._alias_target(typ)
                if target is None:
                    return None
                target_key = self._key(target)
            finally:
                self._alias_stack.pop()

            if target_key is None:
                return None

            return self.writer.recursive_type_alias_key(arg_keys, target_key)

        self._alias_stack.append(typ._alias)
        try:
            target = self._alias_target(typ)
            if target is None:
                return None
            target_key = self._key(target)
        finally:
            self._alias_stack.pop()

        if target_key is None:
            return None

        if is_recursive:
            return self.writer.recursive_type_alias_key(arg_keys, target_key)

        return self.writer.type_alias_key(typ._alias._fullname, typ._alias._runtime_object, arg_keys, target_key)

    def _alias_target(self, typ: TypeAliasType) -> Type | None:
        if not typ._args:
            return typ._alias._target  # type: ignore[union-attr]

        if typ._alias is None or len(typ._args) != len(typ._alias._alias_tvars):
            return None

        from .substitute import substitute_type

        return substitute_type(typ._alias._target, dict(zip(typ._alias._alias_tvars, typ._args)))

    def recursive_alias_canonical_key(self, typ: Type) -> object | None:
        for alias_type in self.collect_recursive_alias_types(typ):
            target = self._alias_target(alias_type)
            if target is None:
                return None

            from .subtypes import is_alpha_structurally_equivalent
            from .subtypes import is_structurally_equivalent

            try:
                if self.policy.alpha:
                    is_match = is_alpha_structurally_equivalent(typ, target)
                else:
                    is_match = is_structurally_equivalent(typ, target)
            except ReflectionError:
                is_match = False

            if is_match:
                return self.type_alias_key(alias_type)

        return None

    def collect_recursive_alias_types(self, typ: Type) -> list[TypeAliasType]:
        visitor = _CollectRecursiveAliasTypesVisitor()
        visitor.collect(typ)
        return visitor.collected
