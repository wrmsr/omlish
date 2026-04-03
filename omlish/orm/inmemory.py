# ruff: noqa: SLF001
import typing as ta

from .. import check
from .keys import _AutoKey
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

    def fetch(self, m: Mapper, k: ta.Any) -> Snap | None:
        check.not_in(k.__class__, WRAPPER_TYPES)
        try:
            t = self._table_for_mapper(m)
        except KeyError:
            return None
        return t.snaps.get(k)

    #

    def lookup(self, m: Mapper, where: ta.Mapping[str, ta.Any]) -> ta.Sequence[Snap]:
        t = self._table_for_mapper(m)

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

    def flush(self, m: Mapper, b: Store.FlushBatch) -> Store.FlushResult:
        kf_sn = m._key_field._store_name

        t = self._table_for_mapper(m)

        iak: dict[ta.Any, ta.Any] = {}

        def index(k: ta.Any, snap: Snap) -> None:  # noqa
            for it, idc in t.indexes.items():
                ik = tuple(snap[f] for f in it)
                try:
                    iz = idc[ik]
                except KeyError:
                    iz = idc[ik] = set()
                iz.add(k)

        def deindex(k: ta.Any, snap: Snap) -> None:  # noqa
            for it, idc in t.indexes.items():
                ik = tuple(snap[f] for f in it)
                iz = idc[ik]
                iz.remove(k)
                if not iz:
                    del idc[ik]

        for snap in b.insert or ():
            k = snap[kf_sn]
            kt = k.__class__
            if kt is _AutoKey:
                ak = len(t.snaps) + 1
                while ak in t.snaps:
                    ak += 1
                iak[k] = ak
                k = ak
                snap[kf_sn] = k
            # FIXME:
            # for sk, sv in snap.items():  # noqa
            #     check.not_in(sv.__class__, WRAPPER_TYPES)
            check.not_in(k, t.snaps)
            t.snaps[k] = snap
            index(k, snap)

        for k, snap in b.update or ():
            check.not_in(kf_sn, snap)
            kt = k.__class__
            check.not_in(kt, WRAPPER_TYPES)
            # FIXME:
            # for sk, sv in snap.items():  # noqa
            #     check.not_in(sv.__class__, WRAPPER_TYPES)
            x = t.snaps[k]
            deindex(k, x)
            snap = {**x, **snap}
            t.snaps[k] = snap
            index(k, snap)

        for k in b.delete or ():
            snap = t.snaps[k]
            del t.snaps[k]
            deindex(k, snap)

        return self.FlushResult(
            inserted_auto_keys=iak or None,
        )
