# ruff: noqa: SLF001
import abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from ..algorithm.toposort import mut_toposort
from .keys import _AutoKey
from .keys import _Key
from .keys import _unwrap_key
from .mappers import Mapper
from .snaps import Snap
from .stores import Store


if ta.TYPE_CHECKING:
    from .sessions import Session


##


class _SessionFlusher:
    def __init__(self, session: 'Session') -> None:
        super().__init__()

        self._session = session

    #

    @dc.dataclass(frozen=True)
    class _DirtyEntities:
        m: Mapper

        _: dc.KW_ONLY

        ak_inserts: ta.Mapping[_AutoKey, tuple['Session._Entity', Snap]]
        vk_inserts: ta.Sequence[tuple['Session._Entity', Snap]]
        updates: ta.Sequence[tuple['Session._Entity', Snap, ta.Sequence[str]]]
        deletes: ta.Sequence['Session._Entity']

    def _build_mapper_dirty_entities(self, m: Mapper) -> _DirtyEntities | None:
        ak_inserts: dict[_AutoKey, tuple[Session._Entity, Snap]] = {}
        vk_inserts: list[tuple[Session._Entity, Snap]] = []
        updates: list[tuple[Session._Entity, Snap, ta.Sequence[str]]] = []
        deletes: list[Session._Entity] = []

        for e in self._session._entities_by_key_by_cls[m._cls].values():
            if e.obj is None:
                if e.snap is None:
                    continue

                check.state(e.k.__class__ is not _AutoKey)
                deletes.append(e)

            else:
                snap = e.m.obj_to_snap(e.obj)
                if snap == e.snap:
                    continue

                is_ak = (k := e.k).__class__ is _AutoKey

                if (xs := e.snap) is None:
                    if is_ak:
                        ak_inserts[k] = (e, snap)  # type: ignore[index]
                    else:
                        vk_inserts.append((e, snap))

                elif (ds := tuple(k for k, nv in snap.items() if xs[k] != nv)):
                    check.state(not is_ak)
                    updates.append((e, snap, ds))

        if not (
                ak_inserts or
                vk_inserts or
                updates or
                deletes
        ):
            return None

        return self._DirtyEntities(
            m,

            ak_inserts=ak_inserts,
            vk_inserts=vk_inserts,
            updates=updates,
            deletes=deletes,
        )

    @lang.cached_function
    def _dirty_entities(self) -> ta.Mapping[Mapper, _DirtyEntities]:
        dct: dict[Mapper, _SessionFlusher._DirtyEntities] = {}

        for m in self._session._registry._mappers:
            if (des := self._build_mapper_dirty_entities(m)) is not None:
                dct[m] = des

        return dct

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class _AutoKeyGraph:
        ents_by_ak: ta.Mapping[_AutoKey, 'Session._Entity']
        ak_toposort: ta.Sequence[ta.Mapping[Mapper, ta.AbstractSet[_AutoKey]]]

    def _auto_key_graph(self) -> _AutoKeyGraph:
        ents_by_ak: dict[_AutoKey, Session._Entity] = {}

        ak_deps_by_ak: dict[_AutoKey, set[_AutoKey]] = {}

        for m, des in self._dirty_entities().items():
            if not des.ak_inserts:
                continue

            kf_sn = m._key_field_store_name

            for ak, (ent, snap) in des.ak_inserts.items():
                check.not_in(ak, ents_by_ak)
                ents_by_ak[ak] = ent

                ak_deps_by_ak[ak] = {
                    v
                    for k, v in snap.items()
                    if k != kf_sn and (v.__class__ is _AutoKey)
                }

        ak_toposort: list[dict[Mapper, set[_AutoKey]]] = []

        for i, step in enumerate(mut_toposort(ak_deps_by_ak)):
            akd: dict[Mapper, set[_AutoKey]] = {}

            for ak in check.not_empty(step):
                e = ents_by_ak[ak]
                try:
                    x = akd[e.m]
                except KeyError:
                    akd[e.m] = {ak}
                else:
                    x.add(ak)

            ak_toposort.append(akd)

        return self._AutoKeyGraph(
            ents_by_ak=ents_by_ak,
            ak_toposort=ak_toposort,
        )

    #

    def flush(self) -> None:
        sess = self._session

        check.state(not sess._aborted)

        des = self._dirty_entities()  # noqa
        akg = self._auto_key_graph()  # noqa

        iak: dict[_AutoKey, ta.Any] = {}

        def fix_snap(m: Mapper, snap: Snap) -> Snap:  # noqa
            kf_sn = m._key_field_store_name
            return {k: iak[v] if v.__class__ is _AutoKey and k != kf_sn else v for k, v in snap.items()}

        for ak_step in akg.ak_toposort:
            for m, aks in ak_step.items():
                m_des = des[m]
                ak_snaps: list[Snap] = []
                for ak in aks:
                    _, snap = m_des.ak_inserts[ak]
                    ak_snaps.append(fix_snap(m, snap))
                ak_upd = sess._store.auto_key_insert(m, ak_snaps)
                iak.update(ak_upd)

        entity_ops: list[tuple[
            Mapper,
            Store.FlushResult,
            list[tuple[
                Session._Entity,
                ta.Any | None,
                Snap | None,
            ]],
        ]] = []

        for cls, cd in sess._entities_by_key_by_cls.items():
            eol: list = []

            m = sess._registry.mapper_for_cls(cls)

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

            fr = sess._store.flush(m, batch)

            entity_ops.append((m, fr, eol))

        for m, fr, eol in entity_ops:
            ed = sess._entities_by_key_by_cls[m._cls]

            for e, e_obj, e_snap in eol:
                if (ek := e.k).__class__ is _AutoKey:
                    k = _Key(fr.inserted_auto_keys[ek])  # type: ignore[index]

                    check.not_in(k, ed)  # noqa
                    check.is_(sess._entities_by_auto_key[ek], e)  # noqa

                    del ed[ek]

                    e.k = k
                    setattr(e_obj, m._key_field._name, k)
                    ed[k] = e

                if e_obj is None and (xo := e.obj) is not None:
                    del sess._entities_by_obj_id[id(xo)]

                e.obj = e_obj
                e.snap = e_snap
