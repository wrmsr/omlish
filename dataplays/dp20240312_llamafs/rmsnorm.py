from torch import nn
import torch


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


class RealRMSNorm(nn.Module):
    """
    https://github.com/bzhangGo/rmsnorm/blob/2e726f1a3f106bb719056422f4f9b6aca03d3ce6/rmsnorm_torch.py

    BSD 3-Clause License

    Copyright (c) 2019, Biao Zhang
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    3. Neither the name of the copyright holder nor the names of its
       contributors may be used to endorse or promote products derived from
       this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """

    def __init__(self, d, p=-1., eps=1e-8, bias=False):
        """
            Root Mean Square Layer Normalization
        :param d: model size
        :param p: partial RMSNorm, valid value [0, 1], default -1.0 (disabled)
        :param eps:  epsilon value, default 1e-8
        :param bias: whether use bias term for RMSNorm, disabled by
            default because RMSNorm doesn't enforce re-centering invariance.
        """
        super().__init__()

        self.eps = eps
        self.d = d
        self.p = p
        self.bias = bias

        self.scale = nn.Parameter(torch.ones(d))
        self.register_parameter("scale", self.scale)

        if self.bias:
            self.offset = nn.Parameter(torch.zeros(d))
            self.register_parameter("offset", self.offset)

    def forward(self, x):
        if self.p < 0. or self.p > 1.:
            norm_x = x.norm(2, dim=-1, keepdim=True)
            d_x = self.d
        else:
            partial_size = int(self.d * self.p)
            partial_x, _ = torch.split(x, [partial_size, self.d - partial_size], dim=-1)

            norm_x = partial_x.norm(2, dim=-1, keepdim=True)
            d_x = partial_size

        rms_x = norm_x * d_x ** (-1. / 2)
        x_normed = x / (rms_x + self.eps)

        if self.bias:
            return self.scale * x_normed + self.offset

        return self.scale * x_normed


def test():
    torch.random.manual_seed(0)

    config = {
        'batch_size': 5,
        'context_window': 11,
        'd_model': 13,
    }
    batch = torch.randn((config['batch_size'], config['context_window'], config['d_model']))

    m = RMSNorm((config['context_window'], config['d_model']))
    g = m(batch)
    assert g.shape == (config['batch_size'], config['context_window'], config['d_model'])

    rm = RealRMSNorm(config['d_model'])
    rg = rm(batch)

    from extra.models.llama import RMSNorm as TgRMSNorm
    import tinygrad as tg
    tgm = TgRMSNorm(config['d_model'])
    tgg = torch.tensor(tgm(tg.Tensor(batch.numpy())).numpy())
    assert torch.allclose(rg, tgg)

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
