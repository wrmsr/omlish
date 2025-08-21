import typing as ta
import weakref

from omlish import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')
T = ta.TypeVar('T')


##


class RegistryClassAttr(ta.Generic[K, V]):
    def __init__(
            self,
            *,
            lock: lang.DefaultLockable = None,
            weak_keys: bool = False,
            weak_values: bool = False,
            requires_override: bool = False,
    ) -> None:
        super().__init__()

        self._lock = lang.default_lock(lock)
        self._weak_keys = weak_keys
        self._weak_values = weak_values
        self._requires_override = requires_override

        self._dct: ta.MutableMapping[ta.Any, ta.MutableSet[K]] = weakref.WeakKeyDictionary() if weak_keys else {}

        self._cls_attrs_cache: ta.MutableMapping[type, ta.MutableMapping[type, ta.Mapping[str, ta.Any]]] = weakref.WeakKeyDictionary()  # noqa

    #

    def is_registered(self, obj: ta.Any) -> bool:
        try:
            hash(obj)
        except TypeError:
            return False
        return obj in self._dct

    def register(self, *ks: K) -> ta.Callable[[T], T]:  # nodiscard
        def inner(v):
            with self._lock():
                try:
                    s = self._dct[v]
                except KeyError:
                    s = self._dct[v] = weakref.WeakSet() if self._weak_values else set()
                for k in ks:
                    s.add(k)
            return v
        return inner

    #

    def _get_cls_attrs_uncached(self, cls: type, owner_cls: type) -> ta.Mapping[str, ta.Any]:
        mro = cls.__mro__[-2::-1]
        try:
            mro_pos = mro.index(owner_cls)
        except ValueError:
            raise TypeError(f'Owner class {owner_cls} not in mro of class {cls}') from None

        #

        mro_dct: dict[str, list[tuple[type, ta.Any]]] = {}
        for cur_cls in mro[:mro_pos + 1]:
            for att, obj in cur_cls.__dict__.items():
                if att not in mro_dct:
                    if not self.is_registered(obj):
                        continue

                try:
                    lst = mro_dct[att]
                except KeyError:
                    lst = mro_dct[att] = []
                lst.append((cur_cls, obj))

        #

        print(mro_dct)

        return {}

    def _get_cls_attrs(self, cls: type, owner_cls: type | None = None) -> ta.Mapping[str, ta.Any]:
        if not isinstance(cls, type):
            raise TypeError(cls)
        if owner_cls is None:
            owner_cls = cls

        try:
            owner_dct = self._cls_attrs_cache[cls]
        except KeyError:
            if owner_cls not in cls.__mro__:
                raise TypeError(f'Owner class {owner_cls} not in mro of class {cls}') from None
            owner_dct = self._cls_attrs_cache[cls] = weakref.WeakKeyDictionary()

        try:
            return owner_dct[owner_cls]
        except KeyError:
            pass

        dct = self._get_cls_attrs_uncached(cls, owner_cls)
        owner_dct[owner_cls] = dct
        return dct
