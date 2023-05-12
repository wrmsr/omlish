import abc
import typing as ta

from omlish import check
from omlish import lang

from .lazy import LazyBuffer
from .lazy import LazyOp
from .ops import Op
from .raw import RawBuffer


EvalContext = ta.MutableMapping[LazyOp, RawBuffer]


class Evaluator(lang.Abstract):
    @abc.abstractmethod
    def eval(
            self,
            expr: LazyOp,
            output: ta.Optional[LazyBuffer],
            *,
            context: ta.Optional[EvalContext] = None,
    ) -> RawBuffer:
        raise NotImplementedError


class Interpreter(Evaluator):

    def __init__(
            self,
            buffer_cls: ta.Type[RawBuffer],
            fns_by_op: ta.Mapping[Op, ta.Callable],
            from_lazy_buffer: ta.Callable[[LazyBuffer], ta.Any] = lambda x: x.get_realized(),
            to_underlying: ta.Callable[[RawBuffer], ta.Any] = lambda x: x._buf,  # FIXME  # noqa
    ) -> None:
        super().__init__()

        self._buffer_cls = check.issubclass(buffer_cls, RawBuffer)
        self._fns_by_op = {check.isinstance(op, Op): check.callable(fn) for op, fn in fns_by_op.items()}
        self._from_lazy_buffer = check.callable(from_lazy_buffer)
        self._to_underlying = check.callable(to_underlying)

    def eval(
            self,
            expr: LazyOp,
            output: ta.Optional[LazyBuffer],
            *,
            context: ta.Optional[EvalContext] = None,
    ) -> RawBuffer:
        # if (
        #         FusedOps.MULACC in self.fxn_for_op and
        #         ast.op == ReduceOps.SUM and
        #         isinstance(ast.src[0], LazyOp) and
        #         ast.src[0].op == BinaryOps.MUL
        # ):
        #     ast = LazyOp(FusedOps.MULACC, ast.src[0].src, ast.arg)

        created_context = context is None
        if context is None:
            context = {}
        if not created_context and expr in context:
            return context[expr]

        srcs = [
            self.eval(x, context=context) if isinstance(x, LazyOp) else self._from_lazy_buffer(x)
            for x in expr.srcs
        ]

        ret = self._buffer_cls(
            self._fns_by_op[expr.op](
                *([self._to_underlying(x) for x in srcs] + ([expr.arg] if expr.arg is not None else []))))

        if not created_context:
            context[expr] = ret

        if output is not None:  # and output.output_buffer is not None:
            # assert output.output_buffer.size == ret.size, output.output_buffer.dtype == ret.dtype
            # output.output_buffer._buf = ret._buf
            # return output.output_buffer
            raise NotImplementedError

        else:
            return ret
