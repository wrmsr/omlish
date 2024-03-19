"""
Author: Robert Guthrie
"""
import math

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def _main():
    torch.manual_seed(1)

    CONTEXT_SIZE = 2  # 2 words to the left, 2 to the right

    raw_text = """We are about to study the idea of a computational process.
    Computational processes are abstract beings that inhabit computers.
    As they evolve, processes manipulate other abstract things called data.
    The evolution of a process is directed by a pattern of rules
    called a program. People create programs to direct processes. In effect,
    we conjure the spirits of the computer with our spells.""".split()

    vocab = set(raw_text)
    words = sorted(vocab)
    vocab_size = len(vocab)

    word_to_ix = {word: i for i, word in enumerate(words)}
    data = []
    for i in range(CONTEXT_SIZE, len(raw_text) - CONTEXT_SIZE):
        context = (
                [raw_text[i - j - 1] for j in range(CONTEXT_SIZE)] +
                [raw_text[i + j + 1] for j in range(CONTEXT_SIZE)]
        )
        target = raw_text[i]
        data.append((context, target))
    # print(data[:5])

    EMBEDDING_DIM = 10
    HIDDEN_DIM = 128

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

    model = CBOW()

    loss_func = nn.NLLLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

    bs = 32
    for epoch in range(100):
        total_loss = 0
        for i in range(math.ceil(len(data) / bs)):
            contexts, targets = zip(*data[i * bs:(i + 1) * bs])
            model.zero_grad()
            log_probs = model(torch.tensor([[word_to_ix[w] for w in context] for context in contexts], dtype=torch.long))
            loss = loss_func(log_probs, torch.tensor([word_to_ix[target] for target in targets], dtype=torch.long))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
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

    similar_words("processes")


if __name__ == '__main__':
    _main()
