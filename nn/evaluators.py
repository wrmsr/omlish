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
            op: LazyOp,
            output: ta.Optional[LazyBuffer] = None,
            *,
            context: ta.Optional[EvalContext] = None,
    ) -> RawBuffer:
        raise NotImplementedError


class Interpreter(Evaluator):

    def __init__(
            self,
            make_buffer: ta.Callable[[ta.Any], RawBuffer],
            fns_by_op: ta.Mapping[Op, ta.Callable],
            from_lazy_buffer: ta.Callable[[LazyBuffer], ta.Any] = lambda x: x.get_realized(),
            to_underlying: ta.Callable[[RawBuffer], ta.Any] = lambda x: x._buf,  #  type: ignore  # noqa  # FIXME
    ) -> None:
        super().__init__()

        self._make_buffer = check.callable(make_buffer)
        self._fns_by_op = {check.isinstance(op, Op): check.callable(fn) for op, fn in fns_by_op.items()}
        self._from_lazy_buffer = check.callable(from_lazy_buffer)
        self._to_underlying = check.callable(to_underlying)

    def eval(
            self,
            op: LazyOp,
            output: ta.Optional[LazyBuffer] = None,
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
        if not created_context and op in context:
            return context[op]

        srcs = [
            self.eval(x, context=context)
            if isinstance(x, LazyOp) else
            self._from_lazy_buffer(x.as_buffer())
            for x in op.srcs
        ]

        ret = self._make_buffer(
            self._fns_by_op[op.op](
                *(
                        [self._to_underlying(x) for x in srcs] +
                        ([op.arg] if op.arg is not None else [])
                )
            )
        )

        if not created_context:
            context[op] = ret

        if output is not None and (ob := output.output_buffer) is not None:
            check.state(ob.size == ret.size and ob.dtype == ret.dtype)
            ob._buf = ret._buf  # type: ignore  # FIXME  # noqa
            return ob

        else:
            return ret


# class Compiler(Evaluator):
#
#     def __init__(
#             self,
#             make_buffer: ta.Callable[[ta.Any], RawBuffer],
#             codegen: Codegen,
#             runtime: Runtime,
#             synchronize: ta.Callable = lambda: None,
#     ) -> None:
#         super().__init__()
#
#         self._make_buffer = check.callable(make_buffer)
