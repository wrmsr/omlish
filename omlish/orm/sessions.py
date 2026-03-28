# ruff: noqa: SLF001
import contextvars
import typing as ta

from .. import check
from .. import lang
from .keys import _KEY_TYPES
from .keys import Key
from .keys import _AutoKey
from .keys import _Key
from .keys import _unwrap_key
from .mappers import Mapper
from .queries import Query
from .refs import _DirectRef
from .refs import _LazyRef
from .registries import Registry
from .snaps import Snap
from .stores import Store


K = ta.TypeVar('K')
T = ta.TypeVar('T')


##


class _NOT_SET(lang.Marker):  # noqa
    pass


class Session:
    def __init__(
            self,
            registry: Registry,
            store: Store,
            *,
            no_auto_flush: bool = True,
    ) -> None:
        super().__init__()

        self._registry = registry
        self._store = store
        self._no_auto_flush = no_auto_flush

        self._aborted = False

        self._entities_by_key_by_cls: dict[type, dict[Key, Session._Entity]] = {m._cls: {} for m in registry._mappers}
        self._entities_by_obj_id: dict[int, Session._Entity] = {}
        self._entities_by_auto_key: dict[_AutoKey, Session._Entity] = {}

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}({"aborted=True" if self._aborted else ""})'

    #

    @property
    def aborted(self) -> bool:
        return self._aborted

    def abort(self) -> None:
        if self._aborted:
            return

        self._aborted = True

        del self._entities_by_key_by_cls
        del self._entities_by_obj_id
        del self._entities_by_auto_key

    #

    def activate(self) -> ta.ContextManager[ta.Self]:
        return _SessionActivator(self)

    #

    class _Entity:
        def __init__(
                self,
                m: Mapper,
                k: Key,
                *,
                obj: ta.Any | None = None,
                snap: Snap | None = None,
        ) -> None:
            super().__init__()

            self.m = m
            self.k = k

            self.obj = obj
            self.snap = snap

        def __repr__(self) -> str:
            return (
                f'{self.__class__.__name__}('
                f'{self.m!r}'
                f', {self.k!r}'
                f'{f", obj={self.obj!r}" if self.obj is not None else ""}'
                f'{f", snap={self.snap!r}" if self.snap is not None else ""}'
                f')'
            )

    def _attach(
            self,
            cls: type | None = None,
            k: Key | None = None,
            *,
            obj: ta.Any | type[_NOT_SET] | None = _NOT_SET,
            snap: Snap | type[_NOT_SET] | None = _NOT_SET,
    ) -> _Entity:
        check.state(not self._aborted)

        check.arg(not (
            obj is not _NOT_SET and
            snap is not _NOT_SET and
            (
                (obj is None and snap is not None) or
                (obj is not None and snap is None)
            )
        ))

        #

        if cls is None:
            check.is_not(obj, _NOT_SET)
            cls = type(check.not_none(obj))
        elif obj is not _NOT_SET and obj is not None:
            check.is_(type(obj), cls)

        m = self._registry.mapper_for_cls(cls)

        #

        if obj is not _NOT_SET and obj is not None:
            ok = m.key_for_obj(obj)
            if k is None:
                k = ok
            else:
                check.equal(k, ok)

        if snap is not _NOT_SET and snap is not None:
            sk = m.key_for_snap(snap)  # type: ignore[arg-type]
            if k is None:
                k = sk
            else:
                check.equal(k, sk)

        if obj is not _NOT_SET and obj is not None and snap is not _NOT_SET and snap is not None:
            check.equal(m.obj_to_snap(obj), snap)

        k = check.not_none(k)

        #

        ed = self._entities_by_key_by_cls[cls]

        try:
            e = ed[k]
        except KeyError:
            pass

        else:
            check.equal(e.k, k)

            if obj is not _NOT_SET:
                check.is_(e.obj, obj)
                if obj is not None:
                    check.is_(self._entities_by_obj_id[id(obj)], e)

            if snap is not _NOT_SET:
                check.equal(e.snap, snap)

            return e

        #

        if snap is not _NOT_SET and snap is not None and obj is _NOT_SET:
            obj = m.snap_to_obj(snap)  # type: ignore[arg-type]

        if obj is _NOT_SET:
            obj = None
        if snap is _NOT_SET:
            snap = None

        e = self._Entity(
            m,
            k,
            obj=obj,
            snap=snap,  # type: ignore[arg-type]
        )

        self._entities_by_key_by_cls.setdefault(m.cls, {})[k] = e

        if obj is not None:
            self._entities_by_obj_id[id(obj)] = e

        if k.__class__ is _AutoKey:
            self._entities_by_auto_key[k] = e  # type: ignore[index]  # noqa

        return e

    #

    def add(self, *objs: ta.Any) -> None:
        for obj in objs:
            self._attach(obj=obj)

    #

    @ta.overload
    def get(self, cls: type[T], k: Key[K]) -> T | None:
        ...

    @ta.overload
    def get(self, cls: type[T], k: K) -> T | None:
        ...

    def get(self, cls, k):  # noqa
        check.state(not self._aborted)

        if k.__class__ not in _KEY_TYPES:
            k = _Key(k)

        cd = self._entities_by_key_by_cls.setdefault(cls, {})

        try:
            e = cd[k]
        except KeyError:
            pass
        else:
            return e.obj

        m = self._registry.mapper_for_cls(cls)

        snap = self._store.fetch(m, k.k)
        if snap is None:
            return None

        e = self._attach(
            cls,
            snap=snap,
        )

        return e.obj

    #

    def _delete(self, obj: ta.Any) -> None:
        e = self._attach(obj=obj)

        e.obj = None

        del self._entities_by_obj_id[id(obj)]

    def delete(self, *objs: ta.Any) -> None:
        check.state(not self._aborted)

        for obj in objs:
            self._delete(obj=obj)

    #

    def flush(self) -> None:
        check.state(not self._aborted)

        entity_ops: list[tuple[
            Mapper,
            Store.FlushResult,
            list[tuple[
                Session._Entity,
                ta.Any | None,
                Snap | None,
            ]],
        ]] = []

        for cls, cd in self._entities_by_key_by_cls.items():
            eol: list = []

            m = self._registry.mapper_for_cls(cls)

            insert: list[Snap] = []
            update: list[tuple[ta.Any, Snap]] = []
            delete: list[ta.Any] = []

            for e in cd.values():
                if e.obj is None:
                    if e.snap is None:
                        continue
                    delete.append(_unwrap_key(e.k))
                    eol.append((e, None, None))

                else:
                    snap = e.m.obj_to_snap(e.obj)
                    if snap == e.snap:
                        continue
                    eol.append((e, e.obj, snap))
                    if (xs := e.snap) is None:
                        insert.append(snap)
                    else:
                        ds = {k: nv for k, nv in snap.items() if xs[k] != nv}
                        update.append((_unwrap_key(e.k), ds))

            if not (insert or update or delete):
                continue

            batch = Store.FlushBatch(
                insert=insert or None,
                update=update or None,
                delete=delete or None,
            )

            fr = self._store.flush(m, batch)

            entity_ops.append((m, fr, eol))

        for m, fr, eol in entity_ops:
            ed = self._entities_by_key_by_cls[m._cls]

            for e, e_obj, e_snap in eol:
                if (ek := e.k).__class__ is _AutoKey:
                    k = _Key(fr.inserted_auto_keys[ek])  # type: ignore[index]

                    check.not_in(k, ed)  # noqa
                    check.is_(self._entities_by_auto_key[ek], e)  # type: ignore[index]

                    del ed[ek]

                    e.k = k
                    setattr(e_obj, m._key_field._name, k)
                    ed[k] = e

                if e_obj is None and (xo := e.obj) is not None:
                    del self._entities_by_obj_id[id(xo)]

                e.obj = e_obj
                e.snap = e_snap

    #

    def _get_direct_ref_key(self, dr: _DirectRef) -> Key:
        e = self._entities_by_obj_id[id(dr._obj)]
        return e.k

    def _get_lazy_ref_obj(self, lr: _LazyRef) -> ta.Any:
        # TODO: writeback?
        return check.not_none(self.get(lr._cls, lr._k))

    #

    def query(self, q: Query[T]) -> list[T]:
        check.state(not self._aborted)

        if not self._no_auto_flush:
            self.flush()

        cls = q._cls
        m = self._registry.mapper_for_cls(cls)

        wh: dict[str, ta.Any] = {}
        for k, v in q.where.items():
            f = m._fields_by_name[k]
            wh[f._store_name] = m.field_value_to_snap_value(f, v)

        if not (snaps := self._store.lookup(m, wh)):
            return []

        out: list[T] = []

        for snap in snaps:
            e = self._attach(cls, snap=snap)

            if (obj := e.obj) is not None:
                out.append(obj)

        return out


##


class NoActiveSessionError(Exception):
    pass


class SessionAlreadyActiveError(Exception):
    pass


_ACTIVE_SESSION: contextvars.ContextVar[Session] = contextvars.ContextVar(f'{__name__}._ACTIVE_SESSION')


@ta.final
class _SessionActivator:
    def __init__(self, s) -> None:
        self._s = s

    _tok: ta.Any

    def __enter__(self):
        try:
            x = _ACTIVE_SESSION.get()
        except LookupError:
            pass
        else:
            raise SessionAlreadyActiveError(x)

        self._tok = _ACTIVE_SESSION.set(self._s)
        return self._s

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            if not self._s._aborted and not self._s._no_auto_flush:
                self._s.flush()
        else:
            self._s.abort()

        _ACTIVE_SESSION.reset(self._tok)


def active_session() -> Session:
    try:
        return _ACTIVE_SESSION.get()
    except LookupError:
        raise NoActiveSessionError from None


def opt_active_session() -> Session | None:
    try:
        return _ACTIVE_SESSION.get()
    except LookupError:
        return None
