from __future__ import annotations

import functools
import operator
import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc

from ..helpers import all_int
from ..helpers import prod
from ..shape.symbolic import Node
from ..shape.symbolic import NumNode
from ..shape.symbolic import Variable
from ..shape.symbolic import VariableOrNum
from ..shape.symbolic import sint


@functools.lru_cache(maxsize=None)
def filter_strides(shape: tuple[int, ...], strides: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(stride if shp != 1 else 0 for stride, shp in zip(strides, shape))


@functools.lru_cache(maxsize=None)
def strides_for_shape(shape: tuple[int, ...]) -> tuple[int, ...]:
    strides = [1] if shape else []
    for d in shape[::-1][:-1]:
        strides = [d * strides[0]] + strides
    return filter_strides(shape, tuple(strides))


@dc.dataclass(frozen=True)
class View:
    shape: tuple[sint, ...]
    strides: tuple[sint, ...]
    offset: sint
    mask: ta.Optional[tuple[tuple[sint, sint], ...]]
    contiguous: bool

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def create(
        shape: tuple[sint, ...],
        strides: ta.Optional[tuple[sint, ...]] = None,
        offset: sint = 0,
        mask: ta.Optional[tuple[tuple[sint, sint], ...]] = None,
    ):
        strides = filter_strides(shape, strides) if strides else strides_for_shape(shape)
        contiguous = (
            offset == 0
            and mask is None
            and all(s1 == s2 for s1, s2 in zip(strides, strides_for_shape(shape)))
        )
        return View(shape, strides, offset, mask, contiguous)

    def vars(self) -> list[Variable]:
        flatten_mask = tuple(x for m in self.mask for x in m) if self.mask is not None else tuple()
        return col.unique(
            functools.reduce(
                operator.add,
                [
                    x.vars()
                    for x in self.shape + self.strides + (self.offset,) + flatten_mask
                    if isinstance(x, Node)
                ],
                [],
            ),
        )

    def unbind(self) -> View:
        unbound_vars: dict[VariableOrNum, Node] = {v: v.unbind()[0] for v in self.vars() if v.val is not None}
        new_shape = tuple([s if isinstance(s, int) else s.substitute(unbound_vars) for s in self.shape])
        new_strides = tuple([s if isinstance(s, int) else s.substitute(unbound_vars) for s in self.strides])
        new_offset = self.offset if isinstance(self.offset, int) else self.offset.substitute(unbound_vars)
        new_mask = tuple(
            (
                a if isinstance(a, int) else a.substitute(unbound_vars),
                b if isinstance(b, int) else b.substitute(unbound_vars),
            )
            for (a, b) in self.mask
        ) if self.mask is not None else None
        return View.create(new_shape, new_strides, new_offset, new_mask)

    # MovementOps live here now

    def __unsafe_resize(self, arg: tuple[tuple[sint, sint], ...], mask=None) -> View:
        offset = sum([s * x[0] for s, x in zip(self.strides, arg)])
        if self.mask:
            # move the old mask
            nmask = tuple(
                [
                    (max(mx - ax, 0), min(my - ax, ay - ax))
                    for (mx, my), (ax, ay) in zip(self.mask, arg)
                ]
            )
            # merge the masks if we have two
            mask = (
                tuple(
                    [
                        (max(mx1, mx2), min(my1, my2))
                        for (mx1, my1), (mx2, my2) in zip(nmask, mask)
                    ]
                )
                if mask is not None
                else nmask
            )
        shape = [y - x for x, y in arg]
        return View.create(
            tuple(s.b if isinstance(s, NumNode) else s for s in shape),
            self.strides,
            self.offset + offset,
            mask,
        )

    @functools.lru_cache(maxsize=None)  # pylint: disable=method-cache-max-size-none
    def pad(self, arg: tuple[tuple[int, int], ...]) -> View:
        assert all((b >= 0 and e >= 0) for b, e in arg) and len(arg) == len(self.shape)
        if any(b or e for b, e in arg):
            zvarg = tuple([(-b, s + e) for s, (b, e) in zip(self.shape, arg)])
            mask = tuple([(b, s + b) for s, (b, _) in zip(self.shape, arg)])
            return self.__unsafe_resize(zvarg, mask=mask)
        return self

    @functools.lru_cache(maxsize=None)  # pylint: disable=method-cache-max-size-none
    def shrink(self, arg: tuple[tuple[sint, sint], ...]) -> View:
        assert all((b >= 0 and e <= s) for s, (b, e) in zip(self.shape, arg)) and len(
            arg
        ) == len(self.shape)
        return self.__unsafe_resize(arg)

    @functools.lru_cache(maxsize=None)  # pylint: disable=method-cache-max-size-none
    def expand(self, new_shape: tuple[sint, ...]) -> View:
        assert len(new_shape) == len(self.shape)
        if 0 in self.shape:
            assert (
                all((s == x == 0) or (s > 0 and (x % s) == 0) for s, x in zip(self.shape, new_shape))
            ), f"can't expand {self.shape} into {new_shape}"
            return View.create(new_shape)
        assert (
            all((s == x or (s == 1 and st == 0)) for s, x, st in zip(self.shape, new_shape, self.strides))
        ), f"can't expand {self.shape} into {new_shape}"
        # NOTE: can the mask ever be (0,0)?
        mask = (
            tuple(
                [
                    (((0, 0) if m != (0, 1) else (0, ns)) if s != ns else m)
                    for m, s, ns in zip(self.mask, self.shape, new_shape)
                ]
            )
            if self.mask
            else None
        )
        return View.create(new_shape, self.strides, self.offset, mask)

    @functools.lru_cache(maxsize=None)  # pylint: disable=method-cache-max-size-none
    def permute(self, axis: tuple[int, ...]) -> View:
        assert all(
            isinstance(x, int) and x >= 0 and x < len(self.shape) for x in axis
        ), f"invalid permute {axis} for {self.shape}"
        assert len(set(axis)) == len(axis) and len(axis) == len(
            self.shape
        ), f"can't permute {self.shape} with {axis}"
        return View.create(
            tuple([self.shape[a] for a in axis]),
            tuple([self.strides[a] for a in axis]),
            self.offset,
            tuple([self.mask[a] for a in axis]) if self.mask is not None else None,
        )

    @functools.lru_cache(maxsize=None)  # pylint: disable=method-cache-max-size-none
    def stride(self, mul: tuple[int, ...]) -> View:
        # except for the negative case, you can build this from the others. invertible in the negative case
        assert all(
            isinstance(x, int) and x != 0 for x in mul
        ), f"invalid stride {mul} for {self.shape}"
        strides = tuple([z * m for z, m in zip(self.strides, mul)])
        new_shape = tuple([(s + (abs(m) - 1)) // abs(m) for s, m in zip(self.shape, mul)])
        offset = sum([(s - 1) * z for s, z, m in zip(self.shape, self.strides, mul) if m < 0])
        mask = (
            tuple(
                [
                    (
                        ((mx if m > 0 else s - my) + (abs(m) - 1)) // abs(m),
                        ((my if m > 0 else s - mx) + (abs(m) - 1)) // abs(m),
                    )
                    for (mx, my), s, m in zip(self.mask, self.shape, mul)
                ]
            )
            if self.mask is not None
            else None
        )
        return View.create(new_shape, strides, self.offset + offset, mask)

    @functools.lru_cache(maxsize=None)  # pylint: disable=method-cache-max-size-none
    def reshape(self, new_shape: tuple[sint, ...]) -> ta.Optional[View]:
        if self.shape == new_shape:
            return self

        assert all(x >= 0 for x in new_shape), f"shape can't contain negative numbers {new_shape}"
        if 0 in self.shape:
            assert 0 in new_shape, f"cannot reshape 0 size to {new_shape}"
            return View.create(new_shape)

        # check for the same size
        if all_int(self.shape):
            assert (
                all(isinstance(s, (int, Variable)) for s in new_shape)
            ), f"{self.shape=} -> {new_shape=} contains non (int, Variable) dim"
            assert (
                prod(self.shape) == prod([s if isinstance(s, int) else ta.cast(Variable, s).val for s in new_shape])
            ), f"size mismatched, can't reshape {self.shape=} -> {new_shape=}"

        # after the asserts, it's okay to check contiguous
        if self.contiguous:
            return View.create(new_shape)

        # check if this is adding or removing 1s (only)
        # NOTE: this is optional, but removes most calls to (expensive!) merge_views (with mask, not optional)
        if [x for x in self.shape if x != 1] == [x for x in new_shape if x != 1]:
            new_strides: list[sint] = [y for x, y in zip(self.shape, self.strides) if x != 1]
            new_strides_tuple: tuple[sint, ...] = tuple([0 if x == 1 else new_strides.pop(0) for x in new_shape])
            new_mask_tuple: ta.Optional[tuple[tuple[sint, sint], ...]] = None
            if self.mask:
                for x, y in zip(self.shape, self.mask):
                    if x == 1 and y != (0, 1):
                        new_mask_tuple = ((0, 0),) * len(new_shape)
                        break
                else:
                    new_mask: list[tuple[sint, sint]] = [y for x, y in zip(self.shape, self.mask) if x != 1]
                    new_mask_tuple = tuple([(0, 1) if x == 1 else new_mask.pop(0) for x in new_shape])
            return View.create(
                new_shape, new_strides_tuple, self.offset, new_mask_tuple
            )

        # TODO: bring the merge_views logic here for more caching

        return None
