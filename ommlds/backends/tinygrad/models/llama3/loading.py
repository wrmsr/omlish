import collections
import json
import os
import pathlib
import typing as ta

from tinygrad import Context
from tinygrad import Device
from tinygrad import Tensor
from tinygrad import dtypes
from tinygrad import nn
from tinygrad.helpers import getenv
from tinygrad.nn.state import gguf_load
from tinygrad.nn.state import load_state_dict
from tinygrad.nn.state import safe_load
from tinygrad.nn.state import torch_load

from .quantization import Int8Embedding
from .quantization import Int8Linear
from .quantization import nf4_linear
from .transformer import Transformer


##


# TODO: model shouldn't be an input here, and n_kv_heads should support None
def convert_from_huggingface(
        weights: dict[str, Tensor],
        model: Transformer,
        n_heads: int,
        n_kv_heads: int,
        permute_layers: bool = True,
):
    # huggingface stores Q and K permuted! it is mostly correct without this, but without it makes RoPE different, so it
    # will diverge after 10+ toks.
    def permute(v: Tensor, n_heads: int):
        return (
            v.reshape(
                n_heads,
                2,
                v.shape[0] // n_heads // 2,
                v.shape[1] if len(v.shape) > 1 else 1,
            )
            .transpose(1, 2)
            .reshape(*v.shape[:2])
        )

    keymap = {
        'model.embed_tokens.weight': 'tok_embeddings.weight',
        **{
            f'model.layers.{l}.input_layernorm.weight': f'layers.{l}.attention_norm.weight'
            for l in range(len(model.layers))
        },
        **{
            f'model.layers.{l}.self_attn.{x}_norm.weight': f'layers.{l}.attention.{x}_norm.weight'
            for x in ['q', 'k']
            for l in range(len(model.layers))
        },
        **{
            f'model.layers.{l}.self_attn.{x}_proj.weight': f'layers.{l}.attention.w{x}.weight'
            for x in ['q', 'k', 'v', 'o']
            for l in range(len(model.layers))
        },
        **{
            f'model.layers.{l}.self_attn.{x}_proj.bias': f'layers.{l}.attention.w{x}.bias'
            for x in ['q', 'k', 'v', 'o']
            for l in range(len(model.layers))
        },
        **{
            f'model.layers.{l}.post_attention_layernorm.weight': f'layers.{l}.ffn_norm.weight'
            for l in range(len(model.layers))
        },
        **{
            f'model.layers.{l}.mlp.{x}_proj.weight': f'layers.{l}.feed_forward.w{y}.weight'
            for x, y in {'gate': '1', 'down': '2', 'up': '3'}.items()
            for l in range(len(model.layers))
        },
        **{
            f'model.layers.{l}.mlp.gate.weight': f'layers.{l}.feed_forward.gate.weight'
            for l in range(len(model.layers))
        },
        'model.norm.weight': 'norm.weight',
        'lm_head.weight': 'output.weight',
    }
    sd = {}
    experts: dict = collections.defaultdict(dict)
    for k, v in weights.items():
        if '.rotary_emb.' in k:
            continue
        v = v.to(Device.DEFAULT)
        if 'model.layers' in k:
            if ('q_proj' in k or 'q_norm' in k) and permute_layers:
                v = permute(v, n_heads)
            elif ('k_proj' in k or 'k_norm' in k) and permute_layers:
                v = permute(v, n_kv_heads)
        if '.mlp.experts.' in k:
            # support MoE models
            _, _, layer, _, _, expert, name, _ = k.split('.')
            experts[f'layers.{layer}.feed_forward.{name}'][int(expert)] = v
            continue
        sd[keymap[k]] = v
    for k, v in experts.items():
        sd[k] = Tensor.stack(*[v[i] for i in range(len(v))])
    return sd


def convert_from_gguf(
        weights: dict[str, Tensor],
        model: Transformer,
):
    keymap = {
        'token_embd.weight': 'tok_embeddings.weight',
        **{
            f'blk.{l}.attn_norm.weight': f'layers.{l}.attention_norm.weight'
            for l in range(len(model.layers))
        },
        **{
            f'blk.{l}.attn_{x}.weight': f'layers.{l}.attention.w{x}.weight'
            for x in ['q', 'k', 'v']
            for l in range(len(model.layers))
        },
        **{
            f'blk.{l}.attn_output.weight': f'layers.{l}.attention.wo.weight'
            for l in range(len(model.layers))
        },
        **{
            f'blk.{l}.ffn_norm.weight': f'layers.{l}.ffn_norm.weight'
            for l in range(len(model.layers))
        },
        **{
            f'blk.{l}.ffn_{x}.weight': f'layers.{l}.feed_forward.w{y}.weight'
            for x, y in {'gate': '1', 'down': '2', 'up': '3'}.items()
            for l in range(len(model.layers))
        },
        'output_norm.weight': 'norm.weight',
        'rope_freqs.weight': 'rope_freqs.weight',
    }
    sd = {keymap[k]: v for k, v in weights.items()}
    sd['output.weight'] = weights['token_embd.weight']
    return sd


def fix_bf16(weights: dict[ta.Any, Tensor]):
    if getenv('SUPPORT_BF16', 1):
        # TODO: without casting to float16, 70B llama OOM on tinybox.
        return {
            k: (
                v.cast(dtypes.float32).cast(dtypes.float16)
                if v.dtype == dtypes.bfloat16
                else v
            )
            for k, v in weights.items()
        }

    # TODO: check if device supports bf16
    return {
        k: (
            v.llvm_bf16_cast(dtypes.half).to(v.device)
            if v.dtype == dtypes.bfloat16
            else v
        )
        for k, v in weights.items()
    }


def concat_weights(models, device=None):
    def convert(name) -> Tensor:
        disk_tensors: list[Tensor] = [model[name] for model in models]
        if len(disk_tensors) == 1 or len(disk_tensors[0].shape) == 1:
            return disk_tensors[0].to(device=device)
        axis = (
            1
            if name.endswith(('.attention.wo.weight', '.feed_forward.w2.weight'))
            else 0
        )
        lazy_tensors = [data.to(device=device) for data in disk_tensors]
        return lazy_tensors[0].cat(*lazy_tensors[1:], dim=axis)

    return {
        name: convert(name)
        for name in {name: None for model in models for name in model}
    }


def load(fn: str):
    if fn.endswith('.index.json'):
        with open(fn) as fp:
            weight_map = json.load(fp)['weight_map']
        parts = {
            n: load(str(pathlib.Path(fn).parent / pathlib.Path(n).name))
            for n in set(weight_map.values())
        }
        return {k: parts[n][k] for k, n in weight_map.items()}

    elif fn.endswith('.gguf'):
        gguf_tensor = Tensor.empty(
            os.stat(fn).st_size, dtype=dtypes.uint8, device=f'disk:{fn}',
        ).to(Device.DEFAULT)
        return gguf_load(gguf_tensor)[1]

    elif fn.endswith('.safetensors'):
        return safe_load(fn)

    else:
        return torch_load(fn)


MODEL_PARAMS: ta.Any = {
    '1B': {
        'args': {
            'dim': 2048,
            'n_heads': 32,
            'n_kv_heads': 8,
            'n_layers': 16,
            'norm_eps': 1e-5,
            'rope_theta': 500000,
            'vocab_size': 128256,
            'hidden_dim': 8192,
        },
        'files': 1,
    },
    '8B': {
        'args': {
            'dim': 4096,
            'n_heads': 32,
            'n_kv_heads': 8,
            'n_layers': 32,
            'norm_eps': 1e-5,
            'rope_theta': 500000,
            'vocab_size': 128256,
            'hidden_dim': 14336,
        },
        'files': 1,
    },
    '70B': {
        'args': {
            'dim': 8192,
            'n_heads': 64,
            'n_kv_heads': 8,
            'n_layers': 80,
            'norm_eps': 1e-5,
            'rope_theta': 500000,
            'vocab_size': 128256,
            'hidden_dim': 28672,
        },
        'files': 8,
    },
}


def build_transformer(
    model_path: pathlib.Path,
    model_size='8B',
    quantize=None,
    scale_dtype=dtypes.float16,
    device=None,
    max_context=8192,
    load_weights=True,
):
    # build model
    linear: ta.Any
    embedding: ta.Any
    quantize_embeds: ta.Any
    if quantize == 'int8':
        linear, embedding, quantize_embeds = Int8Linear, Int8Embedding, True
    elif quantize == 'nf4':
        linear, embedding, quantize_embeds = nf4_linear(64), nn.Embedding, False
    else:
        linear, embedding, quantize_embeds = nn.Linear, nn.Embedding, False

    model = Transformer(
        **MODEL_PARAMS[model_size]['args'],
        linear=linear,
        embedding=embedding,
        max_context=max_context,
        jit=True,
    )

    if not load_weights:
        return model

    # load weights
    if model_path.is_dir():
        if (model_path / 'model.safetensors.index.json').exists():
            weights = load(str(model_path / 'model.safetensors.index.json'))

        elif (model_path / 'model.safetensors').exists():
            weights = load(str(model_path / 'model.safetensors'))

        else:
            weights = concat_weights(
                [
                    load(str(model_path / f'consolidated.{i:02d}.pth'))
                    for i in range(MODEL_PARAMS[model_size]['files'])
                ],
                device[0] if isinstance(device, tuple) else device,
            )

    else:
        weights = load(str(model_path))

    if 'model.embed_tokens.weight' in weights:
        weights = convert_from_huggingface(
            weights,
            model,
            MODEL_PARAMS[model_size]['args']['n_heads'],
            MODEL_PARAMS[model_size]['args']['n_kv_heads'],
        )

    elif 'token_embd.weight' in weights:
        weights = convert_from_gguf(weights, model)

    weights = fix_bf16(weights)

    with Context(BEAM=0):
        # quantize
        if quantize == 'float16':
            weights = {k: v.cast(quantize).contiguous() for k, v in weights.items()}

        elif quantize is not None:
            weights = linear.quantize(weights, device, scale_dtype, quantize_embeds)
            for v in weights:
                v.realize()

        # shard
        if isinstance(device, tuple):
            for k, v in nn.state.get_state_dict(model).items():
                if 'scale' in k:
                    v.shard_(device, axis=None)  # from quantized
                elif '.attention.' in k:
                    v.shard_(device, axis=-1)
                elif '.feed_forward.w1.' in k:
                    v.shard_(device, axis=0)
                elif '.feed_forward.w3.' in k:
                    v.shard_(device, axis=0)
                elif '.feed_forward.' in k:
                    v.shard_(device, axis=-1)
                elif 'tok_embeddings.weight' in k:
                    v.shard_(device, axis=0)
                elif 'output.weight' in k:
                    v.shard_(device, axis=0)
                else:
                    v.shard_(device, axis=None)

        # replace weights in model
        load_state_dict(model, weights, strict=False, consume=True)

    return model
