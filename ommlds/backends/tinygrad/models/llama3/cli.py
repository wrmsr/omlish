import argparse
import pathlib
import typing as ta

from tinygrad import Tensor

from omlish import check

from .fetch import fetch_model
from .llm import Llama3Llm


##


class _RunToStopResult(ta.NamedTuple):
    start_pos: int
    last_tok: int


def _run_to_stop(llm: Llama3Llm, start_pos: int, last_tok: int) -> _RunToStopResult:
    while True:
        tok = llm.feed(
            [last_tok],
            start_pos,
        )
        tok = tok.item()

        start_pos += 1
        last_tok = tok
        if tok in llm.tokenizer.stop_tokens:
            break

        print(llm.tokenizer.decode([tok]), end='', flush=True)

    print(flush=True)

    return _RunToStopResult(start_pos, last_tok)


def _run_new_toks(llm: Llama3Llm, toks: list[int], start_pos: int = 0) -> int:
    start_pos = llm.prefill(toks[:-1], start_pos=start_pos)
    last_tok = toks[-1]
    return _run_to_stop(llm, start_pos, last_tok).start_pos


#


def run_prompt(llm: Llama3Llm, prompt: str) -> None:
    _run_new_toks(llm,[
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
        start_pos = _run_new_toks(llm, [
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
        choices=['1B', '8B', '70B'],
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
        type=int,
        default=0.85,
        help='Temperature',
    )
    parser.add_argument(
        '--prompt',
    )
    return parser


def _main() -> None:
    Tensor.no_grad = True

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
