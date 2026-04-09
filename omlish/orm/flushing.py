# ruff: noqa: SLF001
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from ..algorithm.toposort import mut_toposort
from .errors import FinalFieldModifiedError
from .keys import _AutoKey
from .mappers import Mapper
from .snaps import Snap


if ta.TYPE_CHECKING:
    from .sessions import Session


##


class _SessionFlusher:
    def __init__(self, session: Session) -> None:
        super().__init__()

        self._session = session

    #

    @dc.dataclass(frozen=True)
    class _DirtyEntities:
        m: Mapper

        _: dc.KW_ONLY

        ak_inserts: ta.Mapping[_AutoKey, tuple[Session._Entity, Snap]]
        vk_inserts: ta.Sequence[tuple[Session._Entity, Snap]]
        updates: ta.Sequence[tuple[Session._Entity, Snap, ta.Sequence[str]]]
        deletes: ta.Sequence[Session._Entity]

    def _build_mapper_dirty_entities(self, m: Mapper) -> _DirtyEntities | None:
        ak_inserts: dict[_AutoKey, tuple[Session._Entity, Snap]] = {}
        vk_inserts: list[tuple[Session._Entity, Snap]] = []
        updates: list[tuple[Session._Entity, Snap, ta.Sequence[str]]] = []
        deletes: list[Session._Entity] = []

        ff_sns = m._final_field_store_names

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

                    if ff_sns and (ds_fs := [k for k in ds if k in ff_sns]):
                        raise FinalFieldModifiedError(f'Cannot modify final fields: {ds_fs}')

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
        ents_by_ak: ta.Mapping[_AutoKey, Session._Entity]
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

        for step in mut_toposort(ak_deps_by_ak):
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

    @dc.dataclass(frozen=True, kw_only=True)
    class FlushResult:
        inserted_auto_keys: ta.Mapping[_AutoKey, ta.Any]
        ent_writeback: ta.Mapping[Session._Entity, tuple[ta.Any | None, Snap | None]]

    async def flush(self) -> FlushResult:
        sess = self._session

        #

        des = self._dirty_entities()  # noqa
        akg = self._auto_key_graph()  # noqa

        #

        iak: dict[_AutoKey, ta.Any] = {}

        def fix_snap(m: Mapper, snap: Snap) -> Snap | None:  # noqa
            kf_sn = m._key_field_store_name  # noqa
            if not any(v.__class__ is _AutoKey and k != kf_sn for k, v in snap.items()):
                return None
            return {k: iak[v] for k, v in snap.items() if v.__class__ is _AutoKey and k != kf_sn}

        #

        ent_writeback: dict[Session._Entity, tuple[ta.Any | None, Snap | None]] = {}

        #

        for ak_step in akg.ak_toposort:
            for m, aks in ak_step.items():
                m_des = des[m]
                ak_snaps: list[Snap] = []
                for ak in check.not_empty(aks):
                    _, snap = m_des.ak_inserts[ak]
                    if (wb_snap := fix_snap(m, snap)) is not None:
                        snap = {**snap, **wb_snap}
                    ak_snaps.append(snap)
                ak_upd = await sess._store_ctx.auto_key_insert(m, ak_snaps)
                iak.update(ak_upd)
                for ak in aks:
                    e, snap = m_des.ak_inserts[ak]
                    wb_snap = {k: iak[v] if v.__class__ is _AutoKey else v for k, v in snap.items()}
                    ent_writeback[e] = (ak_upd[ak], wb_snap)

        #

        for m, m_des in des.items():
            if m_des.vk_inserts:
                vk_snaps: list[Snap] = []
                for e, snap in m_des.vk_inserts:
                    if (wb_snap := fix_snap(m, snap)) is not None:
                        snap = {**snap, **wb_snap}
                    ent_writeback[e] = (None, snap)
                    vk_snaps.append(snap)
                await sess._store_ctx.insert(m, vk_snaps)

            if m_des.updates:
                ud_diffs: list[tuple[ta.Any, Snap]] = []
                for e, snap, diff_fs in m_des.updates:
                    diff_snap = {k: v for k, v in snap.items() if k in diff_fs}
                    if (wb_diff_snap := fix_snap(m, diff_snap)) is not None:
                        diff_snap = {**diff_snap, **wb_diff_snap}
                    ent_writeback[e] = (None, diff_snap)
                    ud_diffs.append((e.k._k, diff_snap))  # type: ignore[attr-defined]  # must be a _ValKey
                await sess._store_ctx.update(m, ud_diffs)

            if m_des.deletes:
                del_ks: list[ta.Any] = []
                for e in m_des.deletes:
                    ent_writeback[e] = (None, None)
                    del_ks.append(e.k._k)  # type: ignore[attr-defined]  # must be a _ValKey
                await sess._store_ctx.delete(m, del_ks)

        #

        return self.FlushResult(
            inserted_auto_keys=iak,
            ent_writeback=ent_writeback,
        )
