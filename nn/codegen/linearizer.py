from __future__ import annotations

import typing as ta
import itertools
import math
import functools
import collections

from . import uops as uo
from .. import ops as ops_
from ..codegen.kernel import Kernel
from ..codegen.kernel import LocalBuffer
from ..dtypes import DType
from ..dtypes import ImageDType
from ..dtypes import PtrDType
from ..dtypes import dtypes
from ..execution import ConstBuffer
from ..execution import MemBuffer
from ..features.image import to_image_idx
from ..helpers import DEBUG
from ..helpers import all_same
from ..helpers import colored
from ..helpers import prod
from ..lazy import vars_from_ast
from ..ops import LazyOp
from ..shape.shapetracker import ShapeTracker
from ..shape.symbolic import AndNode
from ..shape.symbolic import DivNode
from ..shape.symbolic import LtNode
from ..shape.symbolic import ModNode
from ..shape.symbolic import MulNode
from ..shape.symbolic import Node
from ..shape.symbolic import NumNode
from ..shape.symbolic import SumNode
from ..shape.symbolic import Variable
from ..shape.symbolic import sym_rename


VariableOrNum = ta.Union[Variable, NumNode, Node]


def get_grouped_dims(prefix, start_dim, local_dims, maxdim: int = 0):
    local_idxs = loop_local_idxs = [
        Variable(f"{prefix}{start_dim+i}", 0, s - 1)
        for i, s in enumerate(
            local_dims[0: maxdim - 1] + (prod(local_dims[maxdim - 1:]),)
            if len(local_dims) > maxdim
            else local_dims
        )
    ]
    if maxdim != 0 and len(local_dims) > maxdim:
        dd = local_idxs[maxdim - 1]
        nli = []
        for s in local_dims[maxdim - 1:][::-1]:
            nli.append(dd % s)
            dd //= s
        local_idxs = local_idxs[0: maxdim - 1] + nli[::-1]
    return local_idxs, [x for x in loop_local_idxs if not isinstance(x, NumNode)]


class Linearizer(Kernel):
    def uop_alu_idx(self, a: uo.UOp, b, ops, ctx: Linearizer, op, dtype=dtypes.int32):
        render_b: uo.UOp = ta.cast(
            uo.UOp, (NumNode(b) if not isinstance(b, Node) else b).render(ops, ctx)
        )
        return self.uop(uo.Alu, dtype, (a, render_b), op)

    # NOTE: the consts have to be be cached for deduping of downstream uops to work
    def const(self, b: ta.Union[int, float], dtype=dtypes.int32, insert_before=None) -> uo.UOp:
        return self.uop(uo.Const, dtype, tuple(), b, insert_before=insert_before)

    render_ops: ta.Any = {
        Variable: lambda self, ops, ctx: ctx.loop_uops[self.expr],
        NumNode: lambda self, ops, ctx: ctx.const(self.b),
        MulNode: lambda self, ops, ctx: ctx.uop_alu_idx(self.a.render(ops, ctx), self.b, ops, ctx, ops_.Mul),
        DivNode: lambda self, ops, ctx: ctx.uop_alu_idx(self.a.render(ops, ctx), self.b, ops, ctx, ops_.Div),
        ModNode: lambda self, ops, ctx: ctx.uop_alu_idx(self.a.render(ops, ctx), self.b, ops, ctx, ops_.Mod),
        LtNode: lambda self, ops, ctx: ctx.uop_alu_idx(self.a.render(ops, ctx), self.b, ops, ctx, ops_.CmpLt, dtype=dtypes.bool),  # noqa
        SumNode: lambda self, ops, ctx: functools.reduce(
            lambda a, b: ctx.uop_alu_idx(a, b, ops, ctx, ops_.Add),
            self.nodes[1:],
            self.nodes[0].render(ops, ctx),
        ),
        AndNode: lambda self, ops, ctx: functools.reduce(
            lambda a, b: ctx.uop_alu_idx(
                a, b, ops, ctx, ops_.Mul, dtype=dtypes.bool
            ),
            self.nodes[1:],
            self.nodes[0].render(ops, ctx),
        ),
    }

    def global_load(
            self,
            i: int,
            idxs: ta.Sequence[Node],
            acc=None,
            barrier: ta.Optional[uo.UOp] = None,
    ) -> list[uo.UOp]:
        buf = self.bufs[i]
        const = buf.val if isinstance(buf, ConstBuffer) else acc

        def rename_var(v: VariableOrNum, expr: str):
            return v if isinstance(v, NumNode) else Variable(expr, v.min, v.max)

        amt, dim = 1, None
        upcast_dim = self.get_upcast_dim(i)

        if len(upcast_dim) == 1 and len(float4_expand := idxs[upcast_dim[0]].expand()) in [4,2]:
            dim, amt = upcast_dim[0], len(float4_expand)

        expand_vars = tuple([rename_var(idx.expand_idx(), f"_uidx{j}") for j, idx in enumerate(idxs)])
        fake_idxs = [idx.substitute({idx.expand_idx(): ev}) for idx, ev in zip(idxs, expand_vars)]
        if dim is not None:
            g_idx, g_valid = self.sts[i].expr_idxs(fake_idxs[:dim] + [float4_expand[0]] + fake_idxs[dim+1:])
            if (g_idx // amt * amt).render() != g_idx.render():
                (g_idx, g_valid), amt, dim = self.sts[i].expr_idxs(fake_idxs), 1, None
        else:
            g_idx, g_valid = self.sts[i].expr_idxs(fake_idxs)
        localtype = dtypes.float32 if amt == 1 else dtypes._float4 if amt == 4 else dtypes._float2

        e_idxs, e_valids = g_idx.expand(expand_vars), g_valid.expand(expand_vars)
        ret = []
        invalid_value = 0 if dtypes.is_int(buf.dtype) else 0.0
        for idx, valid, rep_idx in zip(e_idxs, e_valids, Node.iter_idxs(expand_vars)):
            this_const, idx, valid = (
                (invalid_value, Variable.num(0), Variable.num(1))
                if valid.max == 0
                else (const, idx, valid)
            )

            key = (
                f"{acc}"
                f"{localtype}"
                f"{this_const if this_const is not None and acc is None else (buf.idx if isinstance(buf, MemBuffer) else ta.cast(LocalBuffer, buf).name)}"
                f"{idx.render()}"
                f"{valid.render()}"
            )

            if key not in self.load_cache:
                if acc is not None:
                    assert valid.min == 1
                    self.load_cache[key] = self.uop(
                        uo.DefineAcc, localtype, (), this_const, cachable=False
                    )

                elif this_const is not None:
                    self.load_cache[key] = self.const(this_const, localtype)
                    if valid.min == 0 and valid.max == 1:
                        valid_rendered = valid.render(self.render_ops, self)
                        self.load_cache[key] = self.uop(
                            uo.Alu,
                            localtype,
                            (
                                valid_rendered,
                                self.load_cache[key],
                                self.const(invalid_value, localtype),
                            ),
                            ops_.Where,
                        )

                else:
                    buf_uop = self.buf_uops[i]
                    assert buf_uop is not None, f"buffer {i} wasn't UOped"
                    if isinstance(buf.dtype, ImageDType):
                        idx, valid = to_image_idx(buf.dtype.shape, idx, valid)
                        rendered_idx = self.uop(
                            uo.Cast,
                            dtypes._int2,
                            (
                                idx[0].render(self.render_ops, self),
                                idx[1].render(self.render_ops, self),
                            ),
                        )
                    else:
                        rendered_idx = idx.render(self.render_ops, self)

                    if valid.min == 0:
                        valid_rendered = valid.render(self.render_ops, self)
                        self.load_cache[key] = self.uop(
                            uo.Load,
                            localtype,
                            (
                                buf_uop,
                                rendered_idx,
                                valid_rendered,
                                self.const(invalid_value, localtype),
                            ) + ((barrier,) if barrier else ()),
                        )

                    else:
                        self.load_cache[key] = self.uop(
                            uo.Load,
                            localtype,
                            (buf_uop, rendered_idx) + ((barrier,) if barrier else ()),
                        )

            ret.append(
                self.uop(
                    uo.Gep,
                    dtypes.float32,
                    (self.load_cache[key],),
                    rep_idx[dim],
                )
                if dim is not None else
                self.load_cache[key]
            )

        return ret

    def global_store(self, i: int, idxs: list[Node], store: list[uo.UOp]) -> list[uo.UOp]:
        buf = self.bufs[i]
        buf_uop = self.buf_uops[i]
        assert buf_uop is not None, f"buffer {i} wasn't UOped"

        expanded_nodes = [idx.expand() for idx in idxs]
        _idxs = [x[::-1] for x in itertools.product(*expanded_nodes[::-1])]
        store_offset = dict(zip(_idxs, store))

        # float4 grouping
        upcast_dim = self.get_upcast_dim(i)
        if len(upcast_dim) == 1 and len(expanded_nodes[upcast_dim[0]]) in [2, 4]:
            grouped_store_offset = collections.defaultdict(list)
            for k in store_offset:
                _idx = (
                    k[: upcast_dim[0]]
                    + (expanded_nodes[upcast_dim[0]][0],)
                    + k[upcast_dim[0] + 1:]
                )
                grouped_store_offset[_idx].append(store_offset[k])

            store_offset_new = {}
            for k, out_tokens in grouped_store_offset.items():
                amt = len(out_tokens)
                idx, valid = self.sts[i].expr_idxs(k)
                assert (
                    idx.render() == ((idx // amt) * amt).render()
                ), "float4 stores are always aligned"
                assert valid.min == 1, "stores are always valid"
                store_offset_new[k] = self.uop(
                    uo.Cast,
                    dtypes._float4 if amt == 4 else dtypes._float2,
                    tuple(out_tokens),
                )

            store_offset = store_offset_new

        stores = []
        for idx, var in store_offset.items():
            idx, valid = self.sts[i].expr_idxs(idx)
            if isinstance(buf.dtype, ImageDType):
                idx, valid = to_image_idx(buf.dtype.shape, idx, valid)
                rendered_idx = self.uop(
                    uo.Cast,
                    dtypes._int2,
                    tuple(x.render(self.render_ops, self) for x in idx),
                )
            else:
                rendered_idx = idx.render(self.render_ops, self)
            stores.append(self.uop(uo.Store, None, (buf_uop, rendered_idx, var)))
        return stores

    kernel_cnt: ta.Final[ta.DefaultDict[str, int]] = collections.defaultdict(int)

    def linearize(self):
        # no new opts and we already ran? skip relinearizing
        if self.applied_opts == self.applied_opts_cache:
            return self

        # save backups
        sts_backup = self.sts[:]
        gfr_backup = self.group_for_reduce[:]
        upc_backup = self.upcasted

        # global uop cache
        self.saved_exprs: dict[tuple, uo.UOp] = dict()

        # limit dims if we need to
        if self.opts.global_max and self.opts.local_max:
            self.limit_dims_to_max(self.opts.global_max, self.opts.local_max)

        # uops
        self.uops: list[uo.UOp] = []
        self.buf_uops: list[ta.Optional[uo.UOp]] = [None] * len(self.bufs)
        self.loop_uops: dict[str, uo.UOp] = {}

        # add global buffers
        for i, buf in enumerate(self.bufs):
            if isinstance(buf, MemBuffer):
                self.buf_uops[i] = self.uop(
                    uo.DefineGlobal,
                    PtrDType(buf.dtype)
                    if not isinstance(buf.dtype, ImageDType)
                    else buf.dtype,
                    (),
                    (f"data{buf.idx}", buf.dtype),
                )

        # add var vals
        for var in vars_from_ast(self.ast):
            assert var.expr is not None
            self.loop_uops[var.expr] = self.uop(
                uo.DefineGlobal,
                dtypes.int32,
                (),
                (var.expr, dtypes._arg_int32),
            )

            # define local buffers
            for lb in self.local_alias.values():
                self.buf_uops[self.bufs.index(lb)] = self.uop(
                    uo.DefineLocal,
                    PtrDType(dtypes.float32),
                    (),
                    (lb.name, self.sts[self.bufs.index(lb)].size()),
                )

        # add a local buffer for multistage reduce. # TODO: use local alias
        if self.group_for_reduce:
            # TODO: the strides of this can be controlled
            self.sts.append(
                ShapeTracker.from_shape(
                    tuple(
                        [1] * self.global_dims
                        + list(
                            self.full_shape[
                                self.global_dims:self.global_dims
                                + self.local_dims
                                + len(self.group_for_reduce)
                            ]
                        )
                        + [1]
                        * (
                            self.shape_len
                            - self.upcasted
                            - len(self.group_for_reduce)
                            - self.first_reduce
                        )
                        + [x[0] for x in self.upcasted_axis(0)]
                    )
                )
            )
            self.bufs.append(LocalBuffer("temp", self.sts[-1].size()))
            self.buf_uops.append(
                self.uop(
                    uo.DefineLocal,
                    PtrDType(dtypes.float32),
                    (),
                    ("temp", self.sts[-1].size()),
                )
            )

        # kernel name (before late upcast)
        self.function_name = ("r_" if self.reduceop else "E_") + "_".join(
            [str(x) if isinstance(x, int) else sym_rename(x) for x in self.full_shape]
        )
        self.display_name = ("r_" if self.reduceop else "E_") + colored(
            "_", "BLACK"
        ).join([colored(str(x), c) for x, c in zip(self.full_shape, self.colors())])

        # name the function something unique
        Linearizer.kernel_cnt[self.function_name] += 1
        suffix = (
            f"{'n'+str(Linearizer.kernel_cnt[self.function_name]-1)}"
            if Linearizer.kernel_cnt[self.function_name] > 1
            else ""
        )
        (
            self.function_name,
            self.display_name,
        ) = self.function_name + suffix, self.display_name + colored(suffix, "BLACK")

        # define indexes
        global_idxs, loop_global_idxs = get_grouped_dims(
            "gidx",
            0,
            self.full_shape[: self.global_dims],
            3 if self.opts.has_local else 0,
        )

        local_idxs, loop_local_idxs = get_grouped_dims(
            "lidx",
            self.global_dims,
            self.full_shape[
                self.global_dims:self.first_reduce + len(self.group_for_reduce)
            ],
            3 if self.opts.has_local else 0,
        )

        full_upcast_idxs = [
            Variable(None, 0, s - 1)
            for s in self.full_shape[self.shape_len - self.upcasted:]
        ]

        upcast_idxs = [
            Variable(None, 0, s - 1)
            for s in self.output_shape[self.shape_len - self.upcasted:]
        ]

        # global and local loops
        def render_loop(xx: list[Variable]) -> tuple[uo.UOp, ...]:
            new_loops = {
                x.expr: self.uop(
                    uo.Loop,
                    dtypes.int32,
                    (
                        self.const(x.min) if isinstance(x.min, int) else ta.cast(Node, x.min).render(self.render_ops, self),  # noqa
                        self.const(x.max + 1) if isinstance(x.max, int) else ta.cast(Node, x.max + 1).render(self.render_ops, self),  # noqa
                    ),
                    cachable=False,
                )
                for x in xx
                if not isinstance(x, NumNode)
                and x.expr is not None
            }
            self.loop_uops.update(new_loops)
            return tuple(new_loops.values())

        # set global/local size
        self.global_size: ta.Optional[list[int]] = None
        self.local_size: ta.Optional[list[int]] = None

        if self.dont_use_locals:
            self.global_size = [x.max + 1 for x in loop_global_idxs][::-1]
            self.loop_uops.update({
                x.expr: self.uop(
                    uo.Special,
                    dtypes.int32,
                    (),
                    (
                        len(loop_global_idxs) - 1 - i,
                        x.expr.replace("gidx", "idx"),
                        x.max + 1,
                    ),
                )
                for i, x in enumerate(loop_global_idxs)
            })

        elif self.opts.has_local:
            self.global_size = [x.max + 1 for x in loop_global_idxs][::-1]
            self.local_size = [x.max + 1 for x in loop_local_idxs][::-1]
            self.global_size += [1] * (3 - len(self.global_size))
            self.local_size += [1] * (3 - len(self.local_size))
            self.loop_uops.update(
                {
                    x.expr: self.uop(
                        uo.Special,
                        dtypes.int32,
                        (),
                        (len(loop_global_idxs) - 1 - i, x.expr, x.max + 1),
                    )
                    for i, x in enumerate(loop_global_idxs)
                }
            )
            self.loop_uops.update(
                {
                    x.expr: self.uop(
                        uo.Special,
                        dtypes.int32,
                        (),
                        (len(loop_local_idxs) - 1 - i, x.expr, x.max + 1),
                    )
                    for i, x in enumerate(loop_local_idxs)
                }
            )

        # parse AST
        loaded_buffers = {}
        acc = []
        self.load_cache: dict[str, uo.UOp] = {}

        fake_reduce_idxs: list[Variable] = []
        fake_reduce_idxs = []
        if self.reduceop is not None:
            # define indexes
            reduce_idxs = [
                Variable(f"ridx{i}", 0, self.full_shape[i] - 1)
                for i in range(
                    self.first_reduce + len(self.group_for_reduce),
                    self.shape_len - self.upcasted,
                )
            ]
            fake_reduce_idxs = [x * 0 for x in reduce_idxs]

            # define accumulator
            acc = self.global_load(
                0,
                global_idxs + local_idxs + fake_reduce_idxs + upcast_idxs,
                {ops_.Sum: 0.0, ops_.Max: -math.inf}[type(self.reduceop)],
            )

            if self.tensor_core:
                def calc_tc_idxs(local_size: int, aliases: list[list[int]]):
                    replace_idxs = []
                    for alias in aliases:
                        full_var, full_var_sz = Variable.num(0), 1
                        if alias[0] != 0:
                            for i in alias:
                                next_var = local_idxs[-i] if i > 0 else Variable(None, 0, local_size - 1)
                                full_var += next_var * full_var_sz
                                full_var_sz *= next_var.max + 1
                        replace_idxs.append(full_var)
                    return replace_idxs

                replace_acc_idxs = calc_tc_idxs(
                    self.tensor_core.thread_local_sizes[2],
                    self.tensor_core.thread_local_aliases[2],
                )
                for n in range(len(self.tensor_core.threads)):
                    # replace locals
                    local_idxs[self.local_dims - len(self.tensor_core.threads) + n] = replace_acc_idxs[n]
                for n in range(len(replace_acc_idxs) - len(self.tensor_core.threads)):
                    # replace upcasts
                    upcast_idxs[n] = replace_acc_idxs[len(self.tensor_core.threads) + n]

            # reduce loop
            loop_ctx = render_loop(reduce_idxs)

            # barrier for fast GEMM
            if self.tensor_core:
                self.uop(uo.Barrier, None, (), cachable=False)

            # compute local aliases
            locals_to_store = []
            for i in self.local_alias:
                localbuf_idx = self.bufs.index(self.local_alias[i])
                buf_idxs = [
                    idx * 0 if s == 0 else idx
                    for idx, s in zip(
                        global_idxs + local_idxs + reduce_idxs + full_upcast_idxs,
                        self.sts[i].real_strides()
                    )
                ]
                if self.tensor_core:
                    min_alias_idx = min(self.local_alias.keys())
                    replace_input_idxs = calc_tc_idxs(
                        self.tensor_core.thread_local_sizes[i - min_alias_idx],
                        self.tensor_core.thread_local_aliases[i - min_alias_idx],
                    )
                    for n in range(len(self.tensor_core.threads)):
                        # replace locals
                        buf_idxs[self.first_reduce - len(self.tensor_core.threads) + n] = replace_input_idxs[n]
                    for n in range(len(replace_input_idxs) - len(self.tensor_core.threads)):
                        # replace upcasts
                        buf_idxs[self.shape_len - self.upcasted + n] = replace_input_idxs[len(self.tensor_core.threads) + n]  # noqa
                if DEBUG >= 3:
                    print(f"{localbuf_idx} alias {i}: idxs=", buf_idxs)
                ll = self.global_load(i, buf_idxs)
                locals_to_store.append((localbuf_idx, buf_idxs, ll))

            # copy in any global buffers
            if self.tensor_core:
                wmma_sz = self.tensor_core.thread_local_sizes
                # calculate the number of local accumulator reduces and render WMMAs: this is bad... this needs to come
                # from someplace else
                nx = len(locals_to_store[0][2]) // wmma_sz[0]
                ny = len(locals_to_store[1][2]) // wmma_sz[1]
                nacc = len(acc) // wmma_sz[2]
                acc_reds = math.isqrt((nx * ny) // nacc)
                i, bx, by = 0, nx // acc_reds, ny // acc_reds
                for y in range(by):
                    for x in range(bx):
                        for j in range(acc_reds):
                            op1 = locals_to_store[0][2][(x + (j * bx)) * wmma_sz[0]:(x + (j * bx) + 1) * wmma_sz[0]]
                            op2 = locals_to_store[1][2][(y + (j * by)) * wmma_sz[1]:(y + (j * by) + 1) * wmma_sz[1]]
                            op3 = acc[i:i + wmma_sz[2]]
                            if self.opts.device != "HIP":
                                ops = tuple(op1+op2+op3)
                            else:
                                ops = (
                                    self.uop(uo.Cast, dtypes._half16, tuple(op1)),
                                    self.uop(uo.Cast, dtypes._half16, tuple(op2)),
                                    self.uop(uo.Cast, dtypes._float8, tuple(op3)),
                                )
                            ret = self.uop(
                                uo.Wmma,
                                dtypes._float2 if wmma_sz[2] == 2 else dtypes._float8,
                                ops,
                                (
                                    self.opts.device,
                                    self.tensor_core.dtype_in,
                                    self.tensor_core.dtype_out,
                                ),
                            )
                            for z in range(ta.cast(DType, ret.dtype).sz):
                                acc[i + z] = self.uop(
                                    uo.Phi,
                                    dtypes.float,
                                    (
                                        op3[z],
                                        self.uop(uo.Gep, dtypes.float, (ret,), z),
                                    ) + loop_ctx,
                                )
                        i += wmma_sz[2]

            else:
                if locals_to_store:
                    self.uop(uo.Barrier, None, (), cachable=False)
                    for i, idxs, ll in locals_to_store:
                        self.global_store(i, idxs, ll)
                    self.uop(uo.Barrier, None, (), cachable=False)

                # load earlybufs
                loaded_buffers.update(
                    {
                        b: self.global_load(
                            self.bufs.index(self.local_alias[i])
                            if i in self.local_alias
                            else i,
                            global_idxs + local_idxs + reduce_idxs + full_upcast_idxs,
                        )
                        for i, b in enumerate(self.bufs[1:], start=1)
                        if b in self.earlybufs
                    }
                )

                # run early AST (with reduce)
                self.ast_parse(
                    self.reduceop,
                    acc,
                    self.acc_offsets(self.full_buf_index),
                    loaded_buffers,
                    do_reduce=True,
                    loop_ctx=loop_ctx,
                )

            # end the reduce loop
            self.load_cache.clear()

            # end the local loop, do the local reduce
            if self.group_for_reduce:
                fake_global_idxs = [x * 0 for x in global_idxs]
                stores = self.global_store(-1, fake_global_idxs + local_idxs + fake_reduce_idxs + upcast_idxs, acc)  # store accumulators
                barrier = self.uop(uo.Barrier, None, tuple(stores), cachable=False)

                if self.opts.has_local:
                    fake_idxs = [Variable.num(0)] * len(self.sts[-1].shape)
                    fake_idxs[self.global_dims + self.local_dims:self.global_dims + len(local_idxs)] = local_idxs[self.local_dims:]
                    if_cond: uo.UOp = (self.sts[-1].expr_idxs(fake_idxs)[0] < 1).render(self.render_ops, self)
                    barrier = self.uop(uo.If, None, (if_cond, barrier), cachable=False)

                # create new late reduce local loops and replace local_idxs that have been used
                end_local_idxs = [
                    Variable(
                        f"tidx{i}",
                        0,
                        self.full_shape[i] - 1
                        if i >= self.first_reduce
                        and i not in self.upcast_in_mid_reduce_axes
                        else 0,
                    )
                    for i in range(0, self.first_reduce + len(self.group_for_reduce))
                ]
                local_idxs = (
                    local_idxs[: self.local_dims]
                    + end_local_idxs[self.global_dims + self.local_dims:]
                )

                # if any group_for_reduce items aren't reduces, upcast them here
                for j in self.upcast_in_mid_reduce_axes:
                    self.reshape_and_permute(
                        None, [i for i in range(self.shape_len) if i != j] + [j]
                    )
                    self.upcast()
                    self.group_for_reduce.pop()
                    local_idxs = local_idxs[:-1]
                    end_local_idxs = end_local_idxs[:-1]
                    # regenerate upcast_idxs
                    upcast_idxs = [
                        Variable(None, 0, s - 1)
                        for s in self.output_shape[self.shape_len - self.upcasted:]
                    ]

                # NOTE: this structure is the same as the reduce op above

                # define late accumulator
                acc = self.global_load(
                    -1,
                    fake_global_idxs + local_idxs + fake_reduce_idxs + upcast_idxs,
                    {ops_.Sum: 0.0, ops_.Max: -math.inf}[type(self.reduceop)],
                )

                # late reduce loop
                loop_ctx = render_loop(end_local_idxs)

                # load localbufs
                loaded_buffers[self.bufs[-1]] = self.global_load(
                    -1,
                    fake_global_idxs + local_idxs + fake_reduce_idxs + upcast_idxs,
                    barrier=barrier,
                )

                # there's no AST here (and there's no shape for the reduce LazyOp)
                self.ast_parse(
                    type(self.reduceop)((self.bufs[-1],)),
                    acc,
                    self.acc_offsets(-1),
                    loaded_buffers,
                    do_reduce=True,
                    loop_ctx=loop_ctx,
                )

                # end the late reduce loop
                self.load_cache.clear()

        # load latebufs
        loaded_buffers.update(
            {
                b: self.global_load(
                    i, global_idxs + local_idxs + fake_reduce_idxs + upcast_idxs
                )
                for i, b in enumerate(self.bufs)
                if b not in self.earlybufs and i != 0 and b.__class__ is not LocalBuffer
            }
        )

        # run late AST
        val = self.ast_parse(self.ast, acc, None, loaded_buffers)

        # store
        self.global_store(
            0, global_idxs + local_idxs + fake_reduce_idxs + upcast_idxs, val
        )

        # graph helper functions
        def get_recursive_parents(x: list[uo.UOp]) -> list[uo.UOp]:
            ret: set[uo.UOp] = set()
            this_round: set[uo.UOp] = set(x)
            while len(this_round):
                ret = ret.union(this_round)
                next_round: set[uo.UOp] = set()
                for r in this_round:
                    next_round = next_round.union(set(r.vin))
                this_round = next_round
            return list(ret)

        def get_recursive_children(x: uo.UOp) -> list[uo.UOp]:
            deps = set([x])
            ssize = 0
            while ssize != len(deps):
                ssize = len(deps)
                for u in self.uops:
                    if len(deps.intersection([x for x in u.vin if not isinstance(x, uo.Phi)])):
                        deps.add(u)
            return sorted(list(deps), key=self.uops.index)  # get the last one

        def replace_op(old: uo.UOp, new: uo.UOp):
            for u in self.uops:
                u.vin = tuple(new if x is old else x for x in u.vin)
            self.uops.remove(old)

        # uops optimization
        changed_something = True
        while changed_something:
            changed_something = False
            for u in self.uops:
                if isinstance(u, uo.Phi) and len(u.vin) == 3:
                    # if the parents of the PHI node don't have the LOOP in their parents, it can be folded
                    # TODO: ADD becomes a MUL, MAX can just become nothing
                    if (
                            all(not isinstance(x, uo.Loop) for x in get_recursive_parents(list(u.vin[0:2])))
                            and u.vin[1].arg == ops_.Add
                    ):
                        if DEBUG >= 4:
                            print(f"removing PHI node {u}")

                        del self.saved_exprs[(type(u), u.dtype, u.vin, u.arg)]

                        # NOTE: assuming u.vin[2].vin[1] and u.vin[2].vin[0] have the same dtype
                        loop_len = self.uop(
                            uo.Alu,
                            u.vin[2].vin[1].dtype,
                            (u.vin[2].vin[1], u.vin[2].vin[0]),
                            ops_.Sub,
                            insert_before=self.uops.index(u),
                        )

                        if loop_len.dtype != u.dtype:
                            loop_len = self.uop(
                                uo.Cast,
                                u.dtype,
                                (loop_len,),
                                insert_before=self.uops.index(u),
                            )

                        replace_op(
                            u,
                            self.uop(
                                uo.Alu,
                                u.dtype,
                                (u.vin[1], loop_len),
                                ops_.Mul,
                                insert_before=self.uops.index(u),
                            ),
                        )

                        changed_something = True

        # (recursively) remove childless uops
        # NOTE: DEFINE_GLOBAL should be removable, but we'd have to propagate that
        UOPS_W_SIDE_EFFECTS = {
            uo.Store,
            uo.Barrier,
            uo.DefineGlobal,
        }

        while 1:
            has_child: set[uo.UOp] = set()
            for ru in self.uops:
                for vu in ru.vin:
                    has_child.add(vu)

            nu: list[uo.UOp] = [
                x for x in self.uops if x in has_child or type(x) in UOPS_W_SIDE_EFFECTS
            ]

            if len(nu) == len(self.uops):
                break

            if DEBUG >= 4:
                print(f"reduced UOp count from {len(self.uops)} to {len(nu)}")

            self.uops = nu
            del nu

        # add UOps.END
        for u in self.uops:
            if isinstance(u, uo.Loop):
                # add END of loops after the last thing that (recursively) depends on them
                self.uop(
                    uo.End,
                    None,
                    (u,),
                    cachable=False,
                    insert_before=self.uops.index(get_recursive_children(u)[-1]) + 1,
                )

            elif isinstance(u, uo.If):
                # END any if statements at the end of the uops
                self.uop(uo.End, None, (u,), cachable=False)

        # maybe graph the uops
        if DEBUG >= 5:
            for u in self.uops:
                print(
                    f"{self.uops.index(u):4d} "
                    f"{str(type(u).__name__):20s}: "
                    f"{str(u.dtype) if u.dtype is not None else '':25s} "
                    f"{str([self.uops.index(x) for x in u.vin]):32s} "
                    f"{u.arg}"
                )

        # restore backups
        self.sts = sts_backup
        self.group_for_reduce = gfr_backup
        self.upcasted = upc_backup

        # set cache and return
        self.applied_opts_cache = self.applied_opts[:]
        return self

    def uop(
            self,
            uop: type[uo.UOp],
            dtype: ta.Optional[DType],
            vin: tuple[uo.UOp, ...],
            arg: ta.Any = None,
            cachable=True,
            insert_before=None,
            simplify=True,
    ) -> uo.UOp:
        key = (uop, dtype, vin, arg)
        if simplify:
            if uop == uo.Phi and len(vin) == 2:
                return vin[1]  # a phi without loops is a noop

            if uop == uo.Gep and isinstance(vin[0], uo.Const):
                return self.const(vin[0].arg, dtype, insert_before)

            if uop == uo.Cast and all(isinstance(x, uo.Const) for x in vin) and all_same([x.arg for x in vin]):
                return self.const(vin[0].arg, dtype, insert_before)

            if uop == uo.Alu:
                # rewrites. NOTE: the rewritten NEG op is still around...
                if arg == ops_.Add and isinstance(vin[1], uo.Alu) and vin[1].arg == ops_.Neg:
                    return self.uop(uo.Alu, dtype, (vin[0], vin[1].vin[0]), ops_.Sub, cachable=cachable, insert_before=insert_before)

                # constant folding
                if arg == ops_.Neg and isinstance(vin[0], uo.Const):
                    return self.const(-vin[0].arg, dtype, insert_before)

                # zero folding
                for x in [0, 1]:
                    if arg == ops_.Add and isinstance(vin[x], uo.Const) and vin[x].arg == 0.0:
                        return vin[1 - x]

                    if arg == ops_.Mul and isinstance(vin[x], uo.Const) and vin[x].arg == 1.0:
                        return vin[1 - x]

                    if arg == ops_.Mul and isinstance(vin[x], uo.Const) and vin[x].arg == 0.0:
                        return vin[x]

                if arg == ops_.Sub and isinstance(vin[1], uo.Const) and vin[1].arg == 0.0:
                    return vin[0]

                if arg == ops_.Div and isinstance(vin[1], uo.Const) and vin[1].arg == 1.0:
                    return vin[0]

        if cachable and key in self.saved_exprs:
            return self.saved_exprs[key]

        ret = uop(dtype, vin, arg)

        if insert_before is not None:
            self.uops.insert(insert_before, ret)
        else:
            self.uops.append(ret)

        if cachable:
            self.saved_exprs[key] = ret

        return ret

    def ast_parse(self, x, acc, offs, loaded_buffers, do_reduce=False, loop_ctx=()) -> list[uo.UOp]:
        if not isinstance(x, LazyOp):
            return loaded_buffers[x]  # for LOCAL_BUFFER

        if isinstance(x, ops_.BufferOp):
            return loaded_buffers[x.arg]

        if isinstance(x, ops_.Nop):
            return self.ast_parse(x.src[0], acc, offs, loaded_buffers)

        if isinstance(x, ops_.Cast):
            return [
                self.uop(uo.Cast, x.arg[0], (u,), x.arg) if not isinstance(x.arg[0], ImageDType) else u
                for u in self.ast_parse(x.src[0], acc, offs, loaded_buffers)
            ]

        if isinstance(x, ops_.ReduceOp) and not do_reduce:
            assert offs is None, "not available if we aren't doing reduce"
            return acc

        # MULACC fusion. TODO: this is copied from Interpreted
        if (
            isinstance(x, ops_.Sum)
            and isinstance(x.src[0], ops_.Mul)
        ):
            x = ops_.MulAcc(x.src[0].src, x.arg)

        if (
            isinstance(x, ops_.Sum)
            and isinstance(x.src[0], ops_.Cast)
            and isinstance(x.src[0].src[0], ops_.Mul)
        ):
            x = ops_.MulAcc(x.src[0].src[0].src, x.arg)

        values = [
            self.ast_parse(
                v,
                acc,
                offs,
                loaded_buffers,
                loop_ctx=loop_ctx,
            )
            for v in x.src
        ]

        ops = {
            ops_.Sum: ops_.Add,
            ops_.Max: ops_.Max2,
            ops_.MulAcc: ops_.MulAcc,
        }
        if type(x) in ops:
            ret = []
            input_acc = acc[:]
            for idx, val, off in zip([[i] for i in range(len(values[0]))], zip(*values), offs):
                acc[off] = self.uop(uo.Alu, dtypes.float32, val + (acc[off],), ops[type(x)])
                ret.append((idx, acc[off]))
            for off in range(len(acc)):
                if input_acc[off] != acc[off]:
                    acc[off] = self.uop(uo.Phi, dtypes.float32, (input_acc[off], acc[off]) + tuple(loop_ctx))

        else:
            ret = [
                (idx, self.uop(uo.Alu, dtypes.float32, val, type(x)))
                for idx, val in zip([[i] for i in range(len(values[0]))], zip(*values))
            ]

        ordered_ret: list[ta.Optional[uo.UOp]] = [None] * len(values[0])

        # scatter
        for i, j in ret:
            for k in i:
                ordered_ret[k] = j
        assert all(
            isinstance(x, uo.UOp) for x in ordered_ret
        ), "some tokens didn't get scattered?"

        return ta.cast(list[uo.UOp], ordered_ret)
