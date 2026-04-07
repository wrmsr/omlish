# ruff: noqa: SLF001
import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import lang
from .errors import DuplicateIndexValueError
from .indexes import Index
from .mappers import Mapper
from .snaps import Snap
from .stores import Store
from .wrappers import WRAPPER_TYPES


##


class InMemoryStore(Store):
    def __init__(self) -> None:
        super().__init__()

        self._tables_by_mapper: dict[Mapper, InMemoryStore._Table] = {}
        self._tables_by_name: dict[str, InMemoryStore._Table] = {}

        self._state_ = self._State()

    #

    class _Table:
        def __init__(self, m: Mapper) -> None:
            super().__init__()

            self.m = m

            self.index_lookup: dict[frozenset[str], Index] = {
                frozenset(idx._field_store_names): idx
                for idx in sorted(
                    m._indexes,
                    key=lambda idx: idx._field_store_names,
                )
            }

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}({self.m!r})'

    def _table_for_mapper(self, m: Mapper) -> _Table:
        try:
            return self._tables_by_mapper[m]
        except KeyError:
            pass

        check.not_in(m.store_name, self._tables_by_name)

        t = self._Table(m)

        self._tables_by_mapper[m] = t
        self._tables_by_name[m.store_name] = t

        return t

    #

    @dc.dataclass(frozen=True)
    class _State:
        tables: col.PersistentMapping[str, 'InMemoryStore._TableState'] = dc.field(default_factory=col.new_persistent_map)  # noqa

    @dc.dataclass(frozen=True)
    class _TableState:
        snaps: col.PersistentMapping[ta.Any, Snap] = dc.field(default_factory=col.new_persistent_map)
        indexes: col.PersistentMapping[str, 'InMemoryStore._IndexState'] = dc.field(default_factory=col.new_persistent_map)  # noqa

    @dc.dataclass(frozen=True)
    class _IndexState:
        keys: col.PersistentMapping[tuple[ta.Any, ...] | ta.Any, frozenset[ta.Any] | ta.Any]

    #

    def _new_index_state(self, idx: Index) -> _IndexState:
        if idx.is_sorted:
            return self._IndexState(keys=col.new_persistent_sorted_map())
        else:
            return self._IndexState(keys=col.new_persistent_map())

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class _SelectedIndex:
        index: Index
        index_set: frozenset[str]
        index_key: tuple[ta.Any, ...]
        unindexed_where: ta.Sequence[tuple[str, ta.Any]]

    def _select_index(self, t: _Table, where: ta.Mapping[str, ta.Any]) -> _SelectedIndex | None:
        where_set = frozenset(where)

        best_idx: Index | None = None
        best_set: frozenset[str] | None = None
        best_width: int | None = None

        for cur_set, cur_idx in t.index_lookup.items():
            if cur_set - where_set:
                continue
            cur_width = len(cur_set)
            if not cur_width:
                continue
            if best_width is not None and best_width > cur_width:
                continue
            best_idx = cur_idx
            best_set = cur_set
            best_width = cur_width

        if best_idx is None:
            return None
        best_set = check.not_none(best_set)

        idx_key: ta.Any = tuple(where[k] for k in best_idx._field_store_names)
        if len(idx_key) == 1:
            [idx_key] = idx_key
        un_idx_where = [(k, where[k]) for k in where_set - best_set]

        return self._SelectedIndex(
            index=best_idx,
            index_set=best_set,
            index_key=idx_key,
            unindexed_where=un_idx_where,
        )

    #

    async def _fetch(self, st: _State, m: Mapper, k: ta.Any) -> Snap | None:
        check.not_in(k.__class__, WRAPPER_TYPES)

        try:
            t = self._table_for_mapper(m)
        except KeyError:
            return None

        try:
            ts = st.tables[t.m._store_name]
        except KeyError:
            return None

        return ts.snaps.get(k)

    async def _lookup(self, st: _State, m: Mapper, where: ta.Mapping[str, ta.Any]) -> ta.Sequence[Snap]:
        t = self._table_for_mapper(m)

        try:
            ts = st.tables[t.m._store_name]
        except KeyError:
            return []

        if not where:
            return list(ts.snaps.values())

        if t.m.key_field.store_name in where:
            if (ks := await self._fetch(st, m, where[t.m.key_field.store_name])) is not None:
                return [ks]
            else:
                return []

        si = self._select_index(t, where)

        if si is None:
            lst: list[Snap] = []

            for v in ts.snaps.values():
                for fk, fv in where.items():
                    if v[fk] != fv:
                        break
                else:
                    lst.append(v)

            return lst

        ix = ts.indexes[si.index._store_name]
        try:
            xs = ix.keys[si.index_key]
        except KeyError:
            return []

        if si.index._is_unique:
            xs = [xs]

        if not si.unindexed_where:
            return [ts.snaps[xk] for xk in xs]

        lst = []

        for xk in xs:
            x = ts.snaps[xk]
            for fk, fv in si.unindexed_where:
                if x[fk] != fv:
                    break
            else:
                lst.append(x)

        return lst

    #

    def _index(
            self,
            t: 'InMemoryStore._Table',
            idx_sts: col.PersistentMapping[str, 'InMemoryStore._IndexState'],
            k: ta.Any,
            snap: Snap,
    ) -> col.PersistentMapping[str, 'InMemoryStore._IndexState']:
        if not t.m._indexes:
            return idx_sts

        for idx in t.m._indexes:
            try:
                idx_st = idx_sts[idx._store_name]
            except KeyError:
                idx_st = self._new_index_state(idx)

            idx_keys = idx_st.keys

            idx_key = tuple(snap[f] for f in idx._field_store_names)
            if len(idx_key) == 1:
                [idx_key] = idx_key

            try:
                iz = idx_keys[idx_key]
            except KeyError:
                if idx._is_unique:
                    iz = k
                else:
                    iz = frozenset([k])
            else:
                if idx._is_unique:
                    raise DuplicateIndexValueError(f'Duplicate key in {idx._store_name}: {idx_key}')
                else:
                    iz |= frozenset([k])

            idx_keys = idx_st.keys.with_(idx_key, iz)

            idx_st = dc.replace(idx_st, keys=idx_keys)

            idx_sts = idx_sts.with_(idx._store_name, idx_st)

        return idx_sts

    def _deindex(
            self,
            t: 'InMemoryStore._Table',
            idx_sts: col.PersistentMapping[str, 'InMemoryStore._IndexState'],
            k: ta.Any,
            snap: Snap,
    ) -> col.PersistentMapping[str, 'InMemoryStore._IndexState']:
        if not t.m._indexes:
            return idx_sts

        for idx in t.m._indexes:
            try:
                idx_st = idx_sts[idx._store_name]
            except KeyError:
                idx_st = self._new_index_state(idx)

            idx_keys = idx_st.keys

            idx_key = tuple(snap[f] for f in idx._field_store_names)
            if len(idx_key) == 1:
                [idx_key] = idx_key

            iz = idx_keys[idx_key]
            check.in_(k, iz)

            if idx._is_unique:
                idx_keys = idx_keys.without(idx_key)
            else:
                iz -= frozenset([k])
                if not iz:
                    idx_keys = idx_keys.without(idx_key)
                else:
                    idx_keys = idx_keys.with_(idx_key, iz)

            idx_st = dc.replace(idx_st, keys=idx_keys)

            idx_sts = idx_sts.with_(idx._store_name, idx_st)

        return idx_sts

    #

    def _timestamp_snap(self, m: Mapper, *, create: bool) -> Snap | None:
        ca_sn = m._created_at_store_name if create else None
        ua_sn = m._updated_at_store_name
        if ca_sn is None and ua_sn is None:
            return None

        now = lang.utcnow()

        ti_snap: dict[str, ta.Any] = {}
        if ca_sn is not None:
            ti_snap[ca_sn] = now
        if ua_sn is not None:
            ti_snap[ua_sn] = now

        return ti_snap

    #

    async def _auto_key_insert(
            self,
            st: _State,
            m: Mapper,
            snaps: ta.Sequence[Snap],
    ) -> tuple[_State, ta.Mapping[ta.Any, ta.Any]]:
        t = self._table_for_mapper(m)

        try:
            ts = st.tables[t.m._store_name]
        except KeyError:
            ts = self._TableState()
        ts_snaps = ts.snaps
        idx_sts = ts.indexes

        kf_sn = m._key_field_store_name
        ti_snap = self._timestamp_snap(m, create=True)

        iak: dict[ta.Any, ta.Any] = {}
        for snap in snaps:
            k = snap[kf_sn]
            ak = len(ts_snaps) + 1
            while ak in ts_snaps:
                ak += 1
            iak[k] = ak
            k = ak

            snap = {**snap, kf_sn: k}
            if ti_snap:
                snap.update(ti_snap)

            check.not_in(k, ts_snaps)

            for sk, sv in snap.items():  # noqa
                check.not_in(sv.__class__, WRAPPER_TYPES)

            ts_snaps = ts_snaps.with_(k, snap)
            idx_sts = self._index(t, idx_sts, k, snap)

        ts = dc.replace(ts, snaps=ts_snaps, indexes=idx_sts)
        st = dc.replace(st, tables=st.tables.with_(t.m._store_name, ts))

        return (st, iak)

    async def _insert(
            self,
            st: _State,
            m: Mapper,
            snaps: ta.Sequence[Snap],
    ) -> _State:
        t = self._table_for_mapper(m)

        try:
            ts = st.tables[t.m._store_name]
        except KeyError:
            ts = self._TableState()
        ts_snaps = ts.snaps
        idx_sts = ts.indexes

        kf_sn = m._key_field_store_name
        ti_snap = self._timestamp_snap(m, create=True)

        for snap in snaps:
            k = snap[kf_sn]

            snap = {**snap}
            if ti_snap:
                snap.update(ti_snap)

            for sk, sv in snap.items():  # noqa
                check.not_in(sv.__class__, WRAPPER_TYPES)

            check.not_in(k, ts_snaps)

            ts_snaps = ts_snaps.with_(k, snap)
            idx_sts = self._index(t, idx_sts, k, snap)

        ts = dc.replace(ts, snaps=ts_snaps, indexes=idx_sts)
        st = dc.replace(st, tables=st.tables.with_(t.m._store_name, ts))

        return st

    async def _update(
            self,
            st: _State,
            m: Mapper,
            diffs: ta.Sequence[tuple[ta.Any, Snap]],
    ) -> _State:
        t = self._table_for_mapper(m)

        try:
            ts = st.tables[t.m._store_name]
        except KeyError:
            return st
        ts_snaps = ts.snaps
        idx_sts = ts.indexes

        kf_sn = m._key_field_store_name
        ti_snap = self._timestamp_snap(m, create=False)

        for k, snap in diffs:
            check.not_in(kf_sn, snap)

            kt = k.__class__
            check.not_in(kt, WRAPPER_TYPES)

            for sk, sv in snap.items():  # noqa
                check.not_in(sv.__class__, WRAPPER_TYPES)

            x = ts_snaps[k]

            idx_sts = self._deindex(t, idx_sts, k, x)
            ts_snaps = ts_snaps.without(k)

            snap = {**x, **snap}
            if ti_snap:
                snap.update(ti_snap)

            ts_snaps = ts_snaps.with_(k, snap)
            idx_sts = self._index(t, idx_sts, k, snap)

        ts = dc.replace(ts, snaps=ts_snaps, indexes=idx_sts)
        st = dc.replace(st, tables=st.tables.with_(t.m._store_name, ts))

        return st

    async def _delete(
            self,
            st: _State,
            m: Mapper,
            keys: ta.Sequence[ta.Any],
    ) -> _State:
        t = self._table_for_mapper(m)

        ts = st.tables[t.m._store_name]
        ts_snaps = ts.snaps
        idx_sts = ts.indexes

        for k in keys:
            snap = ts_snaps[k]

            idx_sts = self._deindex(t, idx_sts, k, snap)
            ts_snaps = ts_snaps.without(k)

        ts = dc.replace(ts, snaps=ts_snaps, indexes=idx_sts)
        st = dc.replace(st, tables=st.tables.with_(t.m._store_name, ts))

        return st

    #

    class _Context(Store.Context):
        def __init__(self, o: 'InMemoryStore') -> None:
            super().__init__()

            self._o = o

            st = o._state_
            self._orig_state = st
            self._state = st

        @property
        def store(self) -> 'InMemoryStore':
            return self._o

        #

        async def __aenter__(self) -> ta.Self:
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        #

        async def finish(self) -> None:
            check.is_(self._o._state_, self._orig_state)
            self._o._state_ = self._state

        async def abort(self) -> None:
            pass

        #

        async def fetch(self, m: Mapper, k: ta.Any) -> Snap | None:
            return await self._o._fetch(self._state, m, k)

        async def lookup(self, m: Mapper, where: ta.Mapping[str, ta.Any]) -> ta.Sequence[Snap]:
            return await self._o._lookup(self._state, m, where)

        #

        async def auto_key_insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> ta.Mapping[ta.Any, ta.Any]:
            st, iak = await self._o._auto_key_insert(self._state, m, snaps)
            self._state = st
            return iak

        async def insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> None:
            self._state = await self._o._insert(self._state, m, snaps)

        async def update(self, m: Mapper, diffs: ta.Sequence[tuple[ta.Any, Snap]]) -> None:
            self._state = await self._o._update(self._state, m, diffs)

        async def delete(self, m: Mapper, keys: ta.Sequence[ta.Any]) -> None:
            self._state = await self._o._delete(self._state, m, keys)

    #

    def create_context(
            self,
            *,
            transaction: bool | ta.Literal['default'] = 'default',
    ) -> ta.AsyncContextManager[Store.Context]:
        check.in_(transaction, ('default', False))
        return self._Context(self)
