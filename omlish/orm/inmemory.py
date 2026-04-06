# ruff: noqa: SLF001
import typing as ta

from .. import check
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

    #

    class _Table:
        def __init__(self, m: Mapper) -> None:
            super().__init__()

            self.m = m

            self.snaps: dict[ta.Any, Snap] = {}

            self.indexes: dict[tuple[str, ...], dict[tuple[ta.Any, ...], set[ta.Any]]] = {
                it: {}
                for it in sorted(set(m.index_field_store_names.values()))
            }

            self.index_lookup: dict[frozenset[str], tuple[str, ...]] = {frozenset(t): t for t in self.indexes}

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

    class _Context(Store.Context):
        def __init__(self, o: 'InMemoryStore') -> None:
            super().__init__()

            self._o = o

        @property
        def store(self) -> 'InMemoryStore':
            return self._o

        #

        def __enter__(self) -> ta.Self:
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        #

        def finish(self) -> None:
            pass

        def abort(self) -> None:
            pass

        #

        def fetch(self, m: Mapper, k: ta.Any) -> Snap | None:
            check.not_in(k.__class__, WRAPPER_TYPES)
            try:
                t = self._o._table_for_mapper(m)
            except KeyError:
                return None
            return t.snaps.get(k)

        def lookup(self, m: Mapper, where: ta.Mapping[str, ta.Any]) -> ta.Sequence[Snap]:
            t = self._o._table_for_mapper(m)

            if not where:
                return list(t.snaps.values())

            if t.m.key_field.store_name in where:
                if (ks := self.fetch(m, where[t.m.key_field.store_name])) is not None:
                    return [ks]
                else:
                    return []

            fl = frozenset(where)

            bt: tuple[str, ...] | None = None
            bs: frozenset[str] | None = None
            bi: int | None = None

            for il, it in t.index_lookup.items():
                iz = il - fl
                if iz:
                    continue
                di = len(it)
                if not di:
                    continue
                if bi is not None and bi > di:
                    continue
                bt = it
                bs = il
                bi = di

            del il
            del it

            if bt is None:
                lst: list[Snap] = []

                for v in t.snaps.values():
                    for fk, fv in where.items():
                        if v[fk] != fv:
                            break
                    else:
                        lst.append(v)

                return lst

            ik = tuple(where[k] for k in bt)
            ig = [(k, where[k]) for k in fl - bs]  # type: ignore[operator]

            ix = t.indexes[bt]  # noqa
            try:
                xs = ix[ik]
            except KeyError:
                return []

            if not ig:
                return [t.snaps[k] for k in xs]

            lst = []

            for k in ig:
                v = t.snaps[k]
                for fk, fv in ig:
                    if v[fk] != fv:
                        break
                else:
                    lst.append(v)

            return lst

        #

        def _index(self, t: 'InMemoryStore._Table', k: ta.Any, snap: Snap) -> None:  # noqa
            for it, idc in t.indexes.items():
                ik = tuple(snap[f] for f in it)
                try:
                    iz = idc[ik]
                except KeyError:
                    iz = idc[ik] = set()
                iz.add(k)

        def _deindex(self, t: 'InMemoryStore._Table', k: ta.Any, snap: Snap) -> None:  # noqa
            for it, idc in t.indexes.items():
                ik = tuple(snap[f] for f in it)
                iz = idc[ik]
                iz.remove(k)
                if not iz:
                    del idc[ik]

        def auto_key_insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> ta.Mapping[ta.Any, ta.Any]:
            t = self._o._table_for_mapper(m)
            kf_sn = m._key_field_store_name
            iak: dict[ta.Any, ta.Any] = {}
            for snap in snaps:
                k = snap[kf_sn]
                ak = len(t.snaps) + 1
                while ak in t.snaps:
                    ak += 1
                iak[k] = ak
                k = ak
                snap = {**snap, kf_sn: k}
                for sk, sv in snap.items():  # noqa
                    check.not_in(sv.__class__, WRAPPER_TYPES)
                check.not_in(k, t.snaps)
                t.snaps[k] = snap
                self._index(t, k, snap)
            return iak

        def insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> None:
            t = self._o._table_for_mapper(m)
            kf_sn = m._key_field_store_name
            for snap in snaps:
                k = snap[kf_sn]
                for sk, sv in snap.items():  # noqa
                    check.not_in(sv.__class__, WRAPPER_TYPES)
                check.not_in(k, t.snaps)
                t.snaps[k] = snap
                self._index(t, k, snap)

        def update(self, m: Mapper, diffs: ta.Sequence[tuple[ta.Any, Snap]]) -> None:
            t = self._o._table_for_mapper(m)
            kf_sn = m._key_field_store_name
            for k, snap in diffs:
                check.not_in(kf_sn, snap)
                kt = k.__class__
                check.not_in(kt, WRAPPER_TYPES)
                for sk, sv in snap.items():  # noqa
                    check.not_in(sv.__class__, WRAPPER_TYPES)
                x = t.snaps[k]
                self._deindex(t, k, x)
                snap = {**x, **snap}
                t.snaps[k] = snap
                self._index(t, k, snap)

        def delete(self, m: Mapper, keys: ta.Sequence[ta.Any]) -> None:
            t = self._o._table_for_mapper(m)
            for k in keys:
                snap = t.snaps[k]
                del t.snaps[k]
                self._deindex(t, k, snap)

    #

    def create_context(self) -> ta.ContextManager[Store.Context]:
        return self._Context(self)
