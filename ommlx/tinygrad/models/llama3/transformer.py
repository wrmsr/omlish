import typing as ta

from tinygrad import Tensor
from tinygrad import TinyJit
from tinygrad import UOp
from tinygrad import Variable
from tinygrad import nn

from .attention import Attention
from .sampling import sample


Variable_: ta.TypeAlias = UOp


##


# https://github.com/facebookresearch/llama/blob/1076b9c51c77ad06e9d7ba8a4c6df775741732bd/llama/model.py#L47
def precompute_freqs_cis(dim: int, end: int, theta: float = 10000.0) -> Tensor:
    freqs = 1.0 / (theta ** (Tensor.arange(0, dim, 2)[: (dim // 2)] / dim))
    freqs = Tensor.arange(end).unsqueeze(dim=1) * freqs.unsqueeze(dim=0)
    return Tensor.stack(freqs.cos(), freqs.sin(), dim=-1).reshape(1, end, 1, dim // 2, 2)


class FeedForward:
    def __init__(self, dim: int, hidden_dim: int, linear=nn.Linear):
        super().__init__()

        self.w1 = linear(dim, hidden_dim, bias=False)
        self.w2 = linear(hidden_dim, dim, bias=False)
        self.w3 = linear(dim, hidden_dim, bias=False)  # the gate in Gated Linear Unit

    def __call__(self, x: Tensor) -> Tensor:
        return self.w2(
            self.w1(x).silu() * self.w3(x),
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
            qk_norm=None,
    ):
        super().__init__()

        self.attention = Attention(
            dim, n_heads, n_kv_heads, max_context, linear, qk_norm,
        )
        self.feed_forward = feed_forward(dim, hidden_dim, linear)
        self.attention_norm = nn.RMSNorm(dim, norm_eps)
        self.ffn_norm = nn.RMSNorm(dim, norm_eps)

    def __call__(
            self,
            x: Tensor,
            start_pos: Variable_ | int,
            freqs_cis: Tensor,
            mask: Tensor | None,
    ):
        h = x + self.attention(self.attention_norm(x), start_pos, freqs_cis, mask)
        return (h + self.feed_forward(self.ffn_norm(h))).contiguous()


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
            embedding=nn.Embedding,
            n_kv_heads=None,
            rope_theta=10000,
            max_context=1024,
            jit=True,
            feed_forward=FeedForward,
            qk_norm=None,
    ):
        super().__init__()

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
                qk_norm=qk_norm,
            )
            for _ in range(n_layers)
        ]
        self.norm = nn.RMSNorm(dim, norm_eps)
        self.tok_embeddings = embedding(vocab_size, dim)
        self.output = (
            nn.Linear(dim, vocab_size, bias=False)
            if embedding == nn.Embedding
            else linear(dim, vocab_size, bias=False)
        )
        self.max_context = max_context
        self.freqs_cis = precompute_freqs_cis(
            dim // n_heads, self.max_context * 2, rope_theta,
        ).contiguous()
        self.forward_jit = TinyJit(self.forward) if jit else None

    def forward(
            self,
            tokens: Tensor,
            start_pos: Variable_ | int,
            temperature: float,
            top_k: int,
            top_p: float,
            alpha_f: float,
            alpha_p: float,
    ):
        _bsz, seqlen = tokens.shape
        h = self.tok_embeddings(tokens)

        self.freqs_cis = self.freqs_cis.cast(h.dtype).realize()
        freqs_cis = self.freqs_cis.shrink(
            (None, (start_pos, start_pos + seqlen), None, None, None),
        )

        mask = (
            Tensor.full(
                (1, 1, seqlen, start_pos + seqlen),
                float('-inf'),
                dtype=h.dtype,
                device=h.device,
            )
            .triu(start_pos + 1)
            .realize()
        ) if seqlen > 1 else None

        for layer in self.layers:
            h = layer(h, start_pos, freqs_cis, mask)
        logits = self.output(self.norm(h)).float()[:, -1, :]

        return sample(
            logits.flatten(), temperature, top_k, top_p, alpha_f, alpha_p,
        ).realize()

    def __call__(
            self,
            tokens: Tensor,
            start_pos: int,
            temperature: float = 0.0,
            top_k: int = 0,
            top_p: float = 0.8,
            alpha_f: float = 0.0,
            alpha_p: float = 0.0,
    ):
        # TODO: better way to handle the first call v.s. the rest?
        if (
                tokens.shape[0:2] == (1, 1)
                and self.forward_jit is not None
                and start_pos != 0
        ):
            return self.forward_jit(
                tokens,
                Variable('start_pos', 1, self.max_context).bind(start_pos),
                temperature,
                top_k,
                top_p,
                alpha_f,
                alpha_p,
            )

        return self.forward(
            tokens, start_pos, temperature, top_k, top_p, alpha_f, alpha_p,
        )
