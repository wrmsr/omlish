"""
Paged, cursor-based access to a timeline's past - the lazy-scrollback machinery, uniform across frontends and across
live/resumed sessions.

Cursors are *opaque*: a `TimelineCursor` is only meaningful to (the kind of) history that minted it - its `realm` names
the region it points into ('live' state positions vs 'storage' seqs) and its `key` is that realm's coordinate. Windows
returned by adjacent queries may overlap at region seams or where tool-pairing extends a fetch; consumers are expected
to apply window items by id (upsert), which the projector machinery does.

`CompositeTimelineHistory` is the principal implementation: it stitches the persisted prefix (storage) to the live
suffix (state), making resume-then-watch and scroll-back-while-streaming the same operation. Its region split works as
follows: at first use it captures an *epoch* - the max persisted seq - and treats rows with seq <= epoch as the storage
region and the live state as everything after. Rows persisted after the epoch are exactly the live items being
persisted at turn ends, and are excluded from storage-region queries; as a belt-and-suspenders for late construction,
rows whose message uuids appear in the live snapshot are excluded too.

COHERENCE INVARIANT (load-bearing; see the package README): every method of every implementation must capture any
snapshot of *live, mutable* state synchronously - before its first await. `Timeline.attach` relies on this to guarantee
that a window plus the events after its watermark contain no gaps and no duplicates.

Tool pairing at page boundaries: a page beginning with results whose uses lie just before it is *extended backward*
(bounded) until pairing closes; a page ending with an as-yet-unresulted use yields a PENDING item that later windows
(or live events) advance. When extension hits its bound, leading results surface as orphan-result tool items - visible,
mergeable by consumers via tool-call id, and healed by wider windows.
"""
import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...chat.metadata import MessageUuid
from ...drivers.storage.manager import DriverStorageManager
from ...drivers.storage.types import StoredMessage
from .items import TimelineItem
from .items import TimelineItemId
from .items import ToolUseTimelineItem
from .state import TimelineState
from .translate import timeline_translate_anchored_chat


##


LIVE_TIMELINE_CURSOR_REALM = 'live'
STORAGE_TIMELINE_CURSOR_REALM = 'storage'


@dc.dataclass(frozen=True)
class TimelineCursor(lang.Final):
    """Opaque - resolvable only by (the kind of) history that minted it."""

    item_id: TimelineItemId
    realm: str
    key: int


class TimelineCursorError(Exception):
    pass


@dc.dataclass()
class UnresolvableTimelineCursorError(TimelineCursorError):
    cursor: TimelineCursor


@dc.dataclass(frozen=True, kw_only=True)
class TimelineWindow(lang.Final):
    items: ta.Sequence[TimelineItem]

    has_before: bool = False
    has_after: bool = False

    before_cursor: TimelineCursor | None = None
    after_cursor: TimelineCursor | None = None


EMPTY_TIMELINE_WINDOW = TimelineWindow(items=())


##


class TimelineHistory(lang.Abstract):
    @abc.abstractmethod
    def get_latest(self, limit: int) -> ta.Awaitable[TimelineWindow]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_before(self, cursor: TimelineCursor, limit: int) -> ta.Awaitable[TimelineWindow]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_after(self, cursor: TimelineCursor, limit: int) -> ta.Awaitable[TimelineWindow]:
        raise NotImplementedError


##
# Live state


def _live_cursor(state: TimelineState, position: int) -> TimelineCursor:
    item = check.not_none(state.get_item_at_position(position))

    return TimelineCursor(
        item.id,
        LIVE_TIMELINE_CURSOR_REALM,
        position,
    )


def _resolve_live_cursor(state: TimelineState, cursor: TimelineCursor) -> int:
    check.arg(cursor.realm == LIVE_TIMELINE_CURSOR_REALM)

    if (item := state.get_item_at_position(cursor.key)) is not None and item.id == cursor.item_id:
        return cursor.key

    if (pos := state.get_position(cursor.item_id)) is not None:
        return pos

    raise UnresolvableTimelineCursorError(cursor)


def _make_live_window(
        state: TimelineState,
        start_pos: int,
        stop_pos: int,
        *,
        has_after_tail: bool = False,
) -> TimelineWindow:
    """
    Builds a window over live positions [start_pos, stop_pos). `has_after_tail`: treat the live end as having more.
    """

    first = state.first_position
    end = state.next_position

    start_pos = max(start_pos, first)
    stop_pos = min(stop_pos, end)
    check.arg(start_pos <= stop_pos)

    items = tuple(
        check.not_none(state.get_item_at_position(p))
        for p in range(start_pos, stop_pos)
    )

    return TimelineWindow(
        items=items,
        has_before=start_pos > first,
        has_after=(stop_pos < end) or has_after_tail,
        before_cursor=_live_cursor(state, start_pos) if items else None,
        after_cursor=_live_cursor(state, stop_pos - 1) if items else None,
    )


class StateTimelineHistory(TimelineHistory):
    """History over live state alone - for storageless/ephemeral use and as the composite's live half."""

    def __init__(
            self,
            *,
            state: TimelineState,
    ) -> None:
        super().__init__()

        self._state = state

    async def get_latest(self, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        end = self._state.next_position
        return _make_live_window(self._state, end - limit, end)

    async def get_before(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        pos = _resolve_live_cursor(self._state, cursor)
        return _make_live_window(self._state, pos - limit, pos)

    async def get_after(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        pos = _resolve_live_cursor(self._state, cursor)
        return _make_live_window(self._state, pos + 1, pos + 1 + limit)


##
# Storage


def _stored_message_uuids(rows: ta.Iterable[StoredMessage]) -> ta.Iterator[ta.Any]:
    for r in rows:
        if (mu := r.message.metadata.get(MessageUuid)) is not None:
            yield mu.v


def _translate_rows(rows: ta.Sequence[StoredMessage]) -> ta.Sequence[TimelineItem]:
    return [at.item for at in timeline_translate_anchored_chat((r.seq, r.message) for r in rows)]


def _is_leading_orphan_result(items: ta.Sequence[TimelineItem]) -> bool:
    if not items:
        return False

    return (
        isinstance(it := items[0], ToolUseTimelineItem) and
        it.use is None and
        it.result is not None
    )


# A bounded number of additional backward fetches to close tool use/result pairing at a page's leading edge.
DEFAULT_MAX_PAIRING_EXTENSIONS = 4

# The row count per pairing-extension fetch - tool batches are small.
PAIRING_EXTENSION_FETCH_SIZE = 16

_BackFetcher: ta.TypeAlias = ta.Callable[[int, int], ta.Awaitable[tuple[ta.Sequence[StoredMessage], bool]]]


async def _extend_leading_pairing(
        rows: ta.Sequence[StoredMessage],
        has_before: bool,
        fetch_before: _BackFetcher,
        *,
        max_extensions: int = DEFAULT_MAX_PAIRING_EXTENSIONS,
) -> tuple[ta.Sequence[StoredMessage], bool]:
    """
    `fetch_before(seq, n)` must return up to n rows strictly before seq (ascending) and whether more exist before
    those.
    """

    out = list(rows)

    for _ in range(max_extensions):
        if not out or not has_before:
            break

        if not _is_leading_orphan_result(_translate_rows(out)):
            break

        prev_rows, has_before = await fetch_before(out[0].seq, PAIRING_EXTENSION_FETCH_SIZE)
        if not prev_rows:
            break

        out = [*prev_rows, *out]

    return (out, has_before)


def _make_storage_window(
        rows: ta.Sequence[StoredMessage],
        *,
        has_before: bool,
        has_after: bool,
) -> TimelineWindow:
    items = _translate_rows(rows)

    return TimelineWindow(
        items=items,
        has_before=has_before,
        has_after=has_after,
        # Cursors span the fetched *row* extent (not item anchors): a trailing row folded into an earlier item must
        # not be refetched by a subsequent get_after.
        before_cursor=TimelineCursor(items[0].id, STORAGE_TIMELINE_CURSOR_REALM, rows[0].seq) if items else None,
        after_cursor=TimelineCursor(items[-1].id, STORAGE_TIMELINE_CURSOR_REALM, rows[-1].seq) if items else None,
    )


class StorageTimelineHistory(TimelineHistory):
    """History over persisted messages alone - replay translation, paged. Used standalone for pure-replay reads."""

    def __init__(
            self,
            *,
            storage: DriverStorageManager,
            max_pairing_extensions: int = DEFAULT_MAX_PAIRING_EXTENSIONS,
    ) -> None:
        super().__init__()

        self._storage = storage
        self._max_pairing_extensions = max_pairing_extensions

    async def _fetch_before(self, seq: int, n: int) -> tuple[ta.Sequence[StoredMessage], bool]:
        page = await self._storage.get_chat_page_before(seq, n)
        return (page.rows, page.has_before)

    async def _window_from_page_rows(
            self,
            rows: ta.Sequence[StoredMessage],
            *,
            has_before: bool,
            has_after: bool,
    ) -> TimelineWindow:
        rows, has_before = await _extend_leading_pairing(
            rows,
            has_before,
            self._fetch_before,
            max_extensions=self._max_pairing_extensions,
        )

        return _make_storage_window(
            rows,
            has_before=has_before,
            has_after=has_after,
        )

    async def get_latest(self, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        page = await self._storage.get_latest_chat_page(limit)
        return await self._window_from_page_rows(
            page.rows,
            has_before=page.has_before,
            has_after=page.has_after,
        )

    async def get_before(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        check.arg(cursor.realm == STORAGE_TIMELINE_CURSOR_REALM)
        check.arg(limit >= 0)

        page = await self._storage.get_chat_page_before(cursor.key, limit)
        return await self._window_from_page_rows(
            page.rows,
            has_before=page.has_before,
            has_after=True,
        )

    async def get_after(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        check.arg(cursor.realm == STORAGE_TIMELINE_CURSOR_REALM)
        check.arg(limit >= 0)

        page = await self._storage.get_chat_page_after(cursor.key, limit)
        return await self._window_from_page_rows(
            page.rows,
            has_before=True,
            has_after=page.has_after,
        )


##
# Composite


class CompositeTimelineHistory(TimelineHistory):
    """
    The persisted prefix stitched to the live suffix. See the module docstring for the epoch/dedupe region split and
    the coherence invariant every method here upholds (live snapshots are taken synchronously, before any await).
    """

    def __init__(
            self,
            *,
            storage: DriverStorageManager,
            state: TimelineState,
            max_pairing_extensions: int = DEFAULT_MAX_PAIRING_EXTENSIONS,
    ) -> None:
        super().__init__()

        self._storage = storage
        self._state = state
        self._max_pairing_extensions = max_pairing_extensions

        self._epoch_seq: int | None = None
        self._known_region_nonempty: bool | None = None

    #

    async def _get_epoch_seq(self) -> int:
        if self._epoch_seq is None:
            page = await self._storage.get_latest_chat_page(1)
            e = page.last_seq if page.last_seq is not None else 0

            # First capture wins under concurrent initialization.
            if self._epoch_seq is None:
                self._epoch_seq = e

        return self._epoch_seq

    def _region_keep(self, row: StoredMessage, epoch_seq: int, live_ids: ta.AbstractSet[TimelineItemId]) -> bool:
        if row.seq > epoch_seq:
            return False

        if (mu := row.message.metadata.get(MessageUuid)) is not None and TimelineItemId(mu.v) in live_ids:
            return False

        return True

    async def _fetch_region_before(
            self,
            before_seq: int | None,
            n: int,
            live_ids: ta.AbstractSet[TimelineItemId],
    ) -> tuple[list[StoredMessage], bool]:
        """The last n storage-region rows strictly before before_seq (or at the region's end), ascending."""

        epoch_seq = await self._get_epoch_seq()

        bound = min(before_seq, epoch_seq + 1) if before_seq is not None else epoch_seq + 1

        out: list[StoredMessage] = []
        has_more = False

        cur = bound
        while len(out) < n:
            page = await self._storage.get_chat_page_before(cur, n - len(out))
            if not page.rows:
                has_more = False
                break

            out = [
                *[r for r in page.rows if self._region_keep(r, epoch_seq, live_ids)],
                *out,
            ]

            cur = check.not_none(page.first_seq)
            has_more = page.has_before
            if not has_more:
                break

        if len(out) > n:
            has_more = True
            out = out[len(out) - n:]

        return (out, has_more)

    async def _fetch_region_after(
            self,
            after_seq: int,
            n: int,
            live_ids: ta.AbstractSet[TimelineItemId],
    ) -> tuple[list[StoredMessage], bool]:
        """Up to n storage-region rows strictly after after_seq, ascending, plus whether the region has more after."""

        epoch_seq = await self._get_epoch_seq()

        out: list[StoredMessage] = []

        cur = after_seq
        while len(out) < n:
            page = await self._storage.get_chat_page_after(cur, n - len(out))
            if not page.rows:
                break

            kept = [r for r in page.rows if self._region_keep(r, epoch_seq, live_ids)]
            out.extend(kept)

            cur = check.not_none(page.last_seq)
            if cur > epoch_seq or not page.has_after:
                break

        if len(out) > n:
            return (out[:n], True)

        return (out, False)

    async def _region_nonempty(self, live_ids: ta.AbstractSet[TimelineItemId]) -> bool:
        if self._known_region_nonempty is None:
            rows, _ = await self._fetch_region_before(None, 1, live_ids)
            self._known_region_nonempty = bool(rows)

        return self._known_region_nonempty

    #

    def _splice(
            self,
            storage_rows: ta.Sequence[StoredMessage],
            storage_has_before: bool,
            live_window: TimelineWindow | None,
    ) -> TimelineWindow:
        """Joins a storage-region row prefix to an optional live window."""

        storage_items = _translate_rows(storage_rows)

        if live_window is None:
            live_window = EMPTY_TIMELINE_WINDOW

        if not storage_items:
            return dc.replace(
                live_window,
                has_before=live_window.has_before or storage_has_before,
            )

        before_cursor = TimelineCursor(storage_items[0].id, STORAGE_TIMELINE_CURSOR_REALM, storage_rows[0].seq)

        after_cursor = live_window.after_cursor
        if after_cursor is None:
            after_cursor = TimelineCursor(storage_items[-1].id, STORAGE_TIMELINE_CURSOR_REALM, storage_rows[-1].seq)

        return TimelineWindow(
            items=(*storage_items, *live_window.items),
            has_before=storage_has_before,
            has_after=live_window.has_after,
            before_cursor=before_cursor,
            after_cursor=after_cursor,
        )

    async def _storage_prefix_spliced(
            self,
            n: int,
            live_ids: ta.AbstractSet[TimelineItemId],
            live_window: TimelineWindow | None,
    ) -> TimelineWindow:
        """Fetches the last n storage-region rows (pairing-extended) and splices them before live_window."""

        rows: ta.Sequence[StoredMessage]
        rows, has_more = await self._fetch_region_before(None, n, live_ids)

        async def fetch_before(seq: int, k: int) -> tuple[ta.Sequence[StoredMessage], bool]:
            return await self._fetch_region_before(seq, k, live_ids)

        rows, has_more = await _extend_leading_pairing(
            rows,
            has_more,
            fetch_before,
            max_extensions=self._max_pairing_extensions,
        )

        return self._splice(rows, has_more, live_window)

    #

    async def get_latest(self, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        # Live snapshot first, synchronously - the coherence invariant.
        live_items = self._state.get_items()
        live_ids = {it.id for it in live_items}
        live_end = self._state.next_position

        live_take = min(limit, len(live_items))
        live_window = _make_live_window(self._state, live_end - live_take, live_end) if live_take else None

        if (remaining := limit - live_take) <= 0:
            has_storage_before = (
                (live_window.has_before if live_window is not None else False) or
                await self._region_nonempty(live_ids)
            )

            if live_window is None:
                return dc.replace(EMPTY_TIMELINE_WINDOW, has_before=has_storage_before)

            return dc.replace(live_window, has_before=live_window.has_before or has_storage_before)

        return await self._storage_prefix_spliced(remaining, live_ids, live_window)

    async def get_before(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        # Live snapshot first, synchronously - the coherence invariant.
        live_items = self._state.get_items()
        live_ids = {it.id for it in live_items}
        live_first = self._state.first_position

        if cursor.realm == LIVE_TIMELINE_CURSOR_REALM:
            pos = _resolve_live_cursor(self._state, cursor)

            live_take = min(limit, pos - live_first)
            live_window = (
                _make_live_window(self._state, pos - live_take, pos, has_after_tail=True)
                if live_take > 0
                else dc.replace(EMPTY_TIMELINE_WINDOW, has_after=True)
            )

            if (remaining := limit - live_take) <= 0:
                if not live_window.has_before:
                    live_window = dc.replace(live_window, has_before=await self._region_nonempty(live_ids))
                return live_window

            return await self._storage_prefix_spliced(remaining, live_ids, live_window)

        elif cursor.realm == STORAGE_TIMELINE_CURSOR_REALM:
            rows: ta.Sequence[StoredMessage]
            rows, has_more = await self._fetch_region_before(cursor.key, limit, live_ids)

            async def fetch_before(seq: int, k: int) -> tuple[ta.Sequence[StoredMessage], bool]:
                return await self._fetch_region_before(seq, k, live_ids)

            rows, has_more = await _extend_leading_pairing(
                rows,
                has_more,
                fetch_before,
                max_extensions=self._max_pairing_extensions,
            )

            window = _make_storage_window(rows, has_before=has_more, has_after=True)
            return window

        else:
            raise UnresolvableTimelineCursorError(cursor)

    async def get_after(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        # Live snapshot first, synchronously - the coherence invariant.
        live_items = self._state.get_items()
        live_ids = {it.id for it in live_items}
        live_first = self._state.first_position

        if cursor.realm == LIVE_TIMELINE_CURSOR_REALM:
            pos = _resolve_live_cursor(self._state, cursor)
            return _make_live_window(self._state, pos + 1, pos + 1 + limit)

        elif cursor.realm == STORAGE_TIMELINE_CURSOR_REALM:
            rows, region_has_more = await self._fetch_region_after(cursor.key, limit, live_ids)

            if region_has_more or len(rows) >= limit:
                return _make_storage_window(
                    rows,
                    has_before=True,
                    has_after=region_has_more or bool(live_items),
                )

            # The storage region is exhausted - continue into the live suffix.
            storage_items = _translate_rows(rows)
            remaining = limit - len(storage_items)

            live_take = min(remaining, len(live_items))
            live_window = (
                _make_live_window(self._state, live_first, live_first + live_take)
                if live_take > 0 else None
            )

            if not rows:
                if live_window is not None:
                    return live_window
                return EMPTY_TIMELINE_WINDOW

            return TimelineWindow(
                items=(*storage_items, *(live_window.items if live_window is not None else ())),
                has_before=True,
                has_after=live_window.has_after if live_window is not None else bool(live_items),
                before_cursor=TimelineCursor(storage_items[0].id, STORAGE_TIMELINE_CURSOR_REALM, rows[0].seq),
                after_cursor=(
                    live_window.after_cursor
                    if live_window is not None and live_window.after_cursor is not None
                    else TimelineCursor(storage_items[-1].id, STORAGE_TIMELINE_CURSOR_REALM, rows[-1].seq)
                ),
            )

        else:
            raise UnresolvableTimelineCursorError(cursor)
