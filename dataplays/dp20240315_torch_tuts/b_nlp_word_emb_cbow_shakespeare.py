"""
Author: Robert Guthrie
"""
import math
import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

os.environ['GUTENBERG_MIRROR'] = 'http://mirrors.xmission.com/gutenberg/'

import gutenberg.acquire
import gutenberg.cleanup
import gutenberg._domain_model.exceptions as gutenbarg_exceptions


def _main():
    torch.manual_seed(1)

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

    raw_text = shakespeare.split('\nTHE END', 1)[-1].lower().split()

    vocab = set(raw_text)
    words = sorted(vocab)
    vocab_size = len(vocab)
    word_to_ix = {word: i for i, word in enumerate(words)}

    CONTEXT_SIZE = 2  # 2 words to the left, 2 to the right

    data = []
    for i in range(CONTEXT_SIZE, len(raw_text) - CONTEXT_SIZE):
        context = (
                [raw_text[i - j - 1] for j in range(CONTEXT_SIZE)] +
                [raw_text[i + j + 1] for j in range(CONTEXT_SIZE)]
        )
        target = raw_text[i]
        data.append((context, target))

    EMBEDDING_DIM = 32
    HIDDEN_DIM = 256

    dev = torch.device('cuda') if torch.cuda.is_available() else torch.device('mps')

    class CBOW(nn.Module):

        def __init__(self):
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, EMBEDDING_DIM)
            self.linear1 = nn.Linear(CONTEXT_SIZE * 2 * EMBEDDING_DIM, HIDDEN_DIM)
            self.linear2 = nn.Linear(HIDDEN_DIM, vocab_size)

        def forward(self, inputs):
            x = self.embedding(inputs)
            x = x.view(inputs.shape[0], -1)
            x = self.linear1(x)
            x = F.relu(x)
            x = self.linear2(x)
            x = F.log_softmax(x, 1)
            return x

    model = CBOW().to(dev)

    loss_func = nn.NLLLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

    contexts = torch.tensor(
        [[word_to_ix[w] for w in context] for context, target in data],
        dtype=torch.long,
        device=dev,
    )
    targets = torch.tensor(
        [word_to_ix[target] for contexct, target in data],
        dtype=torch.long,
        device=dev,
    )

    bs = 2048
    for epoch in range(4):
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
        print(total_loss)

    # def make_context_vector(context):
    #     idxs = [word_to_ix[w] for w in context]
    #     return torch.tensor(idxs, dtype=torch.long)
    #
    # make_context_vector(data[0][0])  # example

    word_weights = model.embedding.weight.detach().numpy()
    word_lengths = np.linalg.norm(word_weights, axis=1)
    normalized_words = (word_weights.T / word_lengths).T

    def similar_words(word):
        dists = np.dot(normalized_words, normalized_words[word_to_ix[word]])
        closest = np.argsort(dists)[-10:]
        for c in reversed(closest):
            print((c, words[c], dists[c]))

    similar_words("mated")


if __name__ == '__main__':
    _main()
