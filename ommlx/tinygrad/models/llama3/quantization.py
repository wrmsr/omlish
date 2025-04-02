from omlish import check
from tinygrad import Tensor
from tinygrad import dtypes


##


class Int8Linear:
    def __init__(
            self,
            in_features,
            out_features,
            bias=False,
    ):
        super().__init__()

        check.arg(not bias)
        self.weight = Tensor.ones(out_features, in_features, dtype=dtypes.int8)
        self.scale = Tensor.ones(out_features, dtype=dtypes.half)

    def __call__(self, x):
        return x.dot(self.weight.cast(self.scale.dtype).T * self.scale)

    @staticmethod
    def quantize(
            tensors,
            device,
            scale_dtype=dtypes.float16,
            quantize_embeds=False,
    ):
        new_tensors = {}
        for name, v in tensors.items():
            if (
                    'feed_forward' in name
                    or 'attention.w' in name
                    or (quantize_embeds and 'tok_embeddings.weight' in name)
            ):
                check.in_('weight', name)
                v = v.cast(scale_dtype)
                scale = v.abs().max(axis=1) / 127.0
                int8_weight = (
                    (v.T / scale).T.round().cast(dtype=dtypes.int8)
                )  # without round(), cast truncates -34.9 to -34
                new_tensors[name] = int8_weight
                new_tensors[name.replace('weight', 'scale')] = scale
                if isinstance(device, tuple):
                    new_tensors[name].shard_(device, axis=-1)
                    new_tensors[name.replace('weight', 'scale')].shard_(device, axis=None)

            else:
                new_tensors[name] = v

        if quantize_embeds:
            new_tensors.update({
                'output.weight': new_tensors['tok_embeddings.weight'],
                'output.scale': new_tensors['tok_embeddings.scale'],
            })

        return new_tensors


class Int8Embedding:
    def __init__(self, vocab_size: int, embed_size: int):
        super().__init__()

        self.vocab_sz, self.embed_sz = vocab_size, embed_size
        self.weight, self.scale = Tensor.ones(
            vocab_size, embed_size, dtype=dtypes.int8,
        ), Tensor.ones(vocab_size, dtype=dtypes.half)

    def __call__(self, idx: Tensor) -> Tensor:
        if not hasattr(self, 'arange'):
            self.arange = Tensor.arange(
                self.vocab_sz, requires_grad=False, device=self.weight.device,
            ).unsqueeze(-1)
        big_shp = (*idx.shape, self.vocab_sz, self.embed_sz)
        arange, idx, vals = (
            self.arange.expand(big_shp),
            idx.reshape((*idx.shape, 1, 1)).expand(big_shp),
            (self.weight.cast(self.scale.dtype).T * self.scale).T,
        )
        return (arange == idx).mul(vals).sum(-2, dtype=vals.dtype)


def nf4_linear(block_size):
    _code = [
        -1.0,
        -0.6961928009986877,
        -0.5250730514526367,
        -0.39491748809814453,
        -0.28444138169288635,
        -0.18477343022823334,
        -0.09105003625154495,
        0.0,
        0.07958029955625534,
        0.16093020141124725,
        0.24611230194568634,
        0.33791524171829224,
        0.44070982933044434,
        0.5626170039176941,
        0.7229568362236023,
        1.0,
    ]

    code = Tensor.stack(*[Tensor(c, dtype=dtypes.float16) for c in _code])

    class _Nf4Linear:
        def __init__(
                self,
                in_features,
                out_features,
                bias=False,
        ):
            super().__init__()

            check.arg(not bias, 'bias not supported')
            self.in_features, self.out_features = in_features, out_features
            self.weight = Tensor.empty(int(out_features * in_features / 2), dtype=dtypes.uint8)
            self.scale = Tensor.empty(int(out_features * in_features / block_size), 1, dtype=dtypes.float16)

        def __call__(self, x: Tensor) -> Tensor:
            high_bits = self.weight
            low_bits = (self.weight * 2**4).contiguous()
            unpacked = Tensor.stack(high_bits, low_bits, dim=-1).idiv(2**4)
            unscaled = code[unpacked].to(x.device).reshape(-1, block_size) * self.scale
            return x.linear(unscaled.reshape(self.out_features, self.in_features).T)

        @staticmethod
        def quantize(
                state_dict: dict[str, Tensor],
                device,
                scale_dtype=dtypes.float16,
        ) -> dict[str, Tensor]:
            new_state_dict = {}
            for k, v in state_dict.items():
                if 'feed_forward' in k or 'attention.w' in k:
                    grouped = v.reshape(-1, block_size)
                    scale = grouped.abs().max(axis=1, keepdim=True)
                    coded = (
                        ((grouped / scale).unsqueeze(-1) - code.to(v.device))
                        .abs()
                        .argmin(axis=-1)
                        .cast(dtypes.uint8)
                        .flatten()
                    )
                    new_state_dict[k] = coded[::2] * 2**4 + coded[1::2]
                    new_state_dict[k.replace('.weight', '.scale')] = scale.cast(scale_dtype)
                    if isinstance(device, tuple):
                        new_state_dict[k].shard_(device, axis=-1)
                        new_state_dict[k.replace('weight', 'scale')].shard_(device, axis=None)

                else:
                    new_state_dict[k] = v

            return new_state_dict

    return _Nf4Linear
