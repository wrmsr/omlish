import argparse
import pathlib

from omlish import check
from tinygrad import Tensor

from .fetch import fetch_model
from .llm import Llama3Llm


##


def run_repl(llm: Llama3Llm) -> None:
    prompt = [
        llm.tokenizer.bos_id,
        *llm.encode_message('system', 'You are an helpful assistant.'),
    ]

    start_pos = llm.prefill(prompt)
    while True:
        toks = llm.encode_message('user', input('Q: ')) + llm.encode_role('assistant')

        start_pos = llm.prefill(toks[:-1], start_pos=start_pos)
        last_tok = toks[-1]
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

    run_repl(llm)


if __name__ == '__main__':
    _main()
