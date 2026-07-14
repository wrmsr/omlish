"""
Note that this is similar to but different from `omlish.c3` - this is for validation and debugging of real. concrete,
intended-to-be-final class bases, whereas `omlish.c3` is for computing mro of arbitrary otherwise unrelated types,
including virtual ABC's (primarily for dispatch-like code).
"""
import typing as ta


##


def _resolve_bases(bases: tuple[ta.Any, ...]) -> tuple[tuple[type, ...], tuple[int, ...]]:
    out_bases: list[type] = []
    out_orig_idxs: list[int] = []

    for i, base in enumerate(bases):
        entries = _resolve_one_base_entries(base, bases)

        for e in entries:
            if not isinstance(e, type):
                raise TypeError(f'resolved base entry at bases[{i}] is not a type: {e!r}')
            out_bases.append(e)
            out_orig_idxs.append(i)

    return tuple(out_bases), tuple(out_orig_idxs)


def _resolve_one_base_entries(base: ta.Any, bases: tuple[ta.Any, ...]) -> tuple[ta.Any, ...]:
    if isinstance(base, type):
        return (base,)

    mro_entries = getattr(base, '__mro_entries__', None)
    if mro_entries is not None:
        entries = mro_entries(bases)
        if not isinstance(entries, tuple):
            raise TypeError(f'__mro_entries__ for {base!r} returned non-tuple {entries!r}')
        return entries

    raise TypeError(f'base {base!r} is neither a type nor provides __mro_entries__')


class _Seq:
    def __init__(
        self,
        items: list[type],
        *,
        origin_idxs: list[int] | None = None,
        fixed_origin_idx: int | None = None,
    ) -> None:
        self.items = items
        self._origin_idxs = origin_idxs
        self._fixed_origin_idx = fixed_origin_idx

    def head(self) -> type:
        return self.items[0]

    def head_origin_idx(self) -> int:
        if self._origin_idxs is not None:
            return self._origin_idxs[0]
        if self._fixed_origin_idx is None:
            raise RuntimeError(f'head_origin_idx called on {self!r} with no origin_idxs or fixed_origin_idx')
        return self._fixed_origin_idx

    def iter_pairs(self, orig_bases: tuple[ta.Any, ...]) -> tuple[tuple[ta.Any, type], ...]:
        if self._origin_idxs is not None:
            return tuple((orig_bases[oi], ty) for oi, ty in zip(self._origin_idxs, self.items))
        else:
            if self._fixed_origin_idx is None:
                raise RuntimeError(f'iter_pairs called on {self!r} with no origin_idxs or fixed_origin_idx')
            ob = orig_bases[self._fixed_origin_idx]
            return tuple((ob, ty) for ty in self.items)

    def pop_head_if(self, candidate: type) -> None:
        if self.items and self.items[0] is candidate:
            self.items.pop(0)
            if self._origin_idxs is not None:
                self._origin_idxs.pop(0)

    def tail_contains(self, ty: type) -> bool:
        return ty in self.items[1:]


def _merge_mro_or_raise(
    *,
    orig_bases: tuple[ta.Any, ...],
    expanded_bases: tuple[type, ...],
    expanded_orig_idxs: tuple[int, ...],
) -> None:
    seqs: list[_Seq] = []

    for base, orig_idx in zip(expanded_bases, expanded_orig_idxs):
        seqs.append(_Seq(list(base.__mro__), fixed_origin_idx=orig_idx))

    seqs.append(
        _Seq(list(expanded_bases), origin_idxs=list(expanded_orig_idxs)),
    )

    while True:
        seqs = [s for s in seqs if s.items]
        if not seqs:
            return

        candidate: type | None = None
        for s in seqs:
            h = s.head()
            if all(not other.tail_contains(h) for other in seqs):
                candidate = h
                break

        if candidate is None:
            conflicts = _build_conflicts(orig_bases=orig_bases, seqs=seqs)
            remaining_sequences = tuple(s.iter_pairs(orig_bases) for s in seqs)
            raise MroError(
                bases=orig_bases,
                expanded_bases=expanded_bases,
                conflicts=conflicts,
                remaining_sequences=remaining_sequences,
            )

        for s in seqs:
            s.pop_head_if(candidate)


def _build_conflicts(
    *,
    orig_bases: tuple[ta.Any, ...],
    seqs: list[_Seq],
) -> dict[str, tuple[ta.Any, ...]]:
    out: dict[str, tuple[ta.Any, ...]] = {}
    used_keys: set[str] = set()

    for s in seqs:
        h = s.head()
        blockers: list[int] = []

        for other in seqs:
            if other is s:
                continue
            if other.tail_contains(h):
                blocker_idx = other.head_origin_idx()
                if blocker_idx not in blockers:
                    blockers.append(blocker_idx)

        if not blockers:
            continue

        involved_idxs = [s.head_origin_idx(), *blockers]
        key = _dedupe_key(_type_name(h), used_keys)
        out[key] = tuple(orig_bases[i] for i in involved_idxs)

    return out


def _type_name(ty: type) -> str:
    mod = getattr(ty, '__module__', None)
    qn = getattr(ty, '__qualname__', None)
    if mod and qn:
        return f'{mod}.{qn}'
    n = getattr(ty, '__name__', None)
    if n:
        return n
    return repr(ty)


def _dedupe_key(key: str, used: set[str]) -> str:
    if key not in used:
        used.add(key)
        return key

    i = 2
    while True:
        k = f'{key}#{i}'
        if k not in used:
            used.add(k)
            return k
        i += 1


#


class MroError(TypeError):
    """
    Raised when the given base list cannot be merged into a consistent C3 MRO.

    Attributes:
        bases:
            The exact original objects passed to try_mro(...).

        expanded_bases:
            The flattened type bases after applying __mro_entries__.

        conflicts:
            Mapping from a problematic remaining merge-head name to the ordered original base-list objects involved in
            that conflict.

            The first item is the original base object whose sequence currently proposes that head; subsequent items are
            the original base objects whose current heads force that head to come later.

            These are the *exact* original base-list objects, not their expanded types, and may therefore be arbitrary /
            unhashable objects.

        remaining_sequences:
            The C3 merge sequences at the exact failure point, rendered in terms of the original base-list objects. Each
            entry is a tuple of pairs:
                ((original_base_object, remaining_type), ...)
            where original_base_object is the exact object from the input base list responsible for that remaining type
            position.
    """

    def __init__(
            self,
            *,
            bases: tuple[ta.Any, ...],
            expanded_bases: tuple[type, ...],
            conflicts: dict[str, tuple[ta.Any, ...]],
            remaining_sequences: tuple[tuple[tuple[ta.Any, type], ...], ...],
    ) -> None:
        self.bases = bases
        self.expanded_bases = expanded_bases
        self.conflicts = conflicts
        self.remaining_sequences = remaining_sequences
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        lines = [
            'Cannot create a consistent method resolution order (MRO) for bases.',
            '',
            'Original bases:',
        ]
        for i, b in enumerate(self.bases):
            lines.append(f'  [{i}] {b!r}')

        lines.append('')
        lines.append('Expanded bases:')
        for i, b in enumerate(self.expanded_bases):
            lines.append(f'  [{i}] {_type_name(b)}')

        lines.append('')
        lines.append('Conflicts:')
        for k, vs in self.conflicts.items():
            rendered = ', '.join(repr(v) for v in vs)
            lines.append(f'  {k}: ({rendered})')

        lines.append('')
        lines.append('Remaining sequences at failure:')
        for i, seq in enumerate(self.remaining_sequences):
            rendered = ', '.join(f'({ob!r}, {_type_name(ty)})' for ob, ty in seq)
            lines.append(f'  [{i}] [{rendered}]')

        return '\n'.join(lines)


def try_mro(*bases: ta.Any) -> tuple:
    """
    Validate whether `class X(*bases): ...` would have a consistent MRO.

    This performs C3 linearization on the resolved bases without actually creating a class. It preserves a back-map to
    the *original* base-list objects, including generic aliases and arbitrary __mro_entries__ expanders.

    Returns:
        The given bases if the MRO is consistent.

    Raises:
        MroError:
            If the bases cannot be merged into a consistent MRO.
        TypeError:
            If a base is invalid in a way unrelated to MRO consistency (for example, not a type and with no
            __mro_entries__).
    """

    orig_bases = tuple(bases)
    expanded_bases, expanded_orig_idxs = _resolve_bases(orig_bases)

    _merge_mro_or_raise(
        orig_bases=orig_bases,
        expanded_bases=expanded_bases,
        expanded_orig_idxs=expanded_orig_idxs,
    )

    return bases
