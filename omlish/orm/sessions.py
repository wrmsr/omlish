# ruff: noqa: SLF001
import contextvars
import enum
import typing as ta

from .. import check
from .. import lang
from .backrefs import _BoundBackref
from .fields import RefField
from .flushing import _SessionFlusher
from .keys import _KEY_TYPES
from .keys import Key
from .keys import _AutoKey
from .keys import _ValKey
from .mappers import Mapper
from .queries import Query
from .refs import _KeyRef
from .refs import _ObjRef
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
            transaction: bool | ta.Literal['default'] = 'default',
            no_auto_flush: bool = True,
    ) -> None:
        super().__init__()

        self._registry = registry
        self._store = store

        self._transaction = transaction
        self._no_auto_flush = no_auto_flush

        self._entities_by_key_by_cls: dict[type, dict[Key, Session._Entity]] = {m._cls: {} for m in registry._mappers}
        self._entities_by_obj_id: dict[int, Session._Entity] = {}
        self._entities_by_auto_key: dict[_AutoKey, Session._Entity] = {}

    _store_cm: ta.AsyncContextManager[Store.Context]
    _store_ctx: Store.Context

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}(state={self._state!r}'

    #

    class State(enum.StrEnum):
        NEW = 'new'

        ENTERING = 'entering'
        ENTERED = 'entered'

        FINISHING = 'finishing'
        FINISHED = 'finished'

        ABORTING = 'aborting'
        ABORTED = 'aborted'

        FAILED = 'failed'

    _state = State.NEW

    @property
    def state(self) -> State:
        return self._state

    @property
    def is_alive(self) -> bool:
        return self._state in (self.State.ENTERED, self.State.FINISHING)

    #

    async def __aenter__(self) -> ta.Self:
        check.state(self._state == self.State.NEW)

        self._state = self.State.ENTERING

        self._store_cm = self._store.create_context(
            transaction=self._transaction,
        )
        self._store_ctx = await self._store_cm.__aenter__()

        self._state = self.State.ENTERED

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._state == self.State.ENTERED:
            if exc_type is None:
                await self.finish()
            else:
                await self.abort()

    async def finish(self) -> None:
        if self._state == self.State.FINISHED:
            return

        check.state(self._state == self.State.ENTERED)

        self._state = self.State.FINISHING

        if not self._no_auto_flush:
            await self.flush()

        await self._store_ctx.finish()
        del self._store_ctx

        await self._store_cm.__aexit__(None, None, None)
        del self._store_cm

        self._state = self.State.FINISHED

    async def abort(self) -> None:
        if self._state == self.State.ABORTED:
            return

        check.state(self._state == self.State.ENTERED)

        self._state = self.State.ABORTING

        await self._store_ctx.abort()
        del self._store_ctx

        await self._store_cm.__aexit__(None, None, None)
        del self._store_cm

        self._state = self.State.ABORTED

    #

    def activate(self) -> ta.AsyncContextManager[ta.Self]:
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
        check.state(self.is_alive)

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
                if (es := e.snap) is None:
                    check.none(snap)

                else:
                    snap2 = check.not_none(snap)
                    es_diff: dict[str, tuple[ta.Any, ta.Any]] = {}
                    for dk, dv in es.items():
                        try:
                            dv2 = snap2[dk]  # type: ignore[index]
                        except KeyError:
                            continue
                        if dv != dv2:
                            es_diff[dk] = (dv, dv2)
                    if es_diff:
                        raise RuntimeError(f'Entity {e} snapshots differ: {es_diff}')

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
            self._entities_by_auto_key[k] = e  # noqa

        return e

    #

    async def add(self, *objs: ta.Any) -> None:
        for obj in objs:
            self._attach(obj=obj)

    #

    @ta.overload
    async def get(self, cls: type[T], k: Key[K]) -> T | None:
        ...

    @ta.overload
    async def get(self, cls: type[T], k: K) -> T | None:
        ...

    async def get(self, cls, k):  # noqa
        check.state(self.is_alive)

        if k.__class__ not in _KEY_TYPES:
            k = _ValKey(k)

        cd = self._entities_by_key_by_cls.setdefault(cls, {})

        try:
            e = cd[k]
        except KeyError:
            pass
        else:
            return e.obj

        m = self._registry.mapper_for_cls(cls)

        snap = await self._store_ctx.fetch(m, k.k)
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

    async def delete(self, *objs: ta.Any) -> None:
        check.state(self.is_alive)

        for obj in objs:
            self._delete(obj=obj)

    #

    def _writeback_snap(self, e: _Entity, wb_snap: Snap | None) -> None:
        if wb_snap is None:
            e.snap = None
            return

        e.snap = {**(e.snap or {}), **wb_snap}

        m = e.m
        for k, v in wb_snap.items():
            f = m._fields_by_store_name[k]
            ov = m.snap_value_to_field_value(f, v)
            setattr(e.obj, f._name, ov)

    async def flush(self) -> None:
        check.state(self.is_alive)

        res = await _SessionFlusher(self).flush()

        for e, (wb_k, wb_snap) in res.ent_writeback.items():
            m = e.m

            if wb_k is not None:
                ed = self._entities_by_key_by_cls[m._cls]
                del ed[e.k]
                e.k = _ValKey(wb_k)
                ed[e.k] = e

            self._writeback_snap(e, wb_snap)

    async def refresh(self, *objs: ta.Any) -> None:
        for obj in objs:
            e = self._entities_by_obj_id[id(obj)]
            m = e.m

            snap = await self._store_ctx.fetch(m, e.k.k)

            self._writeback_snap(e, snap)

    #

    def _get_obj_ref_key(self, dr: _ObjRef) -> Key:
        e = self._entities_by_obj_id[id(dr._obj)]
        return e.k

    async def _get_key_ref_obj(self, lr: _KeyRef) -> ta.Any:
        # TODO: writeback?
        return check.not_none(await self.get(lr._cls, lr._k))

    async def _get_bound_backref_objs(self, bbr: _BoundBackref) -> ta.Sequence[ta.Any]:
        binder = bbr._br._binder

        brd = self._registry._fields_by_backref_binding
        try:
            brf_lst = brd[binder]
        except KeyError:
            if not callable(binder):
                raise
            brf_lst = brd[binder()]
        check.not_empty(brf_lst)
        if len(brf_lst) > 1:
            raise RuntimeError(f'Ambiguous backref binding: {binder} -> {brf_lst}')
        [brf] = brf_lst
        rf = check.isinstance(brf, RefField)

        return await self.query(Query(rf._mapper._cls, {rf._name: _ObjRef(bbr._obj)}))

    #

    async def query(self, q: Query[T]) -> list[T]:
        check.state(self.is_alive)

        if not self._no_auto_flush:
            await self.flush()

        cls = q._cls
        m = self._registry.mapper_for_cls(cls)

        wh: dict[str, ta.Any] = {}
        for k, v in q.where.items():
            f = m._fields_by_name[k]
            wh[f._store_name] = m.field_value_to_snap_value(f, v)

        if not (snaps := await self._store_ctx.lookup(m, wh)):
            return []

        out: list[T] = []

        for snap in snaps:
            # FIXME: writeback? merge?
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
    def __init__(self, s: Session) -> None:
        self._s = s

    _tok: ta.Any

    async def __aenter__(self):
        try:
            x = _ACTIVE_SESSION.get()
        except LookupError:
            pass
        else:
            raise SessionAlreadyActiveError(x)

        self._tok = _ACTIVE_SESSION.set(self._s)
        return self._s

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._s._state == Session.State.ENTERED:
            if exc_type is None:
                if not self._s._no_auto_flush:
                    await self._s.flush()
            else:
                await self._s.abort()

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
