# ruff: noqa: SLF001
import typing as ta

from .. import check
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

    def flush(self) -> None:
        session = self._session
        check.state(not session._aborted)

        entity_ops: list[tuple[
            Mapper,
            Store.FlushResult,
            list[tuple[
                Session._Entity,
                ta.Any | None,
                Snap | None,
            ]],
        ]] = []

        for cls, cd in session._entities_by_key_by_cls.items():
            eol: list = []

            m = session._registry.mapper_for_cls(cls)

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

            fr = session._store.flush(m, batch)

            entity_ops.append((m, fr, eol))

        for m, fr, eol in entity_ops:
            ed = session._entities_by_key_by_cls[m._cls]

            for e, e_obj, e_snap in eol:
                if (ek := e.k).__class__ is _AutoKey:
                    k = _Key(fr.inserted_auto_keys[ek])  # type: ignore[index]

                    check.not_in(k, ed)  # noqa
                    check.is_(session._entities_by_auto_key[ek], e)  # noqa

                    del ed[ek]

                    e.k = k
                    setattr(e_obj, m._key_field._name, k)
                    ed[k] = e

                if e_obj is None and (xo := e.obj) is not None:
                    del session._entities_by_obj_id[id(xo)]

                e.obj = e_obj
                e.snap = e_snap
