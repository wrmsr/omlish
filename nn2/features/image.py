import typing as ta

from omlish import dataclasses as dc

from .. import ops
from ..dtypes import ImageDType
from ..dtypes import dtypes
from ..execution import MemBuffer
from ..execution import get_lazyop_info
from ..helpers import DEBUG
from ..helpers import IMAGE
from ..helpers import getenv
from ..helpers import prod
from ..lazy import ScheduleItem
from ..lazy import get_single_root
from ..shape.symbolic import AndNode
from ..shape.symbolic import LtNode
from ..shape.symbolic import ModNode
from ..shape.symbolic import MulNode
from ..shape.symbolic import Node
from ..shape.symbolic import NumNode
from ..shape.symbolic import SumNode
from ..shape.symbolic import Variable


# *** image Tensor function replacements ***


def image_dot(self, w):
    # NOTE: we use a 1x1 conv2d to do the matmul. mxk @ kxn = (1,k,m,1).conv2d(n,k,1,1)
    n1, n2 = len(self.shape), len(w.shape)
    assert n1 != 0 and n2 != 0, f"both arguments to matmul need to be at least 1D, but they are {n1}D and {n2}D"
    assert (
        self.shape[-1] == w.shape[-min(n2, 2)]
    ), f"Input Tensor shapes {self.shape} and {w.shape} cannot be multiplied ({self.shape[-1]} != {w.shape[-min(n2, 2)]})"  # noqa
    bs, groups = prod(self.shape[0:-2]), prod(w.shape[0:-2])
    cin, cout = w.shape[-2], w.shape[-1]
    out_shape_t = self.shape[0:-2] + (cout, -1)
    if len(self.shape) > 1:
        order = tuple(range(len(self.shape) - 2)) + (len(self.shape) - 1, len(self.shape) - 2)
    else:
        order, out_shape_t = (0,), (cout,)
    worder = tuple(range(len(w.shape) - 2)) + (len(w.shape) - 1, len(w.shape) - 2)

    # NOTE: with NHWC we can remove the transposes
    # bs x groups*cin x H x W
    cx = self.permute(order=order).reshape(shape=(bs // groups, groups * cin, -1, 1))
    # groups*cout x cin x H, W
    cw = w.permute(order=worder).reshape(shape=(groups * cout, cin, 1, 1))
    return cx.conv2d(cw, groups=groups).reshape(shape=out_shape_t).permute(order=order)


def image_conv2d(self, weight, bias=None, groups=1, stride=1, dilation=1, padding=0):
    base_image_type = dtypes.imageh if getenv("FLOAT16", 0) else dtypes.imagef

    (bs, _, iy, ix), (cout, cin, H, W) = self.shape, weight.shape
    rcout = cout // groups
    x, w = self, weight.reshape(groups, rcout, cin, H, W)

    # hack for non multiples of 4 on cin
    if cin % 4 != 0 and not (cin == 1 and groups % 4 == 0):
        x = x.reshape(bs, groups, cin, iy, ix)  # do this always?
        added_input_channels = 4 - (cin % 4)
        w = w.pad(tuple((0, added_input_channels) if i == 2 else (0, 0) for i in range(len(w.shape))))
        x = x.pad(tuple((0, added_input_channels) if i == 2 else (0, 0) for i in range(len(x.shape))))
        cin = cin + added_input_channels
        x = x.reshape(bs, groups * cin, iy, ix)

    # hack for non multiples of 4 on rcout
    added_output_channels = 0
    if rcout % 4 != 0 and not (rcout == 1 and groups % 4 == 0):
        added_output_channels = 4 - (rcout % 4)
        rcout += added_output_channels
        cout = groups * rcout
        w = w.slice(tuple((0, rcout) if i == 1 else (0, s) for i, s in enumerate(w.shape)))

    # packed (note: flipping bs and iy would make the auto-padding work)
    x = x.permute(0, 2, 3, 1).reshape(bs * iy, ix * groups * cin // 4, 4)
    cin_last = iy == 1 and ix == 1
    if cin == 1:
        w = w.reshape(cout // 4, 4, H * W).permute(0, 2, 1)
    elif cin_last:
        w = w.\
            reshape(cout // 4, 4, cin // 4, 4, H, W).\
            permute(0, 4, 2, 5, 1, 3).\
            reshape(cout // 4, H * cin // 4 * W * 4, 4)
    else:
        w = w.\
            reshape(cout // 4, 4, cin // 4, 4, H, W).\
            permute(0, 4, 2, 5, 3, 1).\
            reshape(cout // 4, H * cin // 4 * W * 4, 4)

    # contiguous creates the image, and early realize static weights (TODO: test for the static weight)
    if IMAGE >= 2:
        x, w = x.cast(base_image_type(x.shape)), w.cast(base_image_type(w.shape))
    x, w = x.contiguous(), w.contiguous()
    if get_single_root(w.lazydata).realized:
        w.realize()

    # expand out
    rcin_hi, rcin_lo = cin // 4 if cin >= 4 else 1, 4 if cin >= 4 else 1
    cout_expand = [
        groups // 4 if cin == 1 else groups,
        4 if cin == 1 else 1,
        rcout // 4 if rcout >= 4 else 1,
        4 if rcout >= 4 else 1,
    ]
    x = x.reshape(bs, iy, ix, groups, rcin_hi, rcin_lo)
    if cin_last:
        w = w.reshape(cout // 4, H, rcin_hi, W, 4, rcin_lo)
    else:
        w = w.reshape(cout // 4, H, rcin_hi, W, rcin_lo, 4).permute(0, 1, 2, 3, 5, 4)

    # padding
    padding_ = [padding] * 4 if isinstance(padding, int) else (padding if len(padding) == 4 else [padding[1], padding[1], padding[0], padding[0]])  # noqa
    x = x.slice((
        None,
        (-padding_[2], x.shape[1] + padding_[3]),
        (-padding_[0], x.shape[2] + padding_[1]),
        None,
        None,
        None,
    ))

    # prepare input
    x = x.\
        permute(0, 3, 4, 5, 1, 2).\
        _pool((H, W), stride, dilation)  # -> (bs, groups, rcin_hi, rcin_lo, oy, ox, H, W)
    oy, ox = x.shape[4:6]
    x = x.\
        permute(0, 4, 5, 1, 2, 3, 6, 7).\
        reshape(bs, oy, ox, *cout_expand[0:2], 1, 1, rcin_hi, rcin_lo, H, W)
    x = x.expand(bs, oy, ox, *cout_expand, rcin_hi, rcin_lo, H, W)

    # prepare weights
    w = w.permute(0, 4, 2, 5, 1, 3)
    w = w.reshape((1, 1, 1, *cout_expand, rcin_hi, rcin_lo, H, W)).expand(x.shape)

    # the conv! (+ the bias)
    ret = (x * w).cast(dtypes.float32).sum((-4, -3, -2, -1))

    # reshape to image and cast back to image
    ret = ret.reshape(bs * oy, ox * cout // 4, 4)
    if IMAGE >= 2:
        ret = ret.cast(base_image_type(ret.shape))
    if IMAGE >= 3:
        ret = ret.contiguous()

    # undo hack for non multiples of 4 on C.rcout
    if added_output_channels != 0:
        ret = ret.reshape(bs, oy, ox, groups, rcout)[:, :, :, :, :-added_output_channels]
        rcout -= added_output_channels
        cout = groups * rcout

    # NCHW output
    ret = ret.reshape(bs, oy, ox, cout).permute(0, 3, 1, 2)
    return ret if bias is None else ret.add(bias.reshape(1, -1, 1, 1))


# *** schedules with images need to be fixed to be valid ***


def fix_schedule_for_images(schedule: list[ScheduleItem]):
    # this is the fundamental fix, find unwritable or unreadable images and convert them to normal float32 (TODO: should it be float16?)
    for si in schedule:
        if (
            isinstance(si.out.dtype, ImageDType)
            and (
                prod(si.out.shape) != prod(si.out.dtype.shape)
                or not any(si.out.shape[x] % 4 == 0 for x in si.out.st.unit_stride_axes())
            )
        ):
            si.out.dtype = dtypes.float32
        for b in si.ast.get_lazyops():
            if not isinstance(b, ops.Mem):
                continue
            if (
                isinstance(si.inputs[b.arg.idx - 1].dtype, ImageDType)
                and (
                    b.arg.st.real_offset() % 4 != 0
                    or not any(b.arg.st.shape[x] % 4 == 0 for x in b.arg.st.unit_stride_axes())
                )
            ):
                si.inputs[b.arg.idx - 1].dtype = dtypes.float32

    # now fix up the schedule to reflect the new dtypes
    fixed_schedule: list[ScheduleItem] = []
    for si in schedule:
        ast = si.ast
        # fix input dtypes to match what they actually are
        replacements = {}
        for b in si.ast.get_lazyops():
            if not isinstance(b, ops.Mem):
                continue
            if b.arg.dtype != si.inputs[b.arg.idx - 1].dtype:
                replacements[b] = ops.Mem((), MemBuffer(b.arg.idx, si.inputs[b.arg.idx - 1].dtype, b.arg.st))
        if replacements:
            ast = ast.map_buffers(replacements)

        # fix the ops to create the output dtype
        if not isinstance(ast, ops.LoadOp):
            info = get_lazyop_info(ast)
            if info.dtype != si.out.dtype:
                ast = ops.Cast((ast,), (si.out.dtype, False))

        # put this in the fixed schedule
        fixed_schedule.append(dc.replace(si, ast=ast))
    return fixed_schedule


# *** images have weird indexing requirements ***

def to_image_idx(base_shape: tuple[int, ...], idxy: Node, valid: Node) -> tuple[tuple[Node, Node], Node]:
    # This part is substituting variables by just looking at single var LtNodes in valid
    # Basically if var[0-5] < 3 -> var[0-2]
    if valid.min == 0:
        nodes: list = valid.nodes if isinstance(valid, AndNode) else [valid]
        var_dict = {var: [var.min, var.max] for var in valid.vars()}

        for nd in nodes:
            var_range = var_dict[nd.vars()[0]]
            if isinstance(nd.a, MulNode):
                if nd.a.b < 0:
                    var_range[0] = (nd.b // nd.a.b) + 1
                elif nd.a.b > 0:
                    var_range[1] = (nd.b // nd.a.b) - 1 if nd.b % nd.a.b == 0 else nd.b // nd.a.b
            elif isinstance(nd.a, Variable):
                var_range[1] = nd.b - 1
        # We do not allow NumNode because it is constant
        # TODO: Remove mx != mn
        sub_dict: dict[ta.Union[Variable, NumNode], Node] = {
            v: Variable(v.expr, mn, mx)
            for v, (mn, mx) in var_dict.items() if mx != mn
        }
        valid, idxy = valid.substitute(sub_dict), idxy.substitute(sub_dict)

    idx, idy = (idxy // 4) % base_shape[1], (idxy // (4 * base_shape[1]))
    idx_vars, idy_vars, val_vars = set(idx.vars()), set(idy.vars()), set(valid.vars())

    # Simplify ModNode if possibe # test_padded_conv_transpose2d, Needs much more thinking
    if valid.min == 0 and isinstance(idx, ModNode) and isinstance(idx.a, SumNode):
        nodes = valid.nodes if isinstance(valid, AndNode) else [valid]
        same_dict: dict[Node, list[tuple[int, Node]]] = {}
        idx_nodes = idx.a.flat_components

        for node in nodes:
            if not isinstance(node, LtNode) or not isinstance(node.a, SumNode):
                continue

            nd_flat, nd_vars = node.a.flat_components, node.vars()

            same = [x for x in idx_nodes if (x.a if isinstance(x, MulNode) else x) in nd_vars]

            if len(same) != len(nd_vars): continue

            first_b, second_b = nd_flat[0].b if isinstance(nd_flat[0], MulNode) else 1, same[0].b if isinstance(same[0], MulNode) else 1  # noqa

            k, same_sum = second_b // first_b, Variable.sum(same)

            if k * (node.a) == same_sum:
                same_dict[same_sum] = same_dict.get(same_sum, []) + [(k, node)]

        for key in same_dict.keys():
            same, mnn, mxn = key.flat_components, key.min, key.max  # type: ignore # Same is sumnode because node.a is SumNode
            for k, node in same_dict[key]:  # TODO: This part may need more thinking
                if k < 0:
                    mnn = (-k) * max((-node.b) + 1, min([-lal.b if isinstance(lal, MulNode) else 1 for lal in same]))
                else:
                    mxn = (node.b - 1) * k

            fake_var = Variable("valid_fake", mnn, mxn)
            total = (Variable.sum([x for x in idx_nodes if x not in same]) + fake_var) % idx.b
            idx = total.substitute({fake_var: key})
            # TODO: If idx has no ModNode we may can remove the valid node, but removing it needs careful thinking

    # Simplify SumNodes
    # This part just removes valid nodes if node is exactly same as idx or idy
    # idx = 3*a + b (+ 5), valid = 3*a + b < 10 # Valid will be removed as idx will go out of bounds
    # Check for var intersection, removing valid can affect other index
    if valid.min == 0 and not idx_vars.intersection(idy_vars):
        nds = valid.nodes if isinstance(valid, AndNode) else [valid]
        flats = [id.flat_components for id in (idx, idy) if isinstance(id, SumNode)]
        sym_sums = [Variable.sum([i for i in flat if not isinstance(i, NumNode)]) for flat in flats]
        ones = [
            node
            for sym_sum in sym_sums
            for node in nds
            if (node.a == sym_sum)
            or (-(node.a) == sym_sum)
        ]  # type: ignore # AndNode always consists of LtNode
        valid = Variable.ands([i for i in nds if i not in ones])

    # This is the slow part
    # This part is for brute forcing all possible values of idx, idy and valid
    # If valid is both 0 and 1 for the same (idx, idy) we can not delete the valid
    if getenv("VALIDHACKS", 1) and valid.min == 0 and not isinstance(idx, ModNode):
        variables = tuple(val_vars | idy_vars | idx_vars)
        val_infer, idx_infer, idy_infer = valid.expand(variables), idx.expand(variables), idy.expand(variables)
        val_dict: dict[int, set[tuple[int, int]]] = {0: set(), 1: set()}

        for v, x, y in zip(val_infer, idx_infer, idy_infer):
            val_dict[v.min].add((x.min, y.min))

        if not val_dict[1].intersection(val_dict[0]):
            valid = NumNode(1)

    if DEBUG >= 5:
        print("to_image_idx", base_shape, idx.min, idx.max, idy.min, idy.max, idx, idy)
    return (idx, idy), valid
