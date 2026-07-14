import argparse
import pathlib

from tinygrad import Tensor

from omlish import check
from omlish import lang

from .fetch import fetch_model
from .llm import Llama3Llm
from .llm import run_llm


##


def _run(llm: Llama3Llm, toks: list[int], start_pos: int = 0) -> int:
    for s in (gc := lang.capture_generator(run_llm(llm, toks, start_pos))):
        print(s, end='', flush=True)
    print(flush=True)
    return gc.value.start_pos


def run_prompt(llm: Llama3Llm, prompt: str) -> None:
    _run(llm,[
        llm.tokenizer.bos_id,
        *llm.encode_message('system', 'You are an helpful assistant.'),
        *llm.encode_message('user', prompt),
        *llm.encode_role('assistant'),
    ])


def run_repl(llm: Llama3Llm) -> None:
    start_pos = llm.prefill([
        llm.tokenizer.bos_id,
        *llm.encode_message('system', 'You are an helpful assistant.'),
    ])

    while True:
        start_pos = _run(llm, [
            *llm.encode_message('user', input('Q: ')),
            *llm.encode_role('assistant'),
        ], start_pos)


##


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--download_model',
        action='store_true',
        help='Download a model',
    )
    parser.add_argument(
        '--model',
        type=pathlib.Path,
        help='Model path',
    )
    parser.add_argument(
        '--size',
        choices=['1B', '8B', '70B', '405B'],
        default='1B',
        help='Model size',
    )
    parser.add_argument(
        '--shard',
        type=int,
        default=1,
        help='Shard the model across multiple devices',
    )
    parser.add_argument(
        '--quantize',
        choices=['int8', 'nf4', 'float16'],
        help='Quantization method',
    )
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed',
    )
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.85,
        help='Temperature',
    )
    parser.add_argument(
        '--prompt',
    )
    return parser


def _main() -> None:
    args = _build_arg_parser().parse_args()

    # download_model is the default without a model passed in
    if args.download_model or not args.model:
        args.model = fetch_model(args.size)

    check.not_none(args.model)

    if args.seed is not None:
        Tensor.manual_seed(args.seed)

    print(f'seed = {Tensor._seed}')  # noqa

    llm = Llama3Llm(
        args.model,
        size=args.size,
        quantize=args.quantize,
        shard=args.shard,

        temperature=args.temperature,
    )

    if (prompt := args.prompt) is not None:
        run_prompt(llm, prompt)
    else:
        run_repl(llm)


if __name__ == '__main__':
    _main()
