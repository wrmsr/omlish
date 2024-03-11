"""
https://github.com/bkitano/llama-from-scratch/blob/main/llama.ipynb
"""
from pprint import pprint
import time

from matplotlib import pyplot as plt
from torch import nn
from torch.nn import functional as F
import numpy as np
import pandas as pd
import torch

from .data import vocab
from .data import dataset
from .data import get_batches
from .data import decode
from .train import train


##


MASTER_CONFIG = {
    "vocab_size": len(vocab()),
    'batch_size': 8,
    'context_window': 16
}


xs, ys = get_batches(
    dataset(),
    'train',
    MASTER_CONFIG['batch_size'],
    MASTER_CONFIG['context_window'],
)

pprint([(decode(xs[i].tolist()), decode(ys[i].tolist())) for i in range(len(xs))])


##


class SimpleBrokenModel(nn.Module):
    def __init__(self, config=MASTER_CONFIG):
        super().__init__()
        self.config = config

        self.embedding = nn.Embedding(config['vocab_size'], config['d_model'])
        self.linear = nn.Sequential(
            nn.Linear(config['d_model'], config['d_model']),
            nn.ReLU(),
            nn.Linear(config['d_model'], config['vocab_size']),
        )

        print("model params:", sum([m.numel() for m in self.parameters()]))

    def forward(self, idx, targets=None):
        x = self.embedding(idx)
        logits = self.linear(x)

        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, self.config['vocab_size']), targets.view(-1))
            return logits, loss

        else:
            return logits

MASTER_CONFIG.update({
    'd_model': 128,
})

model = SimpleBrokenModel(MASTER_CONFIG)

xs, ys = get_batches(
    dataset(),
    'train',
    MASTER_CONFIG['batch_size'],
    MASTER_CONFIG['context_window'],
)

logits, loss = model(xs, ys)


##


MASTER_CONFIG.update({
    'epochs': 1000,
    'log_interval': 10,
    'batch_size': 32,
})

model = SimpleBrokenModel(MASTER_CONFIG)

optimizer = torch.optim.Adam(
    model.parameters(),
)



train(model, optimizer, config=MASTER_CONFIG, print_logs=True)


##


def generate(model, config=MASTER_CONFIG, max_new_tokens=30):
    idx = torch.zeros(5, 1).long()
    for _ in range(max_new_tokens):
        # call the model
        logits = model(idx[:, -config['context_window']:])
        last_time_step_logits = logits[:, -1, :]  # all the batches (1), last time step, all the logits
        p = F.softmax(last_time_step_logits, dim=-1)  # softmax to get probabilities
        idx_next = torch.multinomial(p, num_samples=1)  # sample from the distribution to get the next token
        idx = torch.cat([idx, idx_next], dim=-1)  # append to the sequence
    return [decode(x) for x in idx.tolist()]

print(generate(model))


##

