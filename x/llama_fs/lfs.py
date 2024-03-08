"""
https://github.com/bkitano/llama-from-scratch/blob/main/llama.ipynb
"""
import torch
from torch import nn
from torch.nn import functional as F
import numpy as np
from matplotlib import pyplot as plt
import time
import pandas as pd


lines = open('./input.txt', 'r').read()

vocab = sorted(list(set(lines)))
itos = {i:ch for i, ch in enumerate(vocab)}
stoi = {ch:i for i, ch in enumerate(vocab)}

print(lines[:30])


# simple tokenization by characters
def encode(s):
    return [stoi[ch] for ch in s]

def decode(l):
    return ''.join([itos[i] for i in l])

print('vocab size:', len(vocab))
print(decode(encode("hello")))


MASTER_CONFIG = {
    "vocab_size": len(vocab),
}


dataset = torch.tensor(encode(lines), dtype=torch.int8)
print(dataset.shape)
