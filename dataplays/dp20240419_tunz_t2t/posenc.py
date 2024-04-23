import math

from torch import Tensor
import numpy as np  # noqa
import torch
import torch.nn.functional as F


def get_posenc_tunz(
        max_length: int,
        *,
        hidden_size: int = 512,
        max_timescale: float = 10000.0,
        min_timescale: float = 1.0,
) -> Tensor:
    num_timescales = hidden_size // 2
    log_timescale_increment = math.log(max_timescale / min_timescale) / max(num_timescales - 1, 1)
    inv_timescales = min_timescale * torch.exp(torch.arange(num_timescales) * -log_timescale_increment)
    position = torch.arange(max_length)
    scaled_time = position.unsqueeze(1) * inv_timescales.unsqueeze(0)
    signal = torch.cat([torch.sin(scaled_time), torch.cos(scaled_time)], dim=1)
    signal = F.pad(signal, (0, 0, 0, hidden_size % 2))

    # !!!
    # pe = torch.zeros(max_length, hidden_size)
    # pe[:, 0::2] = signal[:, :num_timescales]
    # pe[:, 1::2] = signal[:, num_timescales:]
    # signal = pe

    return signal


def get_posenc_harv(
        max_length: int,
        *,
        hidden_size: int = 512,
        max_timescale: float = 10000.0,
        min_timescale: float = 1.0,
) -> Tensor:
    # https://nlp.seas.harvard.edu/2018/04/01/attention.html
    position = torch.arange(0, max_length).unsqueeze(1)
    log_timescale_increment = math.log(max_timescale / min_timescale) / hidden_size
    div_term = min_timescale * torch.exp(torch.arange(0, hidden_size, 2) * -log_timescale_increment)
    pe = torch.zeros(max_length, hidden_size)
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    return pe


def _main():
    torch.set_printoptions(threshold=10_000, linewidth=10_000, sci_mode=False)

    max_length = 8
    hidden_size = 6
    pe_tunz = get_posenc_tunz(max_length, hidden_size=hidden_size)
    pe_harv = get_posenc_harv(max_length, hidden_size=hidden_size)
    print(pe_tunz)
    print(pe_harv)
    pe_tunz_np = pe_tunz.numpy()
    pe_harv_np = pe_harv.numpy()
    print(pe_tunz_np)
    print(pe_harv_np)

if __name__ == '__main__':
    _main()
