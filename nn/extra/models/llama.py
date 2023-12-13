from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

from ... import Device
from ... import Tensor
from ... import TinyJit
from ... import Variable
from ... import dtypes
from ... import nn


# https://github.com/facebookresearch/llama/blob/1076b9c51c77ad06e9d7ba8a4c6df775741732bd/llama/model.py#L47
def precompute_freqs_cis(dim: int, end: int, theta: float = 10000.0) -> Tensor:
    freqs = 1.0 / (theta ** (Tensor.arange(0, dim, 2)[: (dim // 2)] / dim))
    freqs = Tensor.arange(end).unsqueeze(dim=1) * freqs.unsqueeze(dim=0)
    return Tensor.stack([Tensor.cos(freqs), Tensor.sin(freqs)], dim=-1).reshape(
        1, end, 1, dim // 2, 2
    )


# (a+i*b) * (c+i*d) = (ac-bd) + i*(ad+bc)
def complex_mult(A, c, d):
    a, b = A[:, :, :, :, 0:1], A[:, :, :, :, 1:2]
    ro = a * c - b * d
    co = a * d + b * c
    return ro.cat(co, dim=-1)


def apply_rotary_emb(xq, xk, freqs_cis) -> Tuple[Tensor, Tensor]:
    assert (
        freqs_cis.shape[1] == xq.shape[1] and freqs_cis.shape[1] == xk.shape[1]
    ), f"freqs_cis shape mismatch {freqs_cis.shape} xq:{xq.shape} xk:{xk.shape}"
    xq = xq.reshape(*xq.shape[0:-1], -1, 2)
    xk = xk.reshape(*xk.shape[0:-1], -1, 2)
    assert len(xq.shape) == 5 and len(xk.shape) == 5 and len(freqs_cis.shape) == 5
    c, d = (
        freqs_cis[:, : xq.shape[1], :, :, 0:1],
        freqs_cis[:, : xq.shape[1], :, :, 1:2],
    )
    xq_out = complex_mult(xq, c, d)
    xk_out = complex_mult(xk, c, d)
    return xq_out.flatten(3), xk_out.flatten(3)


def repeat_kv(x: Tensor, n_rep: int) -> Tensor:
    bs, seqlen, n_kv_heads, head_dim = x.shape
    if n_rep == 1:
        return x
    return (
        x.reshape(bs, seqlen, n_kv_heads, 1, head_dim)
        .expand(bs, seqlen, n_kv_heads, n_rep, head_dim)
        .reshape(bs, seqlen, n_kv_heads * n_rep, head_dim)
    )


class RMSNorm:
    def __init__(self, dim, eps=1e-6):
        self.eps = eps
        self.weight = Tensor.ones(dim)

    def __call__(self, x: Tensor):
        # TODO: convert to float?
        return (x * (x.pow(2).mean(-1, keepdim=True) + self.eps).rsqrt()) * self.weight


class Attention:
    def __init__(self, dim, n_heads, n_kv_heads, max_context, linear=nn.Linear):
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

    def __call__(
        self,
        x: Tensor,
        start_pos: Union[Variable, int],
        freqs_cis: Tensor,
        mask: Optional[Tensor],
    ) -> Tensor:
        xq, xk, xv = self.wq(x), self.wk(x), self.wv(x)
        xq = xq.reshape(xq.shape[0], xq.shape[1], self.n_heads, self.head_dim)
        xk = xk.reshape(xk.shape[0], xk.shape[1], self.n_kv_heads, self.head_dim)
        xv = xv.reshape(xv.shape[0], xv.shape[1], self.n_kv_heads, self.head_dim)
        xq, xk = apply_rotary_emb(xq, xk, freqs_cis=freqs_cis)
        bsz, seqlen, n_heads, head_dim = xq.shape

        # create kv cache
        if not hasattr(self, "cache_k"):
            self.cache_k, self.cache_v = Tensor.zeros(
                bsz, self.max_context, self.n_kv_heads, self.head_dim
            ), Tensor.zeros(bsz, self.max_context, self.n_kv_heads, self.head_dim)

        keys = self.cache_k.shrink((None, (0, start_pos), None, None)).cat(xk, dim=1)
        values = self.cache_v.shrink((None, (0, start_pos), None, None)).cat(xv, dim=1)

        # update the cache
        self.cache_k.assign(
            keys.pad(
                (None, (0, self.max_context - start_pos - seqlen), None, None)
            ).contiguous()
        ).realize()
        self.cache_v.assign(
            values.pad(
                (None, (0, self.max_context - start_pos - seqlen), None, None)
            ).contiguous()
        ).realize()

        keys, values = repeat_kv(keys, self.n_rep), repeat_kv(values, self.n_rep)

        xq, keys, values = (
            xq.transpose(1, 2),
            keys.transpose(1, 2),
            values.transpose(1, 2),
        )
        attn = (
            xq.scaled_dot_product_attention(keys, values, mask)
            .transpose(1, 2)
            .reshape(bsz, seqlen, -1)
        )
        return self.wo(attn)


class FeedForward:
    def __init__(self, dim: int, hidden_dim: int, linear=nn.Linear):
        self.w1 = linear(dim, hidden_dim, bias=False)
        self.w2 = linear(hidden_dim, dim, bias=False)
        self.w3 = linear(dim, hidden_dim, bias=False)  # the gate in Gated Linear Unit

    def __call__(self, x: Tensor) -> Tensor:
        return self.w2(
            self.w1(x).silu() * self.w3(x)
        )  # SwiGLU [arxiv/2002.05202, eq (5)]


class TransformerBlock:
    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        n_heads: int,
        n_kv_heads: int,
        norm_eps: float,
        max_context: int,
        linear=nn.Linear,
        feed_forward=FeedForward,
    ):
        self.attention = Attention(dim, n_heads, n_kv_heads, max_context, linear)
        self.feed_forward = feed_forward(dim, hidden_dim, linear)
        self.attention_norm = RMSNorm(dim, norm_eps)
        self.ffn_norm = RMSNorm(dim, norm_eps)

    def __call__(
        self,
        x: Tensor,
        start_pos: Union[Variable, int],
        freqs_cis: Tensor,
        mask: Optional[Tensor],
    ):
        h = x + self.attention(self.attention_norm(x), start_pos, freqs_cis, mask)
        return (h + self.feed_forward(self.ffn_norm(h))).realize()


class Transformer:
    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        n_heads: int,
        n_layers: int,
        norm_eps: float,
        vocab_size,
        linear=nn.Linear,
        n_kv_heads=None,
        rope_theta=10000,
        max_context=1024,
        jit=True,
        feed_forward=FeedForward,
    ):
        self.layers = [
            TransformerBlock(
                dim,
                hidden_dim,
                n_heads,
                n_kv_heads,
                norm_eps,
                max_context,
                linear,
                feed_forward=feed_forward,
            )
            for _ in range(n_layers)
        ]
        self.norm = RMSNorm(dim, norm_eps)
        self.tok_embeddings = nn.Embedding(vocab_size, dim)
        self.output = linear(dim, vocab_size, bias=False)
        self.max_context = max_context
        self.freqs_cis = precompute_freqs_cis(
            dim // n_heads, self.max_context * 2, rope_theta
        )
        self.forward_jit = TinyJit(self.forward) if jit else None

    def forward(
        self, tokens: Tensor, start_pos: Union[Variable, int], temperature: float = 0.0
    ):
        _bsz, seqlen = tokens.shape
        freqs_cis = self.freqs_cis.shrink(
            (None, (start_pos, start_pos + seqlen), None, None, None)
        )
        mask = (
            Tensor.full(
                (1, 1, seqlen, start_pos + seqlen), float("-inf"), dtype=dtypes.float32
            )
            .triu(start_pos + 1)
            .realize()
            if seqlen > 1
            else None
        )

        h = self.tok_embeddings(tokens)
        for layer in self.layers:
            h = layer(h, start_pos, freqs_cis, mask)
        logits = self.output(self.norm(h))
        return (logits[:, -1, :] / (temperature + 1e-10)).softmax().flatten().realize()

    def __call__(self, tokens: Tensor, start_pos: Variable, temperature: float = 0.0):
        # TODO: better way to handle the first call v.s. the rest?
        if tokens.shape[0:2] == (1, 1) and self.forward_jit is not None:
            assert start_pos > 0
            return self.forward_jit(
                tokens,
                Variable("start_pos", 1, self.max_context).bind(start_pos),
                temperature,
            )
        return self.forward(tokens, start_pos, temperature)


# *** helpers ***


def convert_from_huggingface(
    weights: Dict[str, Tensor], model: Transformer, n_heads: int, n_kv_heads: int
):
    def permute(v: Tensor, n_heads: int):
        return (
            v.reshape(n_heads, 2, v.shape[0] // n_heads // 2, v.shape[1])
            .transpose(1, 2)
            .reshape(*v.shape[:2])
        )

    keymap = {
        "model.embed_tokens.weight": "tok_embeddings.weight",
        **{
            f"model.layers.{l}.input_layernorm.weight": f"layers.{l}.attention_norm.weight"
            for l in range(len(model.layers))
        },
        **{
            f"model.layers.{l}.self_attn.{x}_proj.weight": f"layers.{l}.attention.w{x}.weight"
            for x in ["q", "k", "v", "o"]
            for l in range(len(model.layers))
        },
        **{
            f"model.layers.{l}.post_attention_layernorm.weight": f"layers.{l}.ffn_norm.weight"
            for l in range(len(model.layers))
        },
        **{
            f"model.layers.{l}.mlp.{x}_proj.weight": f"layers.{l}.feed_forward.w{y}.weight"
            for x, y in {"gate": "1", "down": "2", "up": "3"}.items()
            for l in range(len(model.layers))
        },
        "model.norm.weight": "norm.weight",
        "lm_head.weight": "output.weight",
    }
    sd = {}
    for k, v in weights.items():
        if ".rotary_emb." in k:
            continue
        v = v.to(Device.DEFAULT)
        if "model.layers" in k:
            if "q_proj" in k:
                v = permute(v, n_heads)
            elif "k_proj" in k:
                v = permute(v, n_kv_heads)
        sd[keymap[k]] = v
    return sd
