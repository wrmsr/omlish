import abc
import typing as ta

from omlish import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')

SortDirection: ta.TypeAlias = ta.Literal['asc', 'desc']


##


# Installed by bases.py on import
_KV_BASES_BY_MRO: ta.Mapping[tuple[type['Kv'], ...], type['Kv']]


class KvSubclassMustUseBaseTypeError(TypeError):
    pass


class Kv(lang.Abstract, ta.Generic[K, V]):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            kv_interfaces = KV_INTERFACES
        except NameError:
            # Module initializing
            return

        iface_mro = tuple(mc for mc in cls.__mro__ if mc in kv_interfaces)
        if not iface_mro:
            # Interface-less kv subclasses are mixins.
            return

        sorted_iface_mro = tuple(sorted(iface_mro, key=lambda ic: kv_interfaces.index(ic)))
        if iface_mro != sorted_iface_mro:
            raise TypeError(
                f'Kv subclass {cls} must keep kv interfaces in proper order: '
                f'got {iface_mro}, '
                f'expected {sorted_iface_mro}',
            )

        try:
            kv_bases_by_mro = _KV_BASES_BY_MRO
        except NameError:
            # Bases module uninitialized
            return

        base = kv_bases_by_mro[iface_mro]
        if not issubclass(cls, base):
            raise KvSubclassMustUseBaseTypeError(
                f'Kv subclass {cls} must not subclass kv interface compositions directly: '
                f'mro {iface_mro} '
                f'should inherit from {base}',
            )


##


class QueryableKv(Kv[K, V], lang.Abstract):
    @abc.abstractmethod
    def __getitem__(self, k: K, /) -> V:
        raise NotImplementedError


class SizedKv(Kv[K, V], lang.Abstract):
    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError


class IterableKv(Kv[K, V], lang.Abstract):
    @abc.abstractmethod
    def items(self) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError


class SortedKv(Kv[K, V], lang.Abstract):
    @abc.abstractmethod
    def sorted_items(
            self,
            start: lang.Maybe[K] = lang.empty(),
            direction: SortDirection = 'asc',
    ) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError


class MutableKv(Kv[K, V], lang.Abstract):  # noqa
    @abc.abstractmethod
    def __setitem__(self, k: K, v: V, /) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def __delitem__(self, k: K, /) -> None:
        raise NotImplementedError


##


KvMro: ta.TypeAlias = tuple[type[Kv], ...]


KV_INTERFACES: KvMro = (
    MutableKv,
    SortedKv,
    IterableKv,
    SizedKv,
    QueryableKv,
)


##


_KV_INTERFACE_NON_MEMBERS: frozenset[str] = frozenset(dir(Kv))

KV_INTERFACE_MEMBERS: ta.Mapping[type[Kv], tuple[str, ...]] = {
    ic: tuple(
        a
        for a in lang.mro_dict(ic)  # preserves declaration order unlike dir()
        if a not in _KV_INTERFACE_NON_MEMBERS
    )
    for ic in KV_INTERFACES
}


##


def check_kv_interface_mro(
        iface_mro: KvMro,
        *,
        cls_for_type_error: type | None = None,
) -> KvMro:
    sorted_iface_mro = tuple(sorted(iface_mro, key=lambda ic: KV_INTERFACES.index(ic)))
    if iface_mro != sorted_iface_mro:
        raise TypeError(
            f'Kv subclass '
            f'{f"{cls_for_type_error!r} " if cls_for_type_error is not None else ""}'
            f'must keep kv interfaces in proper order: '
            f'got {iface_mro}, '
            f'expected {sorted_iface_mro}',
        )
    return iface_mro


def get_cls_kv_interface_mro(cls: type[Kv]) -> KvMro:
    iface_mro = tuple(mc for mc in cls.__mro__ if mc in KV_INTERFACES)
    return check_kv_interface_mro(iface_mro, cls_for_type_error=cls)


##


def _main() -> None:
    print(KV_INTERFACE_MEMBERS)


if __name__ == '__main__':
    _main()
