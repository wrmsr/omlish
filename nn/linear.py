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

from . import ops
from . import symbolic as sym
from . import uops as uo
from .buffers import Buffer
from .codegen import Codegen
from .codegen import CodegenOp
from .codegen import Program
from .dims import Shape
from .dtypes import Dtype
from .dtypes import Float32
from .raw import RawBuffer
from .raw import RawConst
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
    def _analyze_buffer(self, buf: Buffer) -> LinearAnalysis:
        return LinearAnalysis(
            buf,
            buf.shape,
            buf.dtype,
            0,
        )

    @_analyze.register
    def _analyze_unary_op(self, op: ops.UnaryOp) -> LinearAnalysis:
        raise NotImplementedError

    @_analyze.register
    def _analyze_cast(self, op: ops.Cast) -> LinearAnalysis:
        raise TypeError(op)

    @_analyze.register
    def _analyze_binary_op(self, op: ops.BinaryOp) -> LinearAnalysis:
        xa = self._analyze(op.x)
        ya = self._analyze(op.y)
        return LinearAnalysis(
            op,
            xa.shape,
            check.equal(xa.dtype, ya.dtype),
            xa.flops + ya.flops + xa.shape.prod,
        )

    @_analyze.register
    def _analyze_reduce_op(self, op: ops.ReduceOp) -> LinearAnalysis:
        xa = self._analyze(op.x)
        return LinearAnalysis(
            op,
            op.new_shape,
            xa.dtype,
            xa.flops + xa.shape.prod,
        )


class KeyRenderer:
    def __init__(self, write: ta.Callable[[str], ta.Any], bufs: ta.Sequence[Buffer]) -> None:
        super().__init__()

        self._write = check.callable(write)
        self._bufs = coerce.seq_of(check.of_isinstance(Buffer))(bufs)
        self._buf_idx_map: ta.Mapping[Buffer, int] = col.IdentityKeyDict((buf, i) for i, buf in enumerate(self._bufs))  # noqa

    @dispatch.method
    def render(self, obj: ta.Any) -> None:
        raise TypeError(obj)

    @render.register
    def render_shape(self, sh: Shape) -> None:
        self._write(f'({", ".join(map(str, sh))})')

    @render.register
    def _render_buffer(self, buf: Buffer) -> None:
        self._write(f'{type(buf).__name__}:{self._buf_idx_map[buf]}')

    @render.register
    def _render_unary_op(self, op: ops.UnaryOp) -> None:
        self._write(f'({type(op).__name__} ')
        self.render(op.x)
        self._write(')')

    @render.register
    def _render_binary_op(self, op: ops.BinaryOp) -> None:
        self._write(f'({type(op).__name__} ')
        self.render(op.x)
        self._write(' ')
        self.render(op.y)
        self._write(')')

    @render.register
    def _render_reduce_op(self, op: ops.ReduceOp) -> None:
        self._write(f'({type(op).__name__} ')
        self.render(op.x)
        self._write(' ')
        self.render(op.new_shape)
        self._write(')')


def render_key(op: ops.Op, bufs: ta.Sequence[Buffer]) -> str:
    buf = io.StringIO()
    KeyRenderer(buf.write, bufs).render(op)
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
    def __init__(self, op: ops.Op, output: Buffer) -> None:
        super().__init__()

        # NOTE: if there's a RESHAPE, we skip it. the output shape is set from the reduce op or a latebuf
        self._op = check.isinstance(op.srcs[0], ops.Op) if isinstance(op, ops.Reshape) else op

        self._bufs: ta.List[ta.Union[Buffer, LocalBuffer]] = [output, *col.unique(op.buffers)]

        self._key = render_key(op, self._bufs)

    @property
    def op(self) -> ops.Op:
        return self._op

    @property
    def buffers(self) -> ta.Sequence[ta.Union[Buffer, LocalBuffer]]:
        return self._bufs

    @cached.property
    def analysis(self) -> LinearAnalysis:
        return LinearAnalyzer().analyze(self._op)  # noqa

    @property
    def key(self) -> str:
        return self._key

    @cached.property
    def reduce_op(self) -> ta.Optional[ops.Op]:
        # there's only allowed to be one reduce op
        reduce_ops = [x for x in self._op.ops if isinstance(x, ops.ReduceOp)]
        return check.single(reduce_ops) if reduce_ops else None  # noqa

    @cached.property
    def early_buffers(self) -> ta.Sequence[Buffer]:
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

    def _prepare_local_dims(self) -> None:
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

    def build(self) -> Program:
        self.prepare()

        self._prepare_local_dims()

        self.simplify_ones()

        self.linearize()

        from .opencl import OpenclDialect
        from .cstyle import CstyleRenderer

        rendered = CstyleRenderer(
            self._uops,
            self._bufs,
            OpenclDialect,
        ).render()

        from .opencl import OpenclProgram

        prg = OpenclProgram(
            self.fn_name,
            rendered.src.replace('KERNEL_NAME_PLACEHOLDER', self.fn_name),
            rendered.global_size[::-1],
            rendered.local_size[::-1],
        )

        return prg

    @cached.property
    def fn_name(self) -> str:
        return ('r_' if self.reduce_op is not None else 'E_') + '_'.join([str(x) for x in self.full_shape])

    _uops: ta.List[uo.Uop]

    def _uop(self, uop: uo.Uop) -> ta.Optional:
        self._uops.append(uop)
        return uop.out

    def linearize(self) -> None:
        # uops
        self._uops = []

        if len(self._group_for_reduce):
            raise NotImplementedError

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
        if self.reduce_op is not None:
            # define indexes
            reduce_idxs = [
                sym.Var(f'ridx{i}', 0, self.full_shape[i] - 1)
                for i in range(
                    self.first_reduce + len(self._group_for_reduce),
                    self.shape_len - self._upcasted,
                )
            ]
            fake_reduce_idxs = [x * 0 for x in reduce_idxs]

            # define accumulator
            acc = self.global_load(
                0,
                gl_idxs + fake_reduce_idxs,
                {ops.Sum: 0.0, ops.Max: -math.inf}[type(self.reduce_op)],
            )

            # reduce loop
            self._uop(uo.Loop(out=None, vin=[], idxs=reduce_idxs, s='reduce'))

            # load earlybufs
            loaded_buffers.update({
                b: self.global_load(i, gl_idxs + reduce_idxs)
                for i, b in enumerate(self._bufs)
                if b in self.early_buffers and i != 0
            })

            # run early AST (with reduce)
            self.process_one(
                self.reduce_op,
                [acc[off] for off in self.acc_offsets(self.full_buffer_index)],
                loaded_buffers,
                ssa,
                do_reduce=True,
            )

            # end the reduce loop
            self._uop(uo.EndLoop(out=None, vin=[], idxs=reduce_idxs, s='reduce'))

            # end the local loop, do the local reduce
            if self._group_for_reduce:
                fake_global_idxs = [x * 0 for x in global_idxs]
                self.global_store(-1, fake_global_idxs + local_idxs + fake_reduce_idxs, acc, ssa)  # store accumulators
                self._uop(uo.Barrier(out=None, vin=[]))
                self._uop(uo.EndLoop(out=None, vin=[], idxs=local_idxs, s='local'))

                # local indexs are over, 0 them out
                local_idxs = [x * 0 for x in local_idxs]

                # if any group_for_reduce items aren't reduces, upcast them here
                for j in self.upcast_in_mid_reduce_axes:
                    self.reshape_and_permute(
                        None, [i for i in range(self.shape_len) if i != j] + [j]
                    )
                    self.upcast()
                    self._group_for_reduce.pop()
                    local_idxs = local_idxs[:-1]

                # NOTE: this structure is the same as the reduce op above

                # define late accumulator
                acc = self.global_load(
                    -1,
                    fake_global_idxs + local_idxs + fake_reduce_idxs,
                    {ops.Sum: 0.0, ops.Max: -math.inf}[type(self.reduce_op)],
                )

                # late reduce loop
                end_local_idxs = [
                    sym.Var(
                        f'tidx{i}',
                        0,
                        self.full_shape[i] - 1 if i >= self.first_reduce else 0,
                    )
                    for i in range(0, self.first_reduce + len(self._group_for_reduce))
                ]
                self._uop(uo.Loop(out=None, vin=[], idxs=end_local_idxs, s='late_reduce'))

                # # load localbufs
                # loaded_buffers['LOCAL_BUFFER'] = self.global_load(-1, end_local_idxs + fake_reduce_idxs)

                # # there's no AST here (and there's no shape for the reduce LazyOp)
                # self.process_one(
                #     LazyOp(self.reduceop.op, ("LOCAL_BUFFER",)),
                #     [acc[off] for off in self.acc_offsets(-1)],
                #     loaded_buffers,
                #     ssa,
                #     do_reduce=True,
                # )

                # # end the late reduce loop
                # self._uop(uo.EndLoop(out=None, vin=[], idxs=end_local_idxs, s='late_reduce'))

                raise NotImplementedError

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
        if not isinstance(x, ops.Op):
            return loaded_buffers[x]
        x = ta.cast(ops.Op, x)

        if isinstance(x, (ops.Nop, ops.Cast)):
            return self.process_one(x.srcs[0], acc, loaded_buffers, ssa)  # cast isn't an ALU op

        if isinstance(x, ops.ReduceOp) and not do_reduce:
            return acc

        # MulAcc fusion. TODO: this is copied from Interpreted
        if (
                isinstance(x, ops.Sum) and
                isinstance(x.x, ops.Mul)
        ):
            x = ops.MulAcc(x.x.x, x.new_shape)

        if (
                isinstance(x, ops.Sum) and
                isinstance(x.x, ops.Cast) and
                isinstance(x.x.x, ops.Mul)
        ):
            x = ops.MulAcc(x.x.x.x, x.new_shape)

        srcs = list(x.srcs)
        if isinstance(x, (ops.Add, ops.Mul)):
            # Reorder sources to put constants first so get_grouped_maybe_float4 can fold the op
            srcs = sorted(
                srcs,
                key=lambda src: not (
                        isinstance(src, Buffer) and
                        src.is_realized and
                        isinstance(src.get_realized(), RawConst)
                ),
            )

        values = [self.process_one(v, acc, loaded_buffers, ssa) for v in srcs]

        if isinstance(x, (ops.ReduceOp, ops.FusedOp)):
            ot = {
                ops.Sum: ops.Add,
                ops.Max: ops.Maximum,
                ops.MulAcc: ops.MulAcc,
            }[type(x)]
            ret = [
                (
                    idx,
                    self._uop(uo.Alu(
                        out=val[-1],
                        vin=list(val),
                        ty=ot,
                    )),
                )
                for idx, val in get_grouped_maybe_float4(*values, acc, grouping_allowed=False)
            ]

        else:
            ret = [
                (
                    idx,
                    self._uop(uo.Alu(
                        out=ssa("alu"),
                        vin=list(val),
                        ty=type(x),
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

    @property
    def upcast_in_mid_reduce_axes(self) -> ta.Sequence[int]:
        return [
            j
            for j in range(self.first_reduce, self.first_reduce + len(self._group_for_reduce))
            if self.full_shape[j] == self._sts[0].shape[j]
        ]

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

    def upcasted_axis(self, i):
        return list(zip(
            self._sts[i].shape[self.shape_len - self._upcasted:],
            self._sts[i].real_strides()[self.shape_len - self._upcasted:],
            [
                x != y
                for x, y in zip(
                    self._sts[0].shape[self.shape_len - self._upcasted:],
                    self.full_shape[self.shape_len - self._upcasted:],
                )
            ],
        ))

    # TODO: is there a better way to write this?
    def acc_offsets(self, i):
        if self._upcasted == 0:
            return [0]
        upcasted_i = self.upcasted_axis(i)
        acc_strides = [
            x * (1 - upcasted_i[::-1][i][2])
            for i, x in enumerate(Shape(1 if r else s for s, _, r in upcasted_i[::-1]).base_stride())
        ]
        return [
            sum(t)
            for t in itertools.product(*[
                [y * acc_strides[i] for y in range(x[0])]
                for i, x in enumerate(upcasted_i[::-1])
            ])
        ]

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
    def op(self, op: ops.Op, output: Buffer) -> CodegenOp:
        return LinearCodegenOp(op, output)
