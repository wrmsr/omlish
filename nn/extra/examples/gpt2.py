#!/usr/bin/env python3
import argparse
from typing import Optional
from typing import Union

import numpy as np
import tiktoken
from tqdm import trange

from ... import Device
from ...helpers import DEBUG
from ...helpers import GlobalCounters
from ...helpers import Timing
from ...helpers import colored
from ...helpers import dtypes
from ...helpers import fetch
from ...helpers import getenv
from ...jit import TinyJit
from ...nn import Embedding
from ...nn import LayerNorm
from ...nn import Linear
from ...nn.state import get_state_dict
from ...nn.state import load_state_dict
from ...nn.state import torch_load
from ...shape.symbolic import Variable
from ...tensor import Tensor

MAX_CONTEXT = getenv("MAX_CONTEXT", 128)
HALF = getenv("HALF")


class Attention:
    def __init__(self, dim, n_heads):
        self.c_attn = Linear(dim, 3 * dim, bias=True)
        self.c_proj = Linear(dim, dim, bias=True)
        self.n_heads = n_heads
        self.dim = dim
        self.head_dim = dim // n_heads

    def __call__(
        self, x: Tensor, start_pos: Variable, mask: Optional[Tensor]
    ) -> Tensor:
        if mask is not None:
            # no symbolic shape qkv when consuming prompts
            start_pos = start_pos.val

        if HALF:
            x = x.half()
        xqkv = self.c_attn(x)
        xq, xk, xv = [
            xqkv.shrink((None, None, (i * self.dim, (i + 1) * self.dim))).reshape(
                xqkv.shape[0], xqkv.shape[1], self.n_heads, self.head_dim
            )
            for i in range(3)
        ]
        bsz, seqlen, n_heads, head_dim = xq.shape

        # create kv cache
        if not hasattr(self, "cache_kv"):
            self.cache_kv = Tensor.zeros(
                2, bsz, MAX_CONTEXT, self.n_heads, self.head_dim
            )
            if HALF:
                self.cache_kv = self.cache_kv.half()

        keys = (
            self.cache_kv[0].shrink((None, (0, start_pos), None, None)).cat(xk, dim=1)
        )
        values = (
            self.cache_kv[1].shrink((None, (0, start_pos), None, None)).cat(xv, dim=1)
        )

        # update the cache
        new_cache = (
            Tensor.stack([keys, values])
            .pad((None, None, (0, MAX_CONTEXT - start_pos - seqlen), None, None))
            .contiguous()
        )
        self.cache_kv.assign(new_cache).realize()

        xq, keys, values = (
            xq.transpose(1, 2),
            keys.transpose(1, 2),
            values.transpose(1, 2),
        )
        return self.c_proj(
            xq.scaled_dot_product_attention(keys, values, mask)
            .cast(dtypes.float32)
            .transpose(1, 2)
            .reshape(bsz, seqlen, -1)
        )


class FeedForward:
    def __init__(self, dim, hidden_dim):
        self.c_fc = Linear(dim, hidden_dim, bias=True)
        self.c_proj = Linear(hidden_dim, dim, bias=True)

    def __call__(self, x: Tensor) -> Tensor:
        return self.c_proj(self.c_fc(x).gelu())


class TransformerBlock:
    def __init__(self, dim, n_heads, norm_eps):
        self.attn = Attention(dim, n_heads)
        self.mlp = FeedForward(dim, 4 * dim)
        self.ln_1 = LayerNorm(dim, norm_eps)
        self.ln_2 = LayerNorm(dim, norm_eps)

    def __call__(self, x: Tensor, start_pos: Variable, mask: Optional[Tensor]):
        h = x + self.attn(self.ln_1(x), start_pos, mask)
        return h + self.mlp(self.ln_2(h))


class Transformer:
    def __init__(self, dim, n_heads, n_layers, norm_eps, vocab_size, max_seq_len=1024):
        self.wte = Embedding(vocab_size, dim)
        self.wpe = Embedding(max_seq_len, dim)
        self.h = [TransformerBlock(dim, n_heads, norm_eps) for _ in range(n_layers)]
        self.ln_f = LayerNorm(dim, norm_eps)
        self.lm_head = Linear(dim, vocab_size, bias=False)
        self.forward_jit = TinyJit(self.forward)

    def forward(
        self,
        tokens: Union[Tensor, Variable],
        start_pos: Variable,
        temperature: float = 0.0,
    ):
        if not hasattr(self, "allpos"):
            self.allpos = Tensor.arange(0, MAX_CONTEXT).reshape(1, -1).realize()
        if isinstance(tokens, Variable):
            seqlen = 1
            tok_emb = self.wte.weight.shrink(((tokens, tokens + 1), None))
        else:
            seqlen = tokens.shape[1]
            tok_emb = self.wte(tokens)

        pos_emb = self.wpe(self.allpos.shrink((None, (start_pos, start_pos + seqlen))))
        h = tok_emb + pos_emb

        mask = (
            Tensor.full((1, 1, seqlen, start_pos.val + seqlen), float("-inf"))
            .triu(start_pos.val + 1)
            .realize()
            if seqlen > 1
            else None
        )

        if HALF:
            h = h.half()
            if mask is not None:
                mask = mask.half()

        for hi in self.h:
            h = hi(h, start_pos=start_pos, mask=mask)

        logits = self.lm_head(self.ln_f(h))
        # NOTE: temperature=0 with HALF breaks due to precision, should use argmax instead
        ret = (logits[:, -1, :] / (temperature + 1e-10)).softmax()
        return ret.half().realize() if HALF else ret.realize()

    # TODO: fix empty token
    def __call__(
        self, tokens: Tensor, start_pos: Variable, temperature: float = 0.0
    ) -> Tensor:
        return (
            self.forward_jit
            if (isinstance(tokens, Variable) or tokens.shape[1] == 1) and getenv("JIT")
            else self.forward
        )(tokens, start_pos, temperature)


VOCAB_SIZE = 50257
MODEL_PARAMS = {
    "gpt2": dict(
        n_layers=12, n_heads=12, dim=768, norm_eps=1e-5, vocab_size=VOCAB_SIZE
    ),  # 124M params
    "gpt2-medium": dict(
        n_layers=24, n_heads=16, dim=1024, norm_eps=1e-5, vocab_size=VOCAB_SIZE
    ),  # 350M params
    "gpt2-large": dict(
        n_layers=36, n_heads=20, dim=1280, norm_eps=1e-5, vocab_size=VOCAB_SIZE
    ),  # 774M params
    "gpt2-xl": dict(
        n_layers=48, n_heads=25, dim=1600, norm_eps=1e-5, vocab_size=VOCAB_SIZE
    ),  # 1558M params
}


class GPT2:
    @staticmethod
    def build(model_size="gpt2"):
        tokenizer = tiktoken.get_encoding("gpt2")

        model = Transformer(**MODEL_PARAMS[model_size])
        weights = torch_load(
            fetch(f"https://huggingface.co/{model_size}/resolve/main/pytorch_model.bin")
        )
        # special treatment for the Conv1D weights we need to transpose
        transposed = [
            "attn.c_attn.weight",
            "attn.c_proj.weight",
            "mlp.c_fc.weight",
            "mlp.c_proj.weight",
        ]
        for k in weights.keys():
            if any(k.endswith(w) for w in transposed):
                weights[k] = weights[k].to(Device.DEFAULT).T
        # lm head and wte are tied
        weights["lm_head.weight"] = Tensor(weights["wte.weight"].numpy())

        load_state_dict(model, weights)
        return GPT2(model, tokenizer)

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def greedy_until(
        self,
        prompt: str,
        max_length: int,
        temperature: float,
        timing: bool = False,
        batch_size: int = 1,
    ):
        prompt_tokens = self.tokenizer.encode(prompt, allowed_special={"<|endoftext|>"})
        toks = [prompt_tokens[:] for _ in range(batch_size)]
        start_pos = 0
        for _ in trange(max_length, disable=(timing == True)):
            GlobalCounters.reset()
            if timing:
                print("")
            st = GlobalCounters.time_sum_s
            with Timing("total ", enabled=timing):
                with Timing(
                    "ran model in ",
                    on_exit=(
                        lambda et: (
                            f", {(GlobalCounters.time_sum_s-st)*1e3:.2f} ms on GPU"
                            if DEBUG >= 2
                            else ""
                        )
                        + f", {GlobalCounters.global_ops*1e-9:.2f} GOPS, {GlobalCounters.global_mem*1e-9:.2f} GB"
                        + (
                            f", {GlobalCounters.global_mem*1e-9/(GlobalCounters.time_sum_s-st):.2f} GB/s"
                            if DEBUG >= 2
                            else ""
                        )
                    )
                    if DEBUG
                    else None,
                    enabled=timing,
                ):
                    if batch_size == 1 and len(toks[0][start_pos:]) == 1:
                        tokens = Variable("tokens", 0, VOCAB_SIZE).bind(
                            toks[0][start_pos]
                        )
                    else:
                        tokens = Tensor([x[start_pos:] for x in toks])
                    probs = self.model(
                        tokens,
                        Variable("start_pos", 1 if start_pos else 0, MAX_CONTEXT).bind(
                            start_pos
                        ),
                        temperature,
                    )
                # TODO: fix JIT rand so we can put this in the JIT
                tok = probs.multinomial().flatten().numpy().tolist()
            start_pos = len(toks[0])
            for i, t in enumerate(tok):
                toks[i].append(t)
            output = [self.tokenizer.decode(x) for x in toks]
        return output


# **** main code ****

if __name__ == "__main__":
    Tensor.no_grad = True
    print(f"using {Device.DEFAULT} backend")
    default_prompt = "What is the answer to life, the universe, and everything?"

    parser = argparse.ArgumentParser(
        description="Run GPT2 in tinygrad",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--prompt", type=str, default=default_prompt, help="Phrase to start with"
    )
    parser.add_argument(
        "--count", type=int, default=100, help="Max number of tokens to generate"
    )
    parser.add_argument(
        "--temperature", type=float, default=0.8, help="Temperature in the softmax"
    )
    parser.add_argument(
        "--model_size",
        type=str,
        default="gpt2-medium",
        help="Size of model to use [gpt2, gpt2-medium, gpt2-large, gpt2-xl]",
    )
    parser.add_argument("--timing", action="store_true", help="Print timing per token")
    parser.add_argument("--seed", type=int, help="Set the random seed")
    parser.add_argument(
        "--batch_size", type=int, default=1, help="Set the input batch size"
    )
    parser.add_argument(
        "--benchmark",
        type=int,
        default=-1,
        help="Benchmark GPT with the given number of tokens",
    )
    parser.add_argument("--noshow", action="store_true", help="Don't show the output")
    args = parser.parse_args()

    if args.seed is not None:
        Tensor._seed = args.seed
        np.random.seed(args.seed)

    print(f"using {args.model_size}")
    gpt2 = GPT2.build(args.model_size)

    if HALF:
        for l in get_state_dict(gpt2).values():
            l.assign(l.half().realize())

    if args.benchmark != -1:
        gpt2.model(
            Tensor.rand(args.batch_size, args.benchmark),
            Variable("a", 0, MAX_CONTEXT).bind(0),
        ).realize()
    else:
        texts = gpt2.greedy_until(
            args.prompt,
            args.count,
            args.temperature,
            timing=args.timing,
            batch_size=args.batch_size,
        )
        if not args.noshow:
            print("Generating text...")
            if len(texts) == 1:
                print(texts[0])
            else:
                for i, text in enumerate(texts):
                    print(colored(f"Response {i}:", "green"), text)

        # validate output!
        if (
            args.temperature == 0
            and args.model_size == "gpt2-medium"
            and args.count == 10
        ):
            expected = {
                default_prompt: "What is the answer to life, the universe, and everything?\n\nThe answer is that we are all one",
                "Hello.": "Hello. I'm a little late to the party, but",
            }
            try:
                assert texts[0] == expected[args.prompt]
                print(colored("output validated", "green"))
            except KeyError:
                pass
