# -*- coding: utf-8 -*-
"""
**Author**: `Sean Robertson <https://github.com/spro>`_
"""
import glob
import io
import math
import os
import random
import string
import time
import typing as ta
import unicodedata

from omlish import cached
from omlish import dataclasses as dc
from omlish import lang

import matplotlib.pyplot as plt

import torch
import torch.nn as nn


T = ta.TypeVar('T')

all_letters = string.ascii_letters + " .,;'-"
n_letters = len(all_letters) + 1  # Plus EOS marker


def unicode_to_ascii(s: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
        and c in all_letters
    )


def read_lines(filename: str) -> list[str]:
    with io.open(filename, encoding='utf-8') as some_file:
        return [unicode_to_ascii(line.strip()) for line in some_file]


@dc.dataclass(frozen=True)
class Data:
    category_lines: ta.Mapping[str, ta.Sequence[str]]

    @cached.property
    def all_categories(self) -> ta.Sequence[str]:
        return list(self.category_lines)

    @cached.property
    def n_categories(self) -> int:
        return len(self.category_lines)


@lang.cached_nullary
def load_data() -> Data:
    category_lines = {}
    for filename in glob.glob('data/names/*.txt'):
        category = os.path.splitext(os.path.basename(filename))[0]
        lines = read_lines(filename)
        category_lines[category] = lines

    if not category_lines:
        raise RuntimeError(
            'Data not found. Make sure that you downloaded data '
            'from https://download.pytorch.org/tutorial/data.zip and extract it to '
            'the current directory.'
        )

    return Data(category_lines)


class RNN(nn.Module):
    def __init__(
            self,
            n_categories,
            input_size,
            hidden_size,
            output_size,
    ):
        super().__init__()
        self.hidden_size = hidden_size

        self.i2h = nn.Linear(n_categories + input_size + hidden_size, hidden_size)
        self.i2o = nn.Linear(n_categories + input_size + hidden_size, output_size)
        self.o2o = nn.Linear(hidden_size + output_size, output_size)
        self.dropout = nn.Dropout(0.1)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, category, input, hidden):
        input_combined = torch.cat((category, input, hidden), 1)
        hidden = self.i2h(input_combined)
        output = self.i2o(input_combined)
        output_combined = torch.cat((hidden, output), 1)
        output = self.o2o(output_combined)
        output = self.dropout(output)
        output = self.softmax(output)
        return output, hidden

    def init_hidden(self):
        return torch.zeros(1, self.hidden_size)


def random_choice(l: ta.Sequence[T]) -> T:
    return l[random.randint(0, len(l) - 1)]


def random_training_pair(data: Data) -> tuple[str, str]:
    category = random_choice(data.all_categories)
    line = random_choice(data.category_lines[category])
    return category, line


# One-hot vector for category
def make_category_tensor(data: Data, category: str) -> torch.Tensor:
    li = data.all_categories.index(category)
    tensor = torch.zeros(1, data.n_categories)
    tensor[0][li] = 1
    return tensor


# One-hot matrix of first to last letters (not including EOS) for input
def make_input_tensor(line: str) -> torch.Tensor:
    tensor = torch.zeros(len(line), 1, n_letters)
    for li in range(len(line)):
        letter = line[li]
        tensor[li][0][all_letters.find(letter)] = 1
    return tensor


# ``LongTensor`` of second letter to end (EOS) for target
def make_target_tensor(line: str) -> torch.Tensor:
    letter_indexes = [all_letters.find(line[li]) for li in range(1, len(line))]
    letter_indexes.append(n_letters - 1)  # EOS
    return torch.LongTensor(letter_indexes)


def random_training_example(data: Data) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    category, line = random_training_pair(data)
    category_tensor = make_category_tensor(data, category)
    input_line_tensor = make_input_tensor(line)
    target_line_tensor = make_target_tensor(line)
    return category_tensor, input_line_tensor, target_line_tensor


def format_time_since(since: float) -> str:
    now = time.time()
    s = now - since
    m = math.floor(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)


def train_model():
    data = load_data()

    rnn = RNN(
        data.n_categories,
        n_letters,
        128,
        n_letters,
    )

    criterion = nn.NLLLoss()

    learning_rate = 0.0005

    def train_once(category_tensor, input_line_tensor, target_line_tensor):
        target_line_tensor.unsqueeze_(-1)
        hidden = rnn.init_hidden()

        rnn.zero_grad()

        loss = torch.Tensor([0])  # you can also just simply use ``loss = 0``

        for i in range(input_line_tensor.size(0)):
            output, hidden = rnn(category_tensor, input_line_tensor[i], hidden)
            l = criterion(output, target_line_tensor[i])
            loss += l

        loss.backward()

        for p in rnn.parameters():
            p.data.add_(p.grad.data, alpha=-learning_rate)

        return output, loss.item() / input_line_tensor.size(0)

    n_iters = 100000
    print_every = 5000
    plot_every = 500
    all_losses = []
    total_loss = 0  # Reset every ``plot_every`` ``iters``

    start = time.time()

    for iter in range(1, n_iters + 1):
        output, loss = train_once(*random_training_example(data))
        total_loss += loss

        if iter % print_every == 0:
            print('%s (%d %d%%) %.4f' % (format_time_since(start), iter, iter / n_iters * 100, loss))

        if iter % plot_every == 0:
            all_losses.append(total_loss / plot_every)
            total_loss = 0

    plt.figure()
    plt.plot(all_losses)

    max_length = 20

    def sample(category, start_letter='A'):
        with torch.no_grad():  # no need to track history in sampling
            category_tensor = make_category_tensor(category)
            input = make_input_tensor(start_letter)
            hidden = rnn.init_hidden()

            output_name = start_letter

            for i in range(max_length):
                output, hidden = rnn(category_tensor, input[0], hidden)
                topv, topi = output.topk(1)
                topi = topi[0][0]
                if topi == n_letters - 1:
                    break
                else:
                    letter = all_letters[topi]
                    output_name += letter
                input = make_input_tensor(letter)

            return output_name

    def print_samples(category, start_letters='ABC'):
        for start_letter in start_letters:
            print(sample(category, start_letter))

    print_samples('Russian', 'RUS')
    print_samples('German', 'GER')
    print_samples('Spanish', 'SPA')
    print_samples('Chinese', 'CHI')


def _main():
    train_model()


if __name__ == '__main__':
    _main()
