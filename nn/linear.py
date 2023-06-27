import collections
import io
import itertools
import math
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import dispatch
from omlish.collections import coerce

from . import ops2  # noqa
from . import symbolic as sym
from . import uops as uo
from .codegen import Codegen
from .codegen import CodegenOp
from .codegen import Program
from .dims import Shape
from .dtypes import Dtype
from .dtypes import Float32
from .lazy import LazyBuffer
from .lazy import LazyOp
from .ops import BinaryOp
from .ops import FusedOp
from .ops import MovementOp
from .ops import ReduceOp
from .ops import UnaryOp
from .raw import RawBuffer
from .shapetracker import ShapeTracker


@dc.dataclass(frozen=True)
class LocalBuffer:
    name: str
    dtype: Dtype = Float32
    realized: ta.Optional[RawBuffer] = None


@dc.dataclass(frozen=True)
class LinearAnalysis:
    obj: ta.Any

    shape: Shape = dc.field(coerce=check.of_isinstance(Shape))
    dtype: Dtype = dc.field(coerce=check.of_isinstance(Dtype))
    flops: int = dc.field(coerce=check.of_isinstance(int))


class LinearAnalyzer:
    def __init__(self) -> None:
        super().__init__()

        self._dct: ta.MutableMapping[ta.Any, LinearAnalysis] = col.IdentityKeyDict()

    def analyze(self, x: ta.Any) -> LinearAnalysis:
        try:
            return self._dct[x]
        except KeyError:
            ret = self._dct[x] = self._analyze(x)
            return ret

    @dispatch.method
    def _analyze(self, x: ta.Any) -> LinearAnalysis:
        raise TypeError(x)

    @_analyze.register
    def _analyze_buffer(self, buf: ops2.Buffer) -> LinearAnalysis:
        lb = check.isinstance(buf.obj, LazyBuffer)
        return LinearAnalysis(
            buf,
            lb.shape,
            lb.dtype,
            0,
        )

    @_analyze.register
    def _analyze_unary_op(self, op: ops2.UnaryOp) -> LinearAnalysis:
        raise NotImplementedError

    @_analyze.register
    def _analyze_cast(self, op: ops2.Cast) -> LinearAnalysis:
        raise TypeError(op)

    @_analyze.register
    def _analyze_binary_op(self, op: ops2.BinaryOp) -> LinearAnalysis:
        xa = self._analyze(op.x)
        ya = self._analyze(op.y)
        return LinearAnalysis(
            op,
            xa.shape,
            check.equal(xa.dtype, ya.dtype),
            xa.flops + ya.flops + xa.shape.prod,
        )


class KeyRenderer:
    def __init__(self, writer: ta.Callable[[str], ta.Any], bufs: ta.Sequence[LazyBuffer]) -> None:
        super().__init__()

        self._writer = check.callable(writer)
        self._bufs = coerce.seq_of(check.of_isinstance(LazyBuffer))(bufs)
        self._buf_idx_map: ta.Mapping[LazyBuffer, int] = col.IdentityKeyDict((buf, i) for i, buf in enumerate(self._bufs))  # noqa

    @dispatch.method
    def render(self, obj: ta.Any) -> None:
        raise TypeError(obj)

    @render.register
    def _render_buffer(self, buf: ops2.Buffer) -> None:
        self._writer(f'{type(buf).__name__}:{self._buf_idx_map[buf.obj]}')

    @render.register
    def _render_unary_op(self, op: ops2.UnaryOp) -> None:
        self._writer(f'({type(op).__name__} ')
        self.render(op.x)
        self._writer(')')

    @render.register
    def _render_binary_op(self, op: ops2.BinaryOp) -> None:
        self._writer(f'({type(op).__name__} ')
        self.render(op.x)
        self._writer(' ')
        self.render(op.y)
        self._writer(')')


def render_key(op: LazyOp, bufs: ta.Sequence[LazyBuffer]) -> str:
    buf = io.StringIO()
    KeyRenderer(buf.write, bufs).render(ops2.convert_from_lazy_op(op))
    return buf.getvalue()


def mnum(i: int) -> str:
    return str(i) if i >= 0 else f"m{-i}"


def get_grouped_float4_idxs(acc: ta.Sequence[uo.Token]) -> ta.Optional[ta.Sequence[int]]:
    idxs: ta.Optional[ta.List[int]] = []
    for i, a in enumerate(acc):
        if idxs is None:
            break
        if i in idxs:
            continue

        if a.dtype.item_size > 1 and a.offset == 0:
            idxs.append(i)
            friends: ta.List[int] = []
            for j, b in enumerate(acc):
                if len(friends) == 3:
                    break
                if j in idxs:
                    continue

                if a.name == b.name and b.dtype.item_size > 1 and b.offset == len(friends) + 1:
                    friends.append(j)

            if len(friends) == 3:
                idxs += friends
            else:
                idxs = None

        else:
            idxs = None

    return idxs


def get_grouped_maybe_float4(*values: ta.Sequence[uo.Token], grouping_allowed: bool = True):
    check.arg(col.all_equal([len(x) for x in values]))

    # these use accumulators, we can only fold if the acc is a float4
    idxs = get_grouped_float4_idxs(values[-1]) if grouping_allowed else None
    if idxs is not None:
        raise NotImplementedError

    return zip([[i] for i in range(len(values[0]))], zip(*values))


class LinearCodegenOp(CodegenOp):
    def __init__(self, op: LazyOp, output: LazyBuffer) -> None:
        super().__init__()

        # NOTE: if there's a RESHAPE, we skip it. the output shape is set from the reduce op or a latebuf
        self._op = check.isinstance(op.srcs[0], LazyOp) if op.op == MovementOp.RESHAPE else op

        self._bufs: ta.List[ta.Union[LazyBuffer, LocalBuffer]] = [output, *col.unique(op.buffers)]

        self._key = render_key(op, self._bufs)

    @property
    def op(self) -> LazyOp:
        return self._op

    @property
    def buffers(self) -> ta.Sequence[ta.Union[LazyBuffer, LazyBuffer]]:
        return self._bufs

    @cached.property
    def analysis(self) -> LinearAnalysis:
        return LinearAnalyzer().analyze(ops2.convert_from_lazy_op(self._op))  # noqa

    @property
    def key(self) -> str:
        return self._key

    @cached.property
    def reduce_op(self) -> ta.Optional[LazyOp]:
        # there's only allowed to be one reduce op
        reduce_ops = [x for x in self._op.ops if isinstance(x.op, ReduceOp)]
        return check.single(reduce_ops) if reduce_ops else None  # noqa

    @cached.property
    def early_buffers(self) -> ta.Sequence[LazyBuffer]:
        # get early bufs, before the one reduce op
        return col.unique(self.reduce_op.buffers) if self.reduce_op is not None else []  # noqa

    @cached.property
    def full_buffer_index(self) -> int:
        return self.buffers.index(self.early_buffers[0]) if len(self.early_buffers) > 0 else 0

    @property
    def full_shape(self) -> Shape:
        return self._sts[self.full_buffer_index].shape

    @property
    def first_reduce(self) -> int:
        return [
            x != y
            for x, y in zip(
                self._sts[0].shape[: self.shape_len - self._upcasted] + (0,),
                self.full_shape[: self.shape_len - self._upcasted] + (1,),
            )
        ].index(True)

    @property
    def shape_len(self) -> int:
        return len(self._sts[0].shape)

    _sts: ta.List[ShapeTracker]

    _group_for_reduce: ta.List[int]
    _upcasted: int
    _local_dims: int

    def prepare(self) -> None:
        # mem_est = sum(  # noqa
        #     x.dtype.item_size * (x.get_realized().size if x.is_realized is not None else x.shape.prod)
        #     for x in self._bufs
        # )

        # create new shapetrackers inside this kernel, we will permute them
        self._sts = [x.shape_tracker.copy() for x in self._bufs]
        for st in self._sts:
            st.simplify()

        # make the output buffer shape correct in here
        self._sts[0].reshape(self.analysis.shape)

        # move all reduce axes to the end
        reduce = list(enumerate(zip(self.full_shape, self._sts[0].shape)))
        permute = tuple(
            [i for i, (s, n) in reduce if s == n]
            + [i for i, (s, n) in reduce if s != n]
        )
        self.reshape_and_permute(None, permute)

        self._group_for_reduce = []
        self._upcasted = 0
        self._local_dims = 0

        # group simplifies
        self.simplify_ones()
        self.simplify_merge_adjacent()

    def build(self) -> Program:
        self.prepare()

        for axis in range(self.first_reduce - self._local_dims - 1, -1, -1):
            if self.full_shape[axis] == 1:
                continue

            local_size = math.prod(self.full_shape[self.first_reduce - self._local_dims: self.first_reduce])
            last_try = self._local_dims == 0 and axis == 0
            if (
                any(
                    self._sts[buf_index].views[-1].stride[axis] == 0
                    for buf_index in range(len(self._sts))
                ) or last_try
            ):
                for sz in [
                    x
                    for x in (([32] if last_try else []) + [16, 8, 4, 3])
                    if self.full_shape[axis] % x == 0 and local_size * x <= 128
                ]:
                    self.shift_to(axis, sz, insert_before=self.first_reduce - self._local_dims)
                    self._local_dims += 1
                    break

            if self._local_dims >= 3:
                break

        self.simplify_ones()

        self.linearize()

        raise NotImplementedError

    _uops: ta.List[uo.Uop]

    def _uop(self, uop: uo.Uop) -> ta.Optional:
        self._uops.append(uop)
        return uop.out

    def linearize(self) -> None:
        # uops
        self._uops = []

        if len(self._group_for_reduce):
            raise NotImplementedError

        fn_name = ('r_' if self.reduce_op is not None else 'E_') + '_'.join([str(x) for x in self.full_shape])

        loaded_buffers = {}
        acc = []

        # ssa
        _ssa: ta.DefaultDict[str, int] = collections.defaultdict(int)

        def ssa(name: str, ltype: Dtype = Float32) -> uo.Token:
            _ssa[name] += 1
            return uo.Token(f'{name}{_ssa[name]-1}', ltype)

        # global loop
        global_idxs = [
            sym.Var(f'gidx{i}', 0, self.full_shape[i] - 1)
            for i in range(0, self.first_reduce - self._local_dims)
        ]

        self._uop(uo.Loop(out=None, vin=[], idxs=global_idxs, s='global'))

        # local loop
        local_idxs = [
            sym.Var(f'lidx{i}', 0, self.full_shape[i] - 1)
            for i in range(
                self.first_reduce - self._local_dims,
                self.first_reduce + len(self._group_for_reduce),
            )
        ]
        self._uop(uo.Loop(out=None, vin=[], idxs=local_idxs, s='local'))
        gl_idxs = global_idxs + local_idxs

        # reduce op
        fake_reduce_idxs = []
        check.none(self.reduce_op)

        # load latebufs
        for i, b in enumerate(self._bufs):
            if b not in self.early_buffers and i != 0 and not isinstance(b, LocalBuffer):
                loaded_buffers[b] = self.global_load(i, global_idxs + local_idxs + fake_reduce_idxs)

        # run late AST
        val = self.process_one(self._op, acc, loaded_buffers, ssa)

        # store
        self.global_store(0, global_idxs + local_idxs + fake_reduce_idxs, val, ssa)

        if not self._group_for_reduce:
            # end the local loop
            self._uop(uo.EndLoop(out=None, vin=[], idxs=local_idxs, s='local'))

        self._uop(uo.EndLoop(out=None, vin=[], idxs=global_idxs, s='global'))

    def process_one(self, x, acc, loaded_buffers, ssa, do_reduce=False) -> ta.List[uo.Token]:
        if not isinstance(x, LazyOp):
            return loaded_buffers[x]
        x = ta.cast(LazyOp, x)

        if x.op in (UnaryOp.NOP, UnaryOp.CAST):
            return self.process_one(x.srcs[0], acc, loaded_buffers, ssa)  # cast isn't an ALU op

        values = [self.process_one(v, acc, loaded_buffers, ssa) for v in x.srcs]

        if isinstance(x.op, (ReduceOp, FusedOp)):
            raise NotImplementedError

        else:
            ret = [
                (
                    idx,
                    self._uop(uo.Alu(
                        out=ssa("alu"),
                        vin=list(val),
                        ty=type(ops2.convert_from_lazy_op(x)),
                    )),
                )
                for idx, val in get_grouped_maybe_float4(*values, grouping_allowed=False)
            ]

        ordered_ret: ta.List[ta.Optional[uo.Token]] = [None] * len(values[0])

        # scatter
        for i, j in ret:
            for o, k in enumerate(i):
                ordered_ret[k] = j

        check.state(all(isinstance(x, uo.Token) for x in ordered_ret))

        return ordered_ret

    def shape_offsets(self, i: int) -> ta.Sequence[ta.Sequence[int]]:
        if self._upcasted < 1:
            return [()]

        return itertools.product(*[
            list(range(s))
            for s in self._sts[i].shape[self.shape_len - self._upcasted:][::-1]
        ])

    class _Gl(ta.NamedTuple):
        local_type: Dtype
        uidx_list: ta.Sequence[int]
        idx: sym.Node
        valid: sym.Node

    def global_load(self, i: int, idxs: ta.Sequence[sym.Var], const=None) -> ta.Sequence[uo.Token]:
        load_offset: ta.Dict[ta.Sequence[int], LinearCodegenOp._Gl] = {}
        for uidxs in self.shape_offsets(i):
            gs = self._sts[i].gen_syms(idxs + [sym.Num(x) for x in uidxs[::-1]])
            load_offset[uidxs] = LinearCodegenOp._Gl(
                Float32,
                uidxs,
                gs.idx,
                gs.mask,
            )

        # do loads
        cache = {}
        loaded = {}
        for uidxs, (localtype, uidx_list, idx, valid) in load_offset.items():
            key = f'{localtype}{idx.expr}{valid.expr}'
            if key not in cache:
                if const is None:
                    cache[key] = self._uop(uo.Load(
                        out=uo.Token(f'val{mnum(i)}_{len(cache)}', localtype),
                        vin=[],
                        i=i,
                        idx=idx,
                        valid=valid,
                    ))
                else:
                    cache[key] = self._uop(uo.Const(
                        out=uo.Token(f'acc{mnum(i)}_{len(cache)}', localtype),
                        vin=[],
                        v=const,
                    ))

            loaded[uidxs] = cache[key]

        return [loaded[uidxs] for uidxs in self.shape_offsets(i)]

    def global_store(self, i, idxs: ta.Sequence[sym.Var], store: ta.Sequence[uo.Token], ssa) -> None:
        store_offset: ta.Dict[ta.Sequence[int], uo.Token] = dict(zip(self.shape_offsets(i), store))

        # do stores
        for uidxs, var in store_offset.items():
            gl = self._sts[i].gen_syms(idxs + [sym.Num(x) for x in uidxs[::-1]])
            self._uop(uo.Store(
                out=None,
                vin=[var],
                i=i,
                idx=gl.idx,
                valid=gl.mask,
            ))

    def reshape_and_permute(
            self,
            new_shape_fn: ta.Optional[ta.Callable[[Shape], Shape]] = None,
            axis: ta.Optional[ta.Sequence[int]] = None,
    ) -> None:
        for st in self._sts:
            if new_shape_fn is not None:
                st.reshape(Shape(new_shape_fn(st.shape)))
            if axis is not None:
                st.permute(tuple(axis))

    # drops the final dimension
    def upcast(self) -> None:
        check.arg(self.full_shape[-1] == 1)
        self._upcasted += 1

    def simplify_ones(self) -> None:
        # remove places where the shape is all ones
        # TODO: this should be factored in to multi shape stride
        if self.shape_len == 0:
            return

        all_ones = [
            all(st.shape[i] == 1 for st in self._sts)
            for i in range(self.shape_len)
        ]

        # keep at least 1 one
        if all(all_ones):
            all_ones[-1] = False

        self.reshape_and_permute(
            lambda shape: Shape(x for i, x in enumerate(shape) if not all_ones[i]),
            None,
        )

    def simplify_merge_adjacent(self):
        if self.shape_len == 0:
            return

        shapes = [x.shape for x in self._sts]
        strides = [x.views[-1].stride for x in self._sts]

        # merge dimensions if we can, multi get_shape_strides
        # TODO: does this always preserve the reduce dimension, NO
        # TODO: move this into shapetracker, with tests!
        rets = [[(shapes[j][0], strides[j][0])] for j in range(len(shapes))]
        for i in range(1, len(shapes[0])):
            can_merge = []
            for j in range(len(shapes)):
                # TODO: added the always mergeability of 1s, is this right? if so, add to shapetracker in the 1 case
                can_merge.append(
                    (strides[j][i] != 0 and rets[j][-1][1] == shapes[j][i] * strides[j][i]) or
                    (strides[j][i] == 0 and rets[j][-1][1] == 0)
                )

            # more can merge than this
            mergeable = all(can_merge) and i != self.first_reduce
            for j in range(len(shapes)):
                if mergeable:
                    rets[j][-1] = (rets[j][-1][0] * shapes[j][i], strides[j][i])
                else:
                    rets[j].append((shapes[j][i], strides[j][i]))

        # do the reshapes
        for i, x in enumerate(rets):
            self._sts[i].reshape(Shape(y[0] for y in x))

    # axis : the axis to pull from
    # amount : the amount to take
    # top : if you want to pull that amount from the top
    # insert_before : place to insert the new stuff
    def shift_to(
            self,
            axis: int,
            amount: int,
            top: bool = False,
            insert_before: ta.Optional[int] = None,
    ) -> None:
        if insert_before is None:
            insert_before = self.shape_len

        move_axis = axis if top else axis + 1
        if move_axis < insert_before:
            insert_before += 1

        self.reshape_and_permute(
            lambda x: Shape(
                list(x[0:axis]) +
                (
                    [amount, x[axis] // amount] if top else
                    [x[axis] // amount, amount] if x[axis] > 1 else
                    [1, 1]
                ) +
                list(x[axis + 1:])
            ),
            (
                [i for i in range(insert_before) if i != move_axis] +
                [move_axis] +
                [i for i in range(insert_before, self.shape_len + 1) if i != move_axis]
            ),
        )


class LinearCodegen(Codegen):
    def op(self, op: LazyOp, output: LazyBuffer) -> CodegenOp:
        return LinearCodegenOp(op, output)
