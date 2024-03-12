from pprint import pprint

import torch

from omlish import lang


@lang.cached_nullary
def lines() -> str:
    return open('./input.txt', 'r').read()


@lang.cached_nullary
def vocab() -> list[str]:
    return sorted(list(set(lines())))


@lang.cached_nullary
def itos() -> dict[int, str]:
    return {i: ch for i, ch in enumerate(vocab())}


@lang.cached_nullary
def stoi() -> dict[str, int]:
    return {ch: i for i, ch in enumerate(vocab())}


def encode(s: str) -> list[int]:
    return [stoi()[ch] for ch in s]


def decode(l: list[int]) -> str:
    return ''.join([itos()[i] for i in l])


@lang.cached_nullary
def dataset() -> torch.Tensor:
    return torch.tensor(encode(lines()), dtype=torch.int8)


def get_batches(data, split, config):
    train = data[:int(.8 * len(data))]
    val = data[int(.8 * len(data)): int(.9 * len(data))]
    test = data[int(.9 * len(data)):]

    batch_data = train
    if split == 'val':
        batch_data = val

    if split == 'test':
        batch_data = test

    # pick random starting points
    ix = torch.randint(0, batch_data.size(0) - config['context_window'] - 1, (config['batch_size'],))
    x = torch.stack([batch_data[i:i + config['context_window']] for i in ix]).long()
    y = torch.stack([batch_data[i + 1:i + config['context_window'] + 1] for i in ix]).long()
    return x, y
