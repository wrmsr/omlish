import torch
from torch import nn


class RMSNorm(nn.Module):
    def __init__(self, layer_shape, eps=1e-8, bias=False):
        super(RMSNorm, self).__init__()
        self.register_parameter("scale", nn.Parameter(torch.ones(layer_shape)))

    def forward(self, x):
        """
        assumes shape is (batch, seq_len, d_model)
        """
        # frob norm is not the same as RMS. RMS = 1/sqrt(N) * frob norm
        ff_rms = torch.linalg.norm(x, dim=(1, 2)) * x[0].numel() ** -.5
        raw = x / ff_rms.unsqueeze(-1).unsqueeze(-1)
        return self.scale[:x.shape[1], :].unsqueeze(0) * raw


def test():
    config = {
        'batch_size': 5,
        'context_window': 11,
        'd_model': 13,
    }
    batch = torch.randn((config['batch_size'], config['context_window'], config['d_model']))

    m = RMSNorm((config['context_window'], config['d_model']))
    g = m(batch)

    # scaled_batch.var(dim=(1,2))
    assert torch.linalg.norm(torch.arange(5).float()) == (torch.arange(5).float() ** 2).sum() ** .5
    rms = torch.linalg.norm(torch.arange(5).float()) * (torch.arange(5).numel() ** -.5)
    assert torch.allclose(torch.linalg.norm(torch.arange(5).float() / rms), torch.tensor(5 ** .5))
    ff_rms = torch.linalg.norm(batch, dim=(1, 2)) * batch.shape[1:].numel() ** -.5

    # RMS for sure
    ffx = torch.zeros_like(batch)
    for i in range(batch.shape[0]):
        ffx[i] = batch[i] / ff_rms[i]
    assert torch.allclose(torch.linalg.norm(ffx, dim=(1, 2)) ** 2, torch.tensor(143).float())
    assert torch.allclose(ffx, g)


if __name__ == '__main__':
    test()
