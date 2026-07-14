import typing as ta

from tinygrad import Tensor
from tinygrad import UOp
from tinygrad import nn
from tinygrad.helpers import getenv

from omlish import check


Variable_: ta.TypeAlias = UOp


##


# matches meta, non hugging face weights
# (a+i*b) * (c+i*d) = (ac-bd) + i*(ad+bc)
def complex_mult(a, c, d):
    a, b = a[..., 0:1], a[..., 1:2]
    ro = a * c - b * d
    co = a * d + b * c
    return ro.cat(co, dim=-1)


def apply_rotary_emb(
        xq: Tensor,
        xk: Tensor,
        freqs_cis: Tensor,
) -> tuple[Tensor, Tensor]:
    check.state(
        freqs_cis.shape[1] == xq.shape[1] == xk.shape[1],
        f'freqs_cis shape mismatch {freqs_cis.shape} xq:{xq.shape} xk:{xk.shape}',
    )

    xq = xq.reshape(*xq.shape[0:-1], -1, 2)
    xk = xk.reshape(*xk.shape[0:-1], -1, 2)
    check.state(len(xq.shape) == len(xk.shape) == len(freqs_cis.shape) == 5)

    c, d = freqs_cis[..., 0:1], freqs_cis[..., 1:2]
    xq_out = complex_mult(xq, c, d)
    xk_out = complex_mult(xk, c, d)
    return xq_out.flatten(3), xk_out.flatten(3)


def repeat_kv(x: Tensor, n_rep: int) -> Tensor:
    bs, seqlen, n_kv_heads, head_dim = x.shape
    if n_rep == 1:
        return x

    # NOTE: this is different from x.repeat((1, 1, n_rep, 1))
    return x.repeat((1, 1, 1, n_rep)).reshape(bs, seqlen, n_kv_heads * n_rep, head_dim)


class Attention:
    def __init__(
            self,
            dim,
            n_heads,
            n_kv_heads=None,
            max_context=0,
            linear=nn.Linear,
            qk_norm: float | None = None,
    ) -> None:
        super().__init__()

        self.n_heads = n_heads
        self.n_kv_heads = (
            n_kv_heads if n_kv_heads is not None else n_heads
        )  # n_kv_heads != n_heads implies MQA [arxiv/2307.09288, A.2.1]
        self.head_dim = dim // n_heads
        self.n_rep = self.n_heads // self.n_kv_heads
        self.max_context = max_context

        self.wq = linear(dim, self.n_heads * self.head_dim, bias=False)
        self.wk = linear(dim, self.n_kv_heads * self.head_dim, bias=False)
        self.wv = linear(dim, self.n_kv_heads * self.head_dim, bias=False)
        self.wo = linear(self.n_heads * self.head_dim, dim, bias=False)

        self.q_norm = nn.RMSNorm(dim, qk_norm) if qk_norm is not None else None
        self.k_norm = nn.RMSNorm(dim, qk_norm) if qk_norm is not None else None

    def __call__(
            self,
            x: Tensor,
            start_pos: Variable_ | int,
            freqs_cis: Tensor,
            mask: Tensor | None = None,
    ) -> Tensor:
        if getenv('WQKV'):
            if not hasattr(self, 'wqkv'):
                self.wqkv = Tensor.cat(self.wq.weight, self.wk.weight, self.wv.weight)
            xqkv = x @ self.wqkv.T
            xq, xk, xv = xqkv.split(
                [
                    self.wq.weight.shape[0],
                    self.wk.weight.shape[0],
                    self.wv.weight.shape[0],
                ],
                dim=2,
            )
        else:
            xq, xk, xv = self.wq(x), self.wk(x), self.wv(x)

        if self.q_norm is not None and self.k_norm is not None:
            xq = self.q_norm(xq)
            xk = self.k_norm(xk)

        xq = xq.reshape(xq.shape[0], xq.shape[1], self.n_heads, self.head_dim)
        xk = xk.reshape(xk.shape[0], xk.shape[1], self.n_kv_heads, self.head_dim)
        xv = xv.reshape(xv.shape[0], xv.shape[1], self.n_kv_heads, self.head_dim)

        xq, xk = apply_rotary_emb(xq, xk, freqs_cis)
        bsz, seqlen, _, _ = xq.shape

        # create kv cache
        # if not hasattr(self, 'cache_kv'):
        #     self.cache_kv = (
        #         Tensor.zeros(
        #             2,
        #             bsz,
        #             self.max_context,
        #             self.n_kv_heads,
        #             self.head_dim,
        #             dtype=x.dtype,
        #         )
        #         .contiguous()
        #         .realize()
        #     )
        #     if isinstance(x.device, tuple):
        #         # TODO: instead of specifying how to shard, it can follow how xk and xv are being sharded
        #         self.cache_kv.shard_(
        #             (x.device), axis=3 if getenv('SHARD_KVCACHE') else None,
        #         ).realize()
        #
        # # update the cache
        # check.state(xk.dtype == xv.dtype == self.cache_kv.dtype, f'{xk.dtype=}, {xv.dtype=}, {self.cache_kv.dtype=}')
        #
        # self.cache_kv[:, :, start_pos:start_pos + seqlen, :, :].assign(Tensor.stack(xk, xv)).realize()
        #
        # keys = self.cache_kv[0, :, 0:start_pos + seqlen, :, :]
        # values = self.cache_kv[1, :, 0:start_pos + seqlen, :, :]

        if self.max_context:
            if not hasattr(self, 'cache_kv'):
                self.cache_kv = (
                    Tensor.zeros(
                        2,
                        bsz,
                        self.max_context,
                        self.n_kv_heads,
                        self.head_dim,
                        dtype=x.dtype,
                    )
                    .contiguous()
                    .realize()
                )
                if isinstance(x.device, tuple):
                    # TODO: instead of specifying how to shard, it can follow how xk and xv are being sharded
                    self.cache_kv.shard_(
                        (x.device),
                        axis=3 if getenv('SHARD_KVCACHE') else None,
                    ).realize()

            # update the cache
            check.state(
                xk.dtype == xv.dtype == self.cache_kv.dtype,
                f'{xk.dtype=}, {xv.dtype=}, {self.cache_kv.dtype=}',
            )
            self.cache_kv[:, :, start_pos:start_pos + seqlen, :, :].assign(Tensor.stack(xk, xv)).realize()

            keys = self.cache_kv[0, :, 0:start_pos + seqlen, :, :]
            values = self.cache_kv[1, :, 0:start_pos + seqlen, :, :]

        else:
            check.state(start_pos == 0)
            keys, values = xk, xv

        keys = repeat_kv(keys, self.n_rep)
        values = repeat_kv(values, self.n_rep)

        xq, keys, values = (
            xq.transpose(1, 2),
            keys.transpose(1, 2),
            values.transpose(1, 2),
        )
        attn = xq.scaled_dot_product_attention(keys, values, mask).transpose(1, 2)
        attn = attn.reshape(bsz, seqlen, -1)
        return self.wo(attn)
