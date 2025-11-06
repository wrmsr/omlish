import contextlib
import ctypes as ct
import os
import sys
import typing as ta

from omlish import check
from omlish import lang

from . import tge


with lang.auto_proxy_import(globals()):
    import tinygrad as tg  # noqa

    from ommlds.backends.tinygrad.models import llama3  # noqa


##


def setup_autorelease_pool() -> ta.Callable[[], None]:
    libobjc = ct.CDLL('/usr/lib/libobjc.dylib')

    # void* objc_autoreleasePoolPush(void);
    libobjc.objc_autoreleasePoolPush.restype = ct.c_void_p
    libobjc.objc_autoreleasePoolPush.argtypes = []

    # void objc_autoreleasePoolPop(void* token);
    libobjc.objc_autoreleasePoolPop.restype = None
    libobjc.objc_autoreleasePoolPop.argtypes = [ct.c_void_p]

    pool = libobjc.objc_autoreleasePoolPush()
    return lambda: libobjc.objc_autoreleasePoolPop(pool)


#


def load_llm(args: ta.Sequence[str] | None = None) -> 'llama3.Llama3Llm':
    check.not_isinstance(args, str)

    tg.Tensor.no_grad = True

    from ommlds.backends.tinygrad.models.llama3.cli import _build_arg_parser  # noqa
    args = _build_arg_parser().parse_args(args)  # noqa

    # download_model is the default without a model passed in
    if args.download_model or not args.model:
        args.model = llama3.fetch_model(args.size)

    check.not_none(args.model)

    if args.seed is not None:
        tg.Tensor.manual_seed(args.seed)

    # print(f'seed = {Tensor._seed}')  # noqa

    return llama3.Llama3Llm(
        args.model,
        size=args.size,
        quantize=args.quantize,
        shard=args.shard,
        temperature=args.temperature,
    )


def unload_llm(llm: 'llama3.Llama3Llm') -> None:  # noqa
    pass


#


def _main(es: contextlib.ExitStack) -> None:
    print(f'{os.getpid()=}')
    input()

    @es.callback
    def say_done() -> None:
        print('all done!', file=sys.stderr)

    tge.get_or_make_executor().start()
    es.callback(tge.get_executor().stop)

    if sys.platform == 'darwin':
        tge.get_executor().add_shutdown_callback(tge.call(setup_autorelease_pool))

    llm = tge.call(load_llm, ['--size=1B'])
    tge.get_executor().add_shutdown_callback(lambda: unload_llm(llm))

    # run_api(llm)
    print(llm)


if __name__ == '__main__':
    lang.call_with_exit_stack(_main)
