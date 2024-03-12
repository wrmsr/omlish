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

from .data import dataset
from .data import decode
from .data import get_batches
from .data import vocab
from .generate import generate
from .rmsnorm import RMSNorm
from .train import train


##


MASTER_CONFIG = {
    "vocab_size": len(vocab()),
    'batch_size': 8,
    'context_window': 16
}


xs, ys = get_batches(dataset(), 'train', MASTER_CONFIG)

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

xs, ys = get_batches(dataset(), 'train', MASTER_CONFIG)

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


train(model, optimizer, MASTER_CONFIG, print_logs=True)


##


print(generate(model, MASTER_CONFIG))


##


class SimpleModel_RMS(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

        self.embedding = nn.Embedding(config['vocab_size'], config['d_model'])
        self.rms = RMSNorm((config['context_window'], config['d_model']))
        self.linear = nn.Sequential(
            nn.Linear(config['d_model'], config['d_model']),
            nn.ReLU(),
            nn.Linear(config['d_model'], config['vocab_size']),
        )

        print("model params:", sum([m.numel() for m in self.parameters()]))

    def forward(self, idx, targets=None):
        x = self.embedding(idx)
        x = self.rms(x)  # rms pre-normalization
        logits = self.linear(x)

        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, self.config['vocab_size']), targets.view(-1))
            return logits, loss

        else:
            return logits


model = SimpleModel_RMS(MASTER_CONFIG)
xs, ys = get_batches(dataset(), 'train', MASTER_CONFIG)

logits, loss = model(xs, ys)
optimizer = torch.optim.Adam(model.parameters())
train(model, optimizer, MASTER_CONFIG, print_logs=True)


##


