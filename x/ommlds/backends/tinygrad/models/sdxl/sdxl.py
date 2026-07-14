"""
This file incorporates code from the following:
 - Github Name                    | License | Link
 - Stability-AI/generative-models | MIT     | https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/LICENSE-CODE
 - mlfoundations/open_clip        | MIT     | https://github.com/mlfoundations/open_clip/blob/58e4e39aaabc6040839b0d2a7e8bf20979e4558a/LICENSE
"""  # noqa
####
# Stability-AI/generative-models
# MIT License
#
# Copyright (c) 2023 Stability AI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
####
# mlfoundations/open_clip
#
# Copyright (c) 2012-2021 Gabriel Ilharco, Mitchell Wortsman, Nicholas Carlini, Rohan Taori, Achal Dave, Vaishaal
# Shankar, John Miller, Hongseok Namkoong, Hannaneh Hajishirzi, Ali Farhadi, Ludwig Schmidt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import abc
import dataclasses as dc
import typing as ta

import numpy as np
from tinygrad import GlobalCounters
from tinygrad import Tensor
from tinygrad import TinyJit
from tinygrad import dtypes
from tinygrad.helpers import Timing
from tinygrad.helpers import trange
from tinygrad.nn import Conv2d
from tinygrad.nn import GroupNorm

from omlish import check
from omlish import lang

from .clip import Embedder
from .clip import FrozenClosedClipEmbedder
from .clip import FrozenOpenClipEmbedder
from .unet import Downsample
from .unet import UnetModel
from .unet import Upsample
from .unet import timestep_embedding


##


class AttnBlock:
    def __init__(self, in_channels) -> None:
        super().__init__()

        self.norm = GroupNorm(32, in_channels)
        self.q = Conv2d(in_channels, in_channels, 1)
        self.k = Conv2d(in_channels, in_channels, 1)
        self.v = Conv2d(in_channels, in_channels, 1)
        self.proj_out = Conv2d(in_channels, in_channels, 1)

    # copied from AttnBlock in ldm repo
    def __call__(self, x):
        h_ = self.norm(x)
        q, k, v = self.q(h_), self.k(h_), self.v(h_)

        # compute attention
        b, c, h, w = q.shape
        q, k, v = [x.reshape(b, c, h * w).transpose(1, 2) for x in (q, k, v)]
        h_ = (
            Tensor.scaled_dot_product_attention(q, k, v)
            .transpose(1, 2)
            .reshape(b, c, h, w)
        )
        return x + self.proj_out(h_)


class ResnetBlock:
    def __init__(self, in_channels, out_channels=None) -> None:
        super().__init__()

        self.norm1 = GroupNorm(32, in_channels)
        self.conv1 = Conv2d(in_channels, out_channels, 3, padding=1)
        self.norm2 = GroupNorm(32, out_channels)
        self.conv2 = Conv2d(out_channels, out_channels, 3, padding=1)
        self.nin_shortcut = (
            Conv2d(in_channels, out_channels, 1)
            if in_channels != out_channels
            else lambda x: x
        )

    def __call__(self, x):
        h = self.conv1(self.norm1(x).swish())
        h = self.conv2(self.norm2(h).swish())
        return self.nin_shortcut(x) + h


class Mid:
    def __init__(self, block_in) -> None:
        super().__init__()

        self.block_1 = ResnetBlock(block_in, block_in)
        self.attn_1 = AttnBlock(block_in)
        self.block_2 = ResnetBlock(block_in, block_in)

    def __call__(self, x):
        return x.sequential([self.block_1, self.attn_1, self.block_2])


##


class DiffusionModel:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

        self.diffusion_model = UnetModel(*args, **kwargs)


##


# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/modules/encoders/modules.py#L913
class ConcatTimestepEmbedderNd(Embedder):
    def __init__(self, outdim: int, input_key: str) -> None:
        super().__init__()

        self.outdim = outdim
        self.input_key = input_key

    def __call__(self, x: str | list[str] | Tensor):
        x = ta.cast(Tensor, check.isinstance(x, Tensor))
        check.state(len(x.shape) == 2)
        emb = timestep_embedding(x.flatten(), self.outdim)
        emb = emb.reshape((x.shape[0], -1))
        return emb


# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/modules/encoders/modules.py#L71
class Conditioner:
    OUTPUT_DIM2KEYS: ta.ClassVar[ta.Mapping[int, str]] = {
        2: 'vector',
        3: 'crossattn',
        4: 'concat',
        5: 'concat',
    }

    KEY2CATDIM: ta.ClassVar[ta.Mapping[str, int]] = {
        'vector': 1,
        'crossattn': 2,
        'concat': 1,
    }

    embedders: list[Embedder]

    def __init__(self, concat_embedders: list[str]) -> None:
        super().__init__()

        self.embedders = [
            FrozenClosedClipEmbedder(ret_layer_idx=11),
            FrozenOpenClipEmbedder(
                dims=1280,
                n_heads=20,
                layers=32,
                return_pooled=True,
            ),
        ]
        for input_key in concat_embedders:
            self.embedders.append(ConcatTimestepEmbedderNd(256, input_key))

    def get_keys(self) -> set[str]:
        return {e.input_key for e in self.embedders}

    def __call__(
            self,
            batch: dict,
            force_zero_embeddings: list | None = None,
    ) -> dict[str, Tensor]:
        output: dict[str, Tensor] = {}

        for embedder in self.embedders:
            emb_out = embedder(batch[embedder.input_key])

            if isinstance(emb_out, Tensor):
                emb_out = (emb_out,)
            check.state(isinstance(emb_out, (list, tuple)))

            for emb in emb_out:
                if embedder.input_key in (force_zero_embeddings or []):
                    emb = Tensor.zeros_like(emb)

                out_key = self.OUTPUT_DIM2KEYS[len(emb.shape)]
                if out_key in output:
                    output[out_key] = Tensor.cat(
                        output[out_key],
                        emb,
                        dim=self.KEY2CATDIM[out_key],
                    )
                else:
                    output[out_key] = emb

        return output


##


def tensor_identity(x: Tensor) -> Tensor:
    return x


class FirstStage:
    """Namespace for First Stage Model components"""

    # https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/modules/diffusionmodules/model.py#L487
    class Encoder:
        class BlockEntry:
            def __init__(self, block: list[ResnetBlock], downsample) -> None:
                super().__init__()

                self.block = block
                self.downsample = downsample

        def __init__(
            self,
            ch: int,
            in_ch: int,
            out_ch: int,
            z_ch: int,
            ch_mult: list[int],
            num_res_blocks: int,
            resolution: int,
        ) -> None:
            super().__init__()

            self.conv_in = Conv2d(in_ch, ch, kernel_size=3, stride=1, padding=1)
            in_ch_mult = (1, *ch_mult)

            self.down: list[FirstStage.Encoder.BlockEntry] = []
            for i_level in range(len(ch_mult)):
                block = []
                block_in = ch * in_ch_mult[i_level]
                block_out = ch * ch_mult[i_level]
                for _ in range(num_res_blocks):
                    block.append(ResnetBlock(block_in, block_out))
                    block_in = block_out

                downsample = (
                    tensor_identity
                    if (i_level == len(ch_mult) - 1)
                    else Downsample(block_in)
                )
                self.down.append(FirstStage.Encoder.BlockEntry(block, downsample))

            self.mid = Mid(block_in)

            self.norm_out = GroupNorm(32, block_in)
            self.conv_out = Conv2d(
                block_in, 2 * z_ch, kernel_size=3, stride=1, padding=1,
            )

        def __call__(self, x: Tensor) -> Tensor:
            h = self.conv_in(x)
            for down in self.down:
                for block in down.block:
                    h = block(h)
                h = down.downsample(h)

            h = h.sequential([self.mid.block_1, self.mid.attn_1, self.mid.block_2])
            h = h.sequential([self.norm_out, Tensor.swish, self.conv_out])
            return h

    # https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/modules/diffusionmodules/model.py#L604
    class Decoder:
        @dc.dataclass()
        class BlockEntry:
            block: list[ResnetBlock]
            upsample: ta.Callable[[ta.Any], ta.Any]

        def __init__(
            self,
            ch: int,
            in_ch: int,
            out_ch: int,
            z_ch: int,
            ch_mult: list[int],
            num_res_blocks: int,
            resolution: int,
        ) -> None:
            super().__init__()

            block_in = ch * ch_mult[-1]
            curr_res = resolution // 2 ** (len(ch_mult) - 1)
            self.z_shape = (1, z_ch, curr_res, curr_res)

            self.conv_in = Conv2d(z_ch, block_in, kernel_size=3, stride=1, padding=1)

            self.mid = Mid(block_in)

            self.up: list[FirstStage.Decoder.BlockEntry] = []
            for i_level in reversed(range(len(ch_mult))):
                block = []
                block_out = ch * ch_mult[i_level]
                for _ in range(num_res_blocks + 1):
                    block.append(ResnetBlock(block_in, block_out))
                    block_in = block_out

                upsample = tensor_identity if i_level == 0 else Upsample(block_in)
                self.up.insert(0, self.BlockEntry(block, upsample))

            self.norm_out = GroupNorm(32, block_in)
            self.conv_out = Conv2d(block_in, out_ch, kernel_size=3, stride=1, padding=1)

        def __call__(self, z: Tensor) -> Tensor:
            h = z.sequential(
                [self.conv_in, self.mid.block_1, self.mid.attn_1, self.mid.block_2],
            )

            for up in self.up[::-1]:
                for block in up.block:
                    h = block(h)
                h = up.upsample(h)

            h = h.sequential([self.norm_out, Tensor.swish, self.conv_out])
            return h


# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/models/autoencoder.py#L102
# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/models/autoencoder.py#L437
# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/models/autoencoder.py#L508
class FirstStageModel:
    def __init__(self, embed_dim: int = 4, **kwargs) -> None:
        super().__init__()

        self.encoder = FirstStage.Encoder(**kwargs)
        self.decoder = FirstStage.Decoder(**kwargs)
        self.quant_conv = Conv2d(2 * kwargs['z_ch'], 2 * embed_dim, 1)
        self.post_quant_conv = Conv2d(embed_dim, kwargs['z_ch'], 1)

    def decode(self, z: Tensor) -> Tensor:
        return z.sequential([self.post_quant_conv, self.decoder])


##


# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/modules/diffusionmodules/discretizer.py#L42
class LegacyDdpmDiscretization:
    def __init__(
        self,
        linear_start: float = 0.00085,
        linear_end: float = 0.0120,
        num_timesteps: int = 1000,
    ) -> None:
        super().__init__()

        self.num_timesteps = num_timesteps
        betas = (
            np.linspace(
                linear_start**0.5, linear_end**0.5, num_timesteps, dtype=np.float32,
            )
            ** 2
        )
        alphas = 1.0 - betas
        self.alphas_cumprod = np.cumprod(alphas, axis=0)

    def __call__(self, n: int, flip: bool = False) -> Tensor:
        if n < self.num_timesteps:
            timesteps = np.linspace(
                self.num_timesteps - 1, 0, n, endpoint=False,
            ).astype(int)[::-1]
            alphas_cumprod = self.alphas_cumprod[timesteps]
        elif n == self.num_timesteps:
            alphas_cumprod = self.alphas_cumprod
        sigmas = Tensor((1 - alphas_cumprod) / alphas_cumprod) ** 0.5
        sigmas = Tensor.cat(Tensor.zeros((1,)), sigmas)
        return (
            sigmas if flip else sigmas.flip(axis=0)
        )  # sigmas is "pre-flipped", need to do oposite of flag


##


def append_dims(x: Tensor, t: Tensor) -> Tensor:
    dims_to_append = len(t.shape) - len(x.shape)
    check.state(dims_to_append >= 0)
    return x.reshape(x.shape + (1,) * dims_to_append)


@TinyJit
def run(model, x, tms, ctx, y, c_out, add):
    return (model(x, tms, ctx, y) * c_out + add).realize()


# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/models/diffusion.py#L19
class Sdxl:
    def __init__(self, config: dict) -> None:
        super().__init__()

        self.conditioner = Conditioner(**config['conditioner'])
        self.first_stage_model = FirstStageModel(**config['first_stage_model'])
        self.model = DiffusionModel(**config['model'])

        self.discretization = LegacyDdpmDiscretization()
        self.sigmas = self.discretization(config['denoiser']['num_idx'], flip=True)

    # https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/inference/helpers.py#L173
    def create_conditioning(
        self,
        pos_prompts: list[str],
        img_width: int,
        img_height: int,
        aesthetic_score: float = 5.0,
    ) -> tuple[dict, dict]:
        n = len(pos_prompts)
        batch_c: dict = {
            'txt': pos_prompts,
            'original_size_as_tuple': Tensor([img_height, img_width]).repeat(n, 1),
            'crop_coords_top_left': Tensor([0, 0]).repeat(n, 1),
            'target_size_as_tuple': Tensor([img_height, img_width]).repeat(n, 1),
            'aesthetic_score': Tensor([aesthetic_score]).repeat(n, 1),
        }
        batch_uc: dict = {
            'txt': [''] * n,
            'original_size_as_tuple': Tensor([img_height, img_width]).repeat(n, 1),
            'crop_coords_top_left': Tensor([0, 0]).repeat(n, 1),
            'target_size_as_tuple': Tensor([img_height, img_width]).repeat(n, 1),
            'aesthetic_score': Tensor([aesthetic_score]).repeat(n, 1),
        }
        return self.conditioner(batch_c), self.conditioner(
            batch_uc, force_zero_embeddings=['txt'],
        )

    # https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/modules/diffusionmodules/denoiser.py#L42
    def denoise(self, x: Tensor, sigma: Tensor, cond: dict) -> Tensor:
        def sigma_to_idx(s: Tensor) -> Tensor:
            dists = s - self.sigmas.unsqueeze(1)
            return dists.abs().argmin(axis=0).view(*s.shape)

        sigma = self.sigmas[sigma_to_idx(sigma)]
        sigma_shape = sigma.shape
        sigma = append_dims(sigma, x)

        c_out = -sigma
        c_in = 1 / (sigma**2 + 1.0) ** 0.5
        c_noise = sigma_to_idx(sigma.reshape(sigma_shape))

        def prep(*tensors: Tensor):
            return tuple(t.cast(dtypes.float16).realize() for t in tensors)

        return run(
            self.model.diffusion_model,
            *prep(x * c_in, c_noise, cond['crossattn'], cond['vector'], c_out, x),
        )

    def decode(self, x: Tensor) -> Tensor:
        return self.first_stage_model.decode(1.0 / 0.13025 * x)


##


class Guider(lang.Abstract):
    def __init__(self, scale: float) -> None:
        super().__init__()

        self.scale = scale

    @abc.abstractmethod
    def __call__(self, denoiser, x: Tensor, s: Tensor, c: dict, uc: dict) -> Tensor:
        pass


class VanillaCfg(Guider):
    def __call__(self, denoiser, x: Tensor, s: Tensor, c: dict, uc: dict) -> Tensor:
        c_out = {}
        for k in c:
            check.state(k in ['vector', 'crossattn', 'concat'])
            c_out[k] = Tensor.cat(uc[k], c[k], dim=0)

        x_u, x_c = denoiser(Tensor.cat(x, x), Tensor.cat(s, s), c_out).chunk(2)
        x_pred = x_u + self.scale * (x_c - x_u)
        return x_pred


class SplitVanillaCfg(Guider):
    def __call__(self, denoiser, x: Tensor, s: Tensor, c: dict, uc: dict) -> Tensor:
        x_u = denoiser(x, s, uc).clone().realize()
        x_c = denoiser(x, s, c)
        x_pred = x_u + self.scale * (x_c - x_u)
        return x_pred


#


# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/modules/diffusionmodules/sampling.py#L21
# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/modules/diffusionmodules/sampling.py#L287
class Dpmpp2mSampler:
    def __init__(self, cfg_scale: float, guider_cls: type[Guider] = VanillaCfg) -> None:
        super().__init__()

        self.discretization = LegacyDdpmDiscretization()
        self.guider = guider_cls(cfg_scale)

    def sampler_step(
        self,
        old_denoised: Tensor | None,
        prev_sigma: Tensor | None,
        sigma: Tensor,
        next_sigma: Tensor,
        denoiser,
        x: Tensor,
        c: dict,
        uc: dict,
    ) -> tuple[Tensor, Tensor]:
        denoised = self.guider(denoiser, x, sigma, c, uc)

        t, t_next = sigma.log().neg(), next_sigma.log().neg()
        h = t_next - t
        r = None if prev_sigma is None else (t - prev_sigma.log().neg()) / h

        mults = [t_next.neg().exp() / t.neg().exp(), (-h).exp().sub(1)]
        if r is not None:
            mults.extend([1 + 1 / (2 * r), 1 / (2 * r)])
        mults = [append_dims(m, x) for m in mults]

        x_standard = mults[0] * x - mults[1] * denoised
        if (old_denoised is None) or (next_sigma.sum().numpy().item() < 1e-14):
            return x_standard, denoised

        denoised_d = mults[2] * denoised - mults[3] * old_denoised
        x_advanced = mults[0] * x - mults[1] * denoised_d
        x = Tensor.where(append_dims(next_sigma, x) > 0.0, x_advanced, x_standard)
        return x, denoised

    def __call__(
            self,
            denoiser,
            x: Tensor,
            c: dict,
            uc: dict,
            num_steps: int,
            timing=False,
    ) -> Tensor:
        sigmas = self.discretization(num_steps).to(x.device)
        x *= Tensor.sqrt(1.0 + sigmas[0] ** 2.0)
        num_sigmas = len(sigmas)

        old_denoised = None
        for i in trange(num_sigmas - 1):
            with Timing(
                'step in ',
                enabled=timing,
                on_exit=lambda _: f', using {GlobalCounters.mem_used / 1e9:.2f} GB',
            ):
                GlobalCounters.reset()
                x, old_denoised = self.sampler_step(
                    old_denoised=old_denoised,
                    prev_sigma=(None if i == 0 else sigmas[i - 1].expand(x.shape[0])),
                    sigma=sigmas[i].expand(x.shape[0]),
                    next_sigma=sigmas[i + 1].expand(x.shape[0]),
                    denoiser=denoiser,
                    x=x,
                    c=c,
                    uc=uc,
                )
                x.realize()
                old_denoised.realize()

        return x
