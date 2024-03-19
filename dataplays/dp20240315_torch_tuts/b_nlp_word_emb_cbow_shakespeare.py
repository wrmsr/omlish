"""
Author: Robert Guthrie
"""
import collections
import math
import os
import re
import typing as ta

from omlish import cached
from omlish import lang
from omlish import dataclasses as dc

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

os.environ['GUTENBERG_MIRROR'] = 'http://mirrors.xmission.com/gutenberg/'

import gutenberg.acquire
import gutenberg.cleanup
import gutenberg._domain_model.exceptions as gutenbarg_exceptions


@lang.cached_nullary
def load_raw_text() -> list[str]:
    # raw_text = """We are about to study the idea of a computational process.
    # Computational processes are abstract beings that inhabit computers.
    # As they evolve, processes manipulate other abstract things called data.
    # The evolution of a process is directed by a pattern of rules
    # called a program. People create programs to direct processes. In effect,
    # we conjure the spirits of the computer with our spells.""".split()

    try:
        gutenberg.acquire.get_metadata_cache().populate()
    except gutenbarg_exceptions.CacheAlreadyExistsException:
        pass

    shakespeare = gutenberg.cleanup.strip_headers(gutenberg.acquire.load_etext(100))

    s = shakespeare.split('\nTHE END', 1)[-1]
    s = s.lower()
    s = re.sub(r'[,\.\?!:;]+', '', s)
    return s.split()


@dc.dataclass(frozen=True)
class Data:
    raw_text: ta.Sequence[str]
    context_size: int = 2

    @cached.property
    def vocab(self) -> ta.AbstractSet[str]:
        return set(self.raw_text)

    @cached.property
    def word_counts(self) -> ta.Mapping[str, int]:
        return collections.Counter(self.raw_text)

    @cached.property
    def words(self) -> ta.Sequence[str]:
        return sorted(self.vocab)

    @cached.property
    def vocab_size(self) -> int:
        return len(self.vocab)

    @cached.property
    def word_to_idx(self) -> ta.Mapping[str, int]:
        return {word: i for i, word in enumerate(self.words)}


class CBOW(nn.Module):

    def __init__(
            self,
            vocab_size,
            embedding_dim,
            context_size,
            hidden_dim,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.linear1 = nn.Linear(context_size * 2 * embedding_dim, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, vocab_size)

    def forward(self, inputs):
        x = self.embedding(inputs)
        x = x.view(inputs.shape[0], -1)
        x = self.linear1(x)
        x = F.relu(x)
        x = self.linear2(x)
        x = F.log_softmax(x, 1)
        return x


def train_model(
        d: Data,
        *,
        epochs: int = 20,
        context_size: int = 2,
        batch_size: int = 2048,
        embedding_dim: int = 32,
        hidden_dim: int = 256
) -> nn.Module:
    data = []
    for i in range(context_size, len(d.raw_text) - context_size):
        context = (
                [d.raw_text[i - j - 1] for j in range(context_size)] +
                [d.raw_text[i + j + 1] for j in range(context_size)]
        )
        target = d.raw_text[i]
        data.append((context, target))

    dev = torch.device('cuda') if torch.cuda.is_available() else torch.device('mps')

    model = CBOW(
        d.vocab_size,
        embedding_dim,
        context_size,
        hidden_dim,
    ).to(dev)

    loss_func = nn.NLLLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

    contexts = torch.tensor(
        [[d.word_to_idx[w] for w in context] for context, target in data],
        dtype=torch.long,
        device=dev,
    )
    targets = torch.tensor(
        [d.word_to_idx[target] for contexct, target in data],
        dtype=torch.long,
        device=dev,
    )

    bs = batch_size
    for epoch in range(epochs):
        total_loss = 0
        n = math.ceil(len(data) / bs)
        for i in range(n):
            context_batch = contexts[i * bs:(i + 1) * bs]
            target_batch = targets[i * bs:(i + 1) * bs]
            model.zero_grad()
            log_probs = model(context_batch)
            loss = loss_func(log_probs, target_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            print((i, n, loss.item()))
        # print(total_loss)

    return model


def _main():
    torch.manual_seed(1)

    # raw_text = """We are about to study the idea of a computational process.
    # Computational processes are abstract beings that inhabit computers.
    # As they evolve, processes manipulate other abstract things called data.
    # The evolution of a process is directed by a pattern of rules
    # called a program. People create programs to direct processes. In effect,
    # we conjure the spirits of the computer with our spells.""".split()

    raw_text = load_raw_text()

    d = Data(raw_text)

    model = train_model(d)

    # def make_context_vector(context):
    #     idxs = [word_to_idx[w] for w in context]
    #     return torch.tensor(idxs, dtype=torch.long)
    #
    # make_context_vector(data[0][0])  # example

    word_weights = model.embedding.weight.detach().cpu().numpy()
    word_lengths = np.linalg.norm(word_weights, axis=1)
    normalized_words = (word_weights.T / word_lengths).T

    def similar_words(word):
        dists = np.dot(normalized_words, normalized_words[d.word_to_idx[word]])
        closest = np.argsort(dists)[-10:]
        for c in reversed(closest):
            print((c, d.words[c], dists[c]))

    # similar_words("process")
    similar_words("mated")


if __name__ == '__main__':
    _main()
