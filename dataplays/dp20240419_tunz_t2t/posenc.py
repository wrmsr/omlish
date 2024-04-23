"""
tensor([[     0.0000,      0.0000,      0.0000,      1.0000,      1.0000,      1.0000],
        [     0.8415,      0.0100,      0.0001,      0.5403,      0.9999,      1.0000],
        [     0.9093,      0.0200,      0.0002,     -0.4161,      0.9998,      1.0000],
        [     0.1411,      0.0300,      0.0003,     -0.9900,      0.9996,      1.0000],
        [    -0.7568,      0.0400,      0.0004,     -0.6536,      0.9992,      1.0000],
        [    -0.9589,      0.0500,      0.0005,      0.2837,      0.9988,      1.0000],
        [    -0.2794,      0.0600,      0.0006,      0.9602,      0.9982,      1.0000],
        [     0.6570,      0.0699,      0.0007,      0.7539,      0.9976,      1.0000]])
tensor([[ 0.0000,  1.0000,  0.0000,  1.0000,  0.0000,  1.0000],
        [ 0.8415,  0.5403,  0.0464,  0.9989,  0.0022,  1.0000],
        [ 0.9093, -0.4161,  0.0927,  0.9957,  0.0043,  1.0000],
        [ 0.1411, -0.9900,  0.1388,  0.9903,  0.0065,  1.0000],
        [-0.7568, -0.6536,  0.1846,  0.9828,  0.0086,  1.0000],
        [-0.9589,  0.2837,  0.2300,  0.9732,  0.0108,  0.9999],
        [-0.2794,  0.9602,  0.2749,  0.9615,  0.0129,  0.9999],
        [ 0.6570,  0.7539,  0.3192,  0.9477,  0.0151,  0.9999]])
tensor([[     0.0000,      0.0000,      0.0000,      1.0000,      1.0000,      1.0000],
        [     0.8415,      0.0100,      0.0001,      0.5403,      0.9999,      1.0000],
        [     0.9093,      0.0200,      0.0002,     -0.4161,      0.9998,      1.0000],
        [     0.1411,      0.0300,      0.0003,     -0.9900,      0.9996,      1.0000],
        [    -0.7568,      0.0400,      0.0004,     -0.6536,      0.9992,      1.0000],
        [    -0.9589,      0.0500,      0.0005,      0.2837,      0.9988,      1.0000],
        [    -0.2794,      0.0600,      0.0006,      0.9602,      0.9982,      1.0000],
        [     0.6570,      0.0699,      0.0007,      0.7539,      0.9976,      1.0000]])
"""
import math

from torch import Tensor
import numpy as np  # noqa
import tensorflow.compat.v1 as tf
import torch
import torch.nn.functional as F  # noqa


def get_posenc_tunz(
        max_length: int,
        *,
        hidden_size: int = 512,
        max_timescale: float = 10000.0,
        min_timescale: float = 1.0,
) -> Tensor:
    position = torch.arange(max_length).unsqueeze(1)  # (8, 1)

    num_timescales = hidden_size // 2  # = 3
    log_timescale_increment = math.log(max_timescale / min_timescale) / max(num_timescales - 1, 1)  # = 4.6051
    inv_timescales = min_timescale * torch.exp(torch.arange(num_timescales) * -log_timescale_increment)  # (3,)
    scaled_time = position * inv_timescales.unsqueeze(0)  # (8, 3)
    signal = torch.cat([torch.sin(scaled_time), torch.cos(scaled_time)], dim=1)  # (8, 6)
    signal = F.pad(signal, (0, 0, 0, hidden_size % 2))
    return signal


def get_posenc_harv(
        max_length: int,
        *,
        hidden_size: int = 512,
        max_timescale: float = 10000.0,
        min_timescale: float = 1.0,
) -> Tensor:
    position = torch.arange(0, max_length).unsqueeze(1)

    # https://nlp.seas.harvard.edu/2018/04/01/attention.html

    # num_timescales = hidden_size // 2
    # log_timescale_increment = math.log(max_timescale / min_timescale) / max(num_timescales - 1, 1)

    log_timescale_increment = math.log(max_timescale) / hidden_size

    div_term = min_timescale * torch.exp(torch.arange(0, hidden_size, 2) * -log_timescale_increment)
    pe = torch.zeros(max_length, hidden_size)
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)

    return pe


def get_posenc_t2t(
        max_length: int,
        *,
        hidden_size: int = 512,
        min_timescale: float = 1.0,
        max_timescale: float = 1.0e4,
):
    position = tf.expand_dims(tf.range(0, max_length), 1)
    num_timescales = hidden_size // 2
    log_timescale_increment = (
            math.log(float(max_timescale) / float(min_timescale)) /
            (tf.to_float(num_timescales) - 1)
    )
    inv_timescales = min_timescale * tf.exp(
            tf.to_float(tf.range(num_timescales)) *
            -log_timescale_increment
    )
    scaled_time = (
            tf.expand_dims(tf.to_float(position), 2) *
            tf.expand_dims(tf.expand_dims(inv_timescales, 0), 0)
    )
    signal = tf.concat([tf.sin(scaled_time), tf.cos(scaled_time)], axis=2)
    signal = tf.pad(signal, [[0, 0], [0, 0], [0, tf.mod(hidden_size, 2)]])
    signal = tf.squeeze(signal)
    return torch.tensor(signal.numpy())


def _main():
    torch.set_printoptions(threshold=10_000, linewidth=10_000, sci_mode=False)

    max_length = 8
    hidden_size = 6

    pe_tunz = get_posenc_tunz(max_length, hidden_size=hidden_size)
    pe_harv = get_posenc_harv(max_length, hidden_size=hidden_size)
    pe_t2t = get_posenc_t2t(max_length, hidden_size=hidden_size)

    print(pe_tunz)
    print(pe_harv)
    print(pe_t2t)

    assert torch.allclose(pe_tunz, pe_t2t)


if __name__ == '__main__':
    _main()
