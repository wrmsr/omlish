import math

from torch import Tensor
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
    signal = signal.view(1, max_length, hidden_size)
    return signal


def get_posenc_harv(
        max_length: int,
        *,
        hidden_size: int = 512,
        max_timescale: float = 10000.0,
        min_timescale: float = 1.0,
) -> Tensor:
    # https://nlp.seas.harvard.edu/2018/04/01/attention.html
    pe = torch.zeros(max_length, hidden_size)
    position = torch.arange(0, max_length).unsqueeze(1)
    log_timescale_increment = math.log(max_timescale / min_timescale) / hidden_size
    div_term = min_timescale * torch.exp(torch.arange(0, hidden_size, 2) * -log_timescale_increment)
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    pe = pe.unsqueeze(0)
    return pe


def _main():
    max_length = 8
    hidden_size = 6
    pe_tunz = get_posenc_tunz(max_length, hidden_size=hidden_size)
    pe_harv = get_posenc_harv(max_length, hidden_size=hidden_size)
    print(pe_tunz.numpy())
    print(pe_harv.numpy())


if __name__ == '__main__':
    _main()
