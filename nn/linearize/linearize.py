import itertools
import math
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc

from . import uops as uo
from .. import ops
from .. import symbolic as sym
from ..buffers import Buffer
from ..codegen.codegen import Codegen
from ..codegen.codegen import CodegenOp
from ..codegen.codegen import Program
from ..dims import Shape
from ..dtypes import Dtype
from ..dtypes import Float32
from ..dtypes import Float4
from ..raw import RawBuffer
from ..raw import RawConst
from ..shapetracker import ShapeTracker
from .analysis import LinearAnalysis
from .analysis import LinearAnalyzer
from .keys import render_key


VarOrNum = ta.Union[sym.Var, sym.Num]


@dc.dataclass(frozen=True)
class LocalBuffer:
    name: str
    size: int
    dtype: Dtype = Float32
    realized: ta.Optional[RawBuffer] = None

    @property
    def is_realized(self) -> bool:
        return self.realized is not None

    def get_realized(self) -> RawBuffer:
        return check.not_none(self.realized)


def mnum(i: int) -> str:
    return str(i) if i >= 0 else f'm{-i}'


def get_grouped_float4_idxs(acc: ta.Sequence[uo.Token]) -> ta.Optional[ta.Sequence[int]]:
    idxs: ta.Optional[ta.List[int]] = []
    for i, a in enumerate(acc):
        if idxs is None:
            break
        if i in idxs:
            continue

        if a.dtype.sz > 1 and a.offset == 0:
            idxs.append(i)
            friends: ta.List[int] = []
            for j, b in enumerate(acc):
                if len(friends) == 3:
                    break
                if j in idxs:
                    continue

                if a.name == b.name and b.dtype.sz > 1 and b.offset == len(friends) + 1:
                    friends.append(j)

            if len(friends) == 3:
                idxs += friends
            else:
                idxs = None

        else:
            idxs = None

    return idxs


def to_float4(x: ta.Sequence[uo.Token]) -> ta.Optional[uo.Token]:
    if col.all_equal(x):
        return x[0]
    if (
            col.all_equal(y.name for y in x) and
            all(y.dtype == Float4 and y.offset == i for i, y in enumerate(x))
    ):
        return uo.Token(x[0].name, Float4)
    return None


def get_grouped_maybe_float4(*values: ta.Sequence[uo.Token], grouping_allowed: bool = True):
    check.arg(col.all_equal([len(x) for x in values]))

    # these use accumulators, we can only fold if the acc is a float4
    idxs = get_grouped_float4_idxs(values[-1]) if grouping_allowed else None
    if idxs is not None:
        new_idxs = []
        new_values = []
        for i in range(0, len(idxs), 4):
            nv = [to_float4([v[j] for j in idxs[i: i + 4]]) for v in values]
            if any([x is None for x in nv]):
                break
            new_idxs.append(idxs[i: i + 4])
            new_values.append(nv)
        if len(new_values) == len(idxs) // 4:
            return zip(new_idxs, new_values)

    return zip([[i] for i in range(len(values[0]))], zip(*values))


def expand_idxs(idxs: ta.Sequence[VarOrNum]) -> ta.Iterator[ta.Sequence[VarOrNum]]:
    for x in itertools.product(*[
        [idx] if not isinstance(idx, sym.Var) or idx.expr is not None else
        [sym.Num(j) for j in range(idx.min, idx.max + 1)]
        for idx in idxs[::-1]
    ]):
        yield x[::-1]


class FnNamer:
    def __init__(self) -> None:
        super().__init__()

        self._counts: ta.Dict[str, int] = {}
        self._names: ta.Dict[str, str] = {}

    def __call__(self, src: str, shape: Shape, has_reduce: bool) -> str:
        try:
            return self._names[src]
        except KeyError:
            name = ('r_' if has_reduce is not None else 'E_') + '_'.join([str(x) for x in shape])
            n = self._counts.get(name, 0)
            self._counts[name] = n + 1
            if n:
                name += f'n{n}'
            return name


class LinearCodegenOp(CodegenOp):
    def __init__(self, op: ops.Op, output: Buffer) -> None:
        super().__init__()

        # NOTE: if there's a RESHAPE, we skip it. the output shape is set from the reduce op or a latebuf
        self._op = check.isinstance(op.srcs[0], ops.Op) if isinstance(op, ops.Reshape) else op

        self._bufs: ta.List[ta.Union[Buffer, LocalBuffer]] = [output, *col.unique(op.buffers)]

        self._key = render_key(op, self._bufs)

    fn_namer: ta.Final[FnNamer] = FnNamer()

    def build(self) -> Program:
        # from . import dot
        # dot.open_dot(self._op)

        self.process()

        from ..backends.opencl import OpenclDialect

        self.hand_coded_optimizations()
        self.limit_global_dims(len(OpenclDialect.gid))

        self.linearize()

        from ..codegen.cstyle import CstyleRenderer

        rendered = CstyleRenderer(
            self._uops,
            self._bufs,
            OpenclDialect,
        ).render()

        fn_name = self.fn_namer(
            rendered.src,
            self.full_shape,
            self.reduce_op is not None,
        )

        from ..backends.opencl import OpenclProgram

        prg = OpenclProgram(
            fn_name,
            rendered.src.replace('KERNEL_NAME_PLACEHOLDER', fn_name),
            rendered.global_size,
            rendered.local_size,
        )

        return prg

    ##

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

    _sts: ta.List[ShapeTracker]

    _group_for_reduce: ta.List[int]
    _upcasted: int
    _local_dims: int

    supports_float4: bool = True
    supports_float4_alu: bool = True

    ##

    def process(self) -> None:
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

    def shape_offsets(self, i: int) -> ta.Sequence[ta.Sequence[int]]:
        if self._upcasted < 1:
            return [()]

        return itertools.product(*[
            list(range(s))
            for s in self._sts[i].shape[self.shape_len - self._upcasted:][::-1]
        ])

    def float4_axis(self, i: int) -> ta.Sequence[int]:
        return [
            x - (self.shape_len - self._upcasted)
            for x in self._sts[i].unit_stride_axes()
            if x >= self.shape_len - self._upcasted and self._sts[i].shape[x] % 4 == 0
        ]

    def upcasted_axis(self, i: int) -> ta.Sequence[ta.Tuple[Shape, ta.Sequence[ta.Optional[int]], bool]]:
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
    def acc_offsets(self, i: int) -> ta.Sequence[int]:
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

    def get_upcast_dim(self, i: int, amt: int = 4) -> ta.Sequence[int]:
        should_upcast = self.supports_float4 and self._bufs[i].dtype in (Float32,)
        return [
            x
            for x in self._sts[i].unit_stride_axes()
            if should_upcast
            and x >= self.shape_len - self._upcasted
            and self._sts[i].shape[x] == amt
        ]

    def global_load(self, i: int, idxs: ta.Sequence[VarOrNum], const=None) -> ta.Sequence[uo.Token]:
        upcast_dim = self.get_upcast_dim(i)
        cache: ta.Dict[str, uo.Token] = {}
        ret = []
        for _idx in expand_idxs(idxs):
            if len(upcast_dim) == 1:
                idx, valid = self._sts[i].gen_syms([
                    *_idx[: upcast_dim[0]],
                    sym.Num(0),
                    *_idx[upcast_dim[0] + 1 :]
                ])
                localtype = Float4
                # disallow unaligned access, fall back to float
                if idx.expr != ((idx // 4) * 4).expr:
                    idx, valid = self._sts[i].gen_syms(_idx)
                    localtype = Float32
            else:
                idx, valid = self._sts[i].gen_syms(_idx)
                localtype = Float32
            key = f'{localtype}{idx.expr}{valid.expr}'
            if key not in cache:
                cache[key] = (
                    self._uop(uo.Load(
                        out=uo.Token(f'val{mnum(i)}_{len(cache)}', localtype),
                        vin=[],
                        i=i,
                        idx=idx,
                        valid=valid,
                    )) if const is None else self._uop(uo.Const(
                        out=uo.Token(f'acc{mnum(i)}_{len(cache)}', localtype),
                        vin=[],
                        v=const,
                    ))
                )
            ret.append(
                uo.Token(cache[key].name, cache[key].dtype, _idx[upcast_dim[0]].b)
                if localtype == Float4 else cache[key]
            )
        return ret

    def global_store(self, i: int, idxs: ta.Sequence[VarOrNum], store: ta.Sequence[uo.Token], ssa) -> None:
        store_offset = dict(zip(expand_idxs(idxs), store))

        # float4 grouping
        upcast_dim = self.get_upcast_dim(i)
        if len(upcast_dim) == 1:
            grouped_store_offset = {}
            for k in store_offset:
                _idx = k[: upcast_dim[0]] + (sym.Num(0),) + k[upcast_dim[0] + 1:]
                try:
                    l = grouped_store_offset[_idx]
                except KeyError:
                    l = grouped_store_offset[_idx] = []
                l.append(store_offset[k])
            store_offset_new = {}
            for k, out_tokens in grouped_store_offset.items():
                idx, valid = self._sts[i].gen_syms(k)
                check.arg(idx.expr == ((idx // 4) * 4).expr)
                check.arg(valid.min == 1)
                if col.all_equal(x.name for x in out_tokens) and tuple(x.offset for x in out_tokens) == (0, 1, 2, 3):
                    store_offset_new[k] = uo.Token(out_tokens[0].name, Float4)
                else:
                    store_offset_new[k] = self._uop(uo.Cast(
                        out=ssa('alu', Float4),
                        vin=out_tokens,
                    ))
            store_offset = store_offset_new

        for idx, var in store_offset.items():
            xi, xv = self._sts[i].gen_syms(idx)
            self._uop(uo.Store(
                out=None,
                vin=[var],
                i=i,
                idx=xi,
                valid=xv,
            ))

    def linearize(self) -> None:
        # uops
        self._uops = []

        if len(self._group_for_reduce):
            # TODO: the strides of this can be controlled
            self._sts.append(
                ShapeTracker(
                    Shape(
                        [1] * self.first_reduce
                        + self._group_for_reduce
                        + [1]
                        * (
                                self.shape_len
                                - self._upcasted
                                - len(self._group_for_reduce)
                                - self.first_reduce
                        )
                        + [x[0] for x in self.upcasted_axis(0)]
                    )
                )
            )
            self._bufs.append(LocalBuffer('temp', self._sts[-1].size))
            self._uop(uo.DefineLocal(out=None, vin=[], s='temp', sz=self._sts[-1].size))

        loaded_buffers = {}
        acc = []

        # ssa
        _ssa: ta.Dict[str, int] = {}

        def ssa(name: str, ltype: Dtype = Float32) -> uo.Token:
            _ssa[name] = _ssa.get(name, 0) + 1
            return uo.Token(f'{name}{_ssa[name]-1}', ltype)

        # global loop
        global_idxs = [
            sym.var(f'gidx{i}', 0, self.full_shape[i] - 1)
            for i in range(0, self.first_reduce - self._local_dims)
        ]

        self._uop(uo.Loop(out=None, vin=[], idxs=global_idxs, s='global'))

        # local loop
        local_idxs = [
            sym.var(f'lidx{i}', 0, self.full_shape[i] - 1)
            for i in range(
                self.first_reduce - self._local_dims,
                self.first_reduce + len(self._group_for_reduce),
            )
        ]
        self._uop(uo.Loop(out=None, vin=[], idxs=local_idxs, s='local'))

        # upcast indexes
        full_upcast_idxs = [
            sym.var(None, 0, s - 1)
            for i, s in enumerate(self.full_shape[self.shape_len - self._upcasted:])
        ]
        upcast_idxs = [
            sym.var(None, 0, s - 1)
            for i, s in enumerate(self.output_shape[self.shape_len - self._upcasted:])
        ]

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
                global_idxs + local_idxs + fake_reduce_idxs + upcast_idxs,
                {ops.Sum: 0.0, ops.Max: -math.inf}[type(self.reduce_op)],
            )

            # reduce loop
            self._uop(uo.Loop(out=None, vin=[], idxs=reduce_idxs, s='reduce'))

            # load earlybufs
            loaded_buffers.update({
                b: self.global_load(i, global_idxs + local_idxs + reduce_idxs + full_upcast_idxs)
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
                    # regenerate upcast_idxs
                    upcast_idxs = [
                        sym.var(None, 0, s - 1)
                        for i, s in enumerate(self.output_shape[self.shape_len - self._upcasted:])
                    ]

                # NOTE: this structure is the same as the reduce op above

                # define late accumulator
                acc = self.global_load(
                    -1,
                    fake_global_idxs + local_idxs + fake_reduce_idxs + upcast_idxs,
                    {ops.Sum: 0.0, ops.Max: -math.inf}[type(self.reduce_op)],
                )

                # late reduce loop
                end_local_idxs = [
                    sym.var(
                        f'tidx{i}',
                        0,
                        self.full_shape[i] - 1 if i >= self.first_reduce else 0,
                    )
                    for i in range(0, self.first_reduce + len(self._group_for_reduce))
                ]
                self._uop(uo.Loop(out=None, vin=[], idxs=end_local_idxs, s='late_reduce'))

                # load localbufs
                loaded_buffers['LOCAL_BUFFER'] = self.global_load(-1, end_local_idxs + fake_reduce_idxs + upcast_idxs)

                # # there's no AST here (and there's no shape for the reduce LazyOp)
                # self.process_one(
                #     LazyOp(self.reduceop.op, ('LOCAL_BUFFER',)),
                #     [acc[off] for off in self.acc_offsets(-1)],
                #     loaded_buffers,
                #     ssa,
                #     do_reduce=True,
                # )

                ####

                ot = {
                    ops.Sum: ops.Add,
                    ops.Max: ops.Maximum,
                    ops.MulAcc: ops.MulAcc,
                }[type(self.reduce_op)]
                [
                    (
                        idx,
                        self._uop(uo.Alu(
                            out=val[-1],
                            vin=list(val),
                            ty=ot,
                        )),
                    )
                    for idx, val in
                    get_grouped_maybe_float4(loaded_buffers['LOCAL_BUFFER'], acc, grouping_allowed=self.supports_float4_alu)
                ]

                ####

                # end the late reduce loop
                self._uop(uo.EndLoop(out=None, vin=[], idxs=end_local_idxs, s='late_reduce'))

        # load latebufs
        for i, b in enumerate(self._bufs):
            if b not in self.early_buffers and i != 0 and not isinstance(b, LocalBuffer):
                loaded_buffers[b] = self.global_load(i, global_idxs + local_idxs + fake_reduce_idxs + upcast_idxs)

        # run late AST
        val = self.process_one(self._op, acc, loaded_buffers, ssa)

        # store
        self.global_store(0, global_idxs + local_idxs + fake_reduce_idxs + upcast_idxs, val, ssa)

        if not self._group_for_reduce:
            # end the global+local loop
            self._uop(uo.EndLoop(out=None, vin=[], idxs=global_idxs + local_idxs, s='global+local'))
        else:
            # end the global loop
            self._uop(uo.EndLoop(out=None, vin=[], idxs=global_idxs, s='global'))

    _uops: ta.List[uo.Uop]

    def _uop(self, uop: uo.Uop) -> ta.Optional:
        self._uops.append(uop)
        return uop.out

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

        otd = {
            ops.Sum: ops.Add,
            ops.Max: ops.Maximum,
            ops.MulAcc: ops.MulAcc,
        }
        if type(x) in otd:
            ot = otd[type(x)]
            ret = [
                (
                    idx,
                    self._uop(uo.Alu(
                        out=val[-1],
                        vin=list(val),
                        ty=ot,
                    )),
                )
                for idx, val in get_grouped_maybe_float4(
                    *values,
                    acc,
                    grouping_allowed=self.supports_float4_alu,
                )
            ]

        else:
            ret = [
                (
                    idx,
                    self._uop(uo.Alu(
                        out=ssa('alu', Float4) if any(x.dtype == Float4 and x.offset is None for x in val) else ssa('alu'),  # noqa
                        vin=list(val),
                        ty=type(x),
                    )),
                )
                for idx, val in get_grouped_maybe_float4(
                    *values,
                    grouping_allowed=self.supports_float4_alu and not isinstance(x, (ops.CmpEq, ops.Where)),
                )
            ]

        ordered_ret: ta.List[ta.Optional[uo.Token]] = [None] * len(values[0])

        # scatter
        for i, j in ret:
            for o, k in enumerate(i):
                ordered_ret[k] = uo.Token(j.name, j.dtype, o) if j.dtype == Float4 else j

        check.state(all(isinstance(x, uo.Token) for x in ordered_ret))

        return ordered_ret

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
    def output_shape(self) -> Shape:
        return self._sts[0].shape

    @property
    def full_shape(self) -> Shape:
        return self._sts[self.full_buffer_index].shape

    @property
    def full_unupcasted_shape(self) -> Shape:
        return Shape(self.full_shape[: self.shape_len - self._upcasted])

    @property
    def shape_len(self) -> int:
        return len(self._sts[0].shape)

    @property
    def upcast_in_mid_reduce_axes(self) -> ta.Sequence[int]:
        return [
            j
            for j in range(self.first_reduce, self.first_reduce + len(self._group_for_reduce))
            if self.full_shape[j] == self._sts[0].shape[j]
        ]

    # ~~colors lol~~

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
        check.arg(self.full_shape[-1] != 1)
        self._upcasted += 1

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
                    ([amount, x[axis] // amount] if top else
                     [x[axis] // amount, amount]) if x[axis] > 1 else [1, 1]
                ) +
                list(x[axis + 1:])
            ),
            (
                    [i for i in range(insert_before) if i != move_axis] +
                    [move_axis] +
                    [i for i in range(insert_before, self.shape_len + 1) if i != move_axis]
            ),
        )

    ##

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
        strides = [x.stride for x in self._sts]

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

    ##

    class _Gl(ta.NamedTuple):
        local_type: Dtype
        uidx_list: ta.Sequence[int]
        idx: sym.Node
        valid: sym.Node

    def required_optimizations(self, early_only=False):
        for buf_index, buf in enumerate(self._bufs):
            unit_stride_axes_mul_4 = [
                i
                for i in self._sts[buf_index].unit_stride_axes()
                if self._sts[buf_index].shape[i] % 4 == 0
            ]
            # if (not early_only or buf in self.earlybufs) and self.bufs[buf_index].dtype.__class__ is ImageDType:
            #     assert (
            #             len(unit_stride_axes_mul_4) >= 1
            #     ), f"needs a unit stride axis in {self.bufs[buf_index]}"
            #     if (
            #             all(
            #                 x < (self.shape_len - self.upcasted)
            #                 for x in unit_stride_axes_mul_4
            #             )
            #             and unit_stride_axes_mul_4[0] not in self.upcast_in_mid_reduce_axes
            #     ):
            #         self.shift_to(unit_stride_axes_mul_4[0], 4)
            #         self.upcast()

    def limit_global_dims(self, limit: int) -> None:
        # sometimes, there's more dimensions than len(self.lang.gid).
        # compact all the dimensions into the first
        # NOTE: this might make multiview shapetrackers
        if limit and (self.first_reduce - self._local_dims) > limit:
            num_to_merge = ((self.first_reduce - self._local_dims) - limit) + 1
            self.reshape_and_permute(
                lambda x: (math.prod(x[0:num_to_merge]),) + x[num_to_merge:], None
            )

    def hand_coded_optimizations(self) -> None:
        # if there's images in the earlybufs, we have to make an axis the 4 loading one
        self.required_optimizations(early_only=True)

        # simplify
        self.simplify_ones()

        # are we grouping? (requires local shape support)
        if (
                not self.float4_axis(0) and
                self.first_reduce <= 2 and
                self.first_reduce + 1 <= self.shape_len and
                math.prod(self._sts[0].shape[: self.first_reduce]) <= 2048
        ):
            # TODO: use 1024 if it's allowed in a smarter way
            for sz in (
                    ([256, 16]) if math.prod(self._sts[0].shape[: self.first_reduce]) <= 32 else [16]
            ):
                if all([
                    st.shape[self.first_reduce] % sz == 0 or st.shape[self.first_reduce] == 1
                    for st in self._sts
                ]):
                    self.shift_to(
                        self.first_reduce,
                        sz,
                        top=True,
                        insert_before=self.first_reduce + len(self._group_for_reduce),
                    )
                    self._group_for_reduce.append(sz)
                    break

        # now do everything required
        self.required_optimizations()

        # simplify (sets first_reduce)
        self.simplify_ones()

        # no more opt if we are grouping
        if self._group_for_reduce:
            return

        # **** below this line need to be optional and benchmarked ****

        # potentially do more upcasts of non reduce axes based on a heuristic
        upcasted_axis = set()
        while math.prod(self._sts[0].shape[: self.first_reduce]) >= 1024:
            xb_choices = []
            # consider all the non reduce axes, and a 3 or 4 reduce
            for axis, upcast_amount in itertools.product(range(self.first_reduce), [3, 4]):
                # if we haven't upcasted it, it mods, and some buffer has stride 0 on axis while having no stride 0 in
                # the upcasted axis already
                if (
                        axis not in upcasted_axis and
                        self.full_shape[axis] % upcast_amount == 0 and
                        any(
                            self._sts[buf_index].stride[axis] == 0 and
                            not any(x[1] == 0 for x in self.upcasted_axis(buf_index))
                            for buf_index in range(len(self._sts))
                        )
                ):
                    xb_choices.append(
                        (
                            sum(st.stride[axis] > 0 for st in self._sts),
                            sum(st.stride[axis] for st in self._sts),
                            axis,
                            upcast_amount,
                        )
                    )
            if len(xb_choices):
                xb_choices = sorted(xb_choices)
                self.shift_to(xb_choices[0][2], amount=xb_choices[0][3])
                self.upcast()
                self.simplify_ones()
                upcasted_axis.add(xb_choices[0][2])
            else:
                break

        # if last dim is small(ish) and it's a reduce dim, upcast the reduce (loop unrolling). no simplify needed it's
        # just an upcast. NOTE: careful, this has broken VALIDHACKS
        if self.first_reduce < (self.shape_len - self._upcasted) and (
                len(list(self.shape_offsets(self.full_buffer_index))) <= 4
                or not any(r for _, _, r in self.upcasted_axis(self.full_buffer_index))
        ):
            if (s := self.full_unupcasted_shape[-1]) <= 32:
                self.upcast()
                # if it's small, upcast a second reduce dimension too
                if (
                        self.first_reduce < (self.shape_len - self._upcasted) and
                        s <= 3 and
                        self.full_unupcasted_shape[-1] <= 3
                ):
                    self.upcast()
            else:
                for splits in [4]:
                    if self.full_unupcasted_shape[-1] % splits == 0:
                        self.shift_to(
                            len(self.full_unupcasted_shape) - 1,
                            splits,
                            insert_before=len(self.full_unupcasted_shape),
                        )
                        self.upcast()
                        break

        # if nothing at all is upcasted and it's easy to, do an upcast
        # TODO: this is breaking the tests
        for splits in [4]:
            if (
                    self._upcasted == 0 and
                    len(self.full_unupcasted_shape) > 0 and
                    self.full_unupcasted_shape[-1] % splits == 0
            ):
                self.shift_to(
                    len(self.full_unupcasted_shape) - 1,
                    splits,
                    insert_before=len(self.full_unupcasted_shape),
                )
                self.upcast()

        # **** local groups ****

        for axis in range(self.first_reduce - self._local_dims - 1, -1, -1):
            if self.full_shape[axis] == 1:
                continue

            local_size = math.prod(self.full_shape[self.first_reduce - self._local_dims: self.first_reduce])
            last_try = self._local_dims == 0 and axis == 0
            if (
                    any(
                        self._sts[buf_index].stride[axis] == 0
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


class LinearCodegen(Codegen):
    def op(self, op: ops.Op, output: Buffer) -> CodegenOp:
        return LinearCodegenOp(op, output)
