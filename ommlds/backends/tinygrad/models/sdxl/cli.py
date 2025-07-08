import argparse
import pathlib
import tempfile

import numpy as np
from PIL import Image
from tinygrad import Tensor
from tinygrad import dtypes
from tinygrad.helpers import colored
from tinygrad.helpers import fetch
from tinygrad.nn.state import load_state_dict
from tinygrad.nn.state import safe_load

from omlish import check

from .sdxl import Dpmpp2mSampler
from .sdxl import Sdxl


##


# configs:
# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/configs/inference/sd_xl_base.yaml
# https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/configs/inference/sd_xl_refiner.yaml
CONFIGS: dict = {
    'SDXL_Base': {
        'model': {
            'adm_in_ch': 2816,
            'in_ch': 4,
            'out_ch': 4,
            'model_ch': 320,
            'attention_resolutions': [4, 2],
            'num_res_blocks': 2,
            'channel_mult': [1, 2, 4],
            'd_head': 64,
            'transformer_depth': [1, 2, 10],
            'ctx_dim': 2048,
            'use_linear': True,
        },
        'conditioner': {
            'concat_embedders': [
                'original_size_as_tuple',
                'crop_coords_top_left',
                'target_size_as_tuple',
            ],
        },
        'first_stage_model': {
            'ch': 128,
            'in_ch': 3,
            'out_ch': 3,
            'z_ch': 4,
            'ch_mult': [1, 2, 4, 4],
            'num_res_blocks': 2,
            'resolution': 256,
        },
        'denoiser': {'num_idx': 1000},
    },
    'SDXL_Refiner': {
        'model': {
            'adm_in_ch': 2560,
            'in_ch': 4,
            'out_ch': 4,
            'model_ch': 384,
            'attention_resolutions': [4, 2],
            'num_res_blocks': 2,
            'channel_mult': [1, 2, 4, 4],
            'd_head': 64,
            'transformer_depth': [4, 4, 4, 4],
            'ctx_dim': [1280, 1280, 1280, 1280],
            'use_linear': True,
        },
        'conditioner': {
            'concat_embedders': [
                'original_size_as_tuple',
                'crop_coords_top_left',
                'aesthetic_score',
            ],
        },
        'first_stage_model': {
            'ch': 128,
            'in_ch': 3,
            'out_ch': 3,
            'z_ch': 4,
            'ch_mult': [1, 2, 4, 4],
            'num_res_blocks': 2,
            'resolution': 256,
        },
        'denoiser': {'num_idx': 1000},
    },
}


##


def _main() -> None:
    default_prompt = 'elon musk eating poop'
    parser = argparse.ArgumentParser(
        description='Run SDXL',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--steps',
        type=int,
        default=10,
        help='The number of diffusion steps',
    )
    parser.add_argument(
        '--prompt',
        type=str,
        default=default_prompt,
        help='Description of image to generate',
    )
    parser.add_argument(
        '--out',
        type=str,
        default=pathlib.Path(tempfile.gettempdir()) / 'rendered.png',
        help='Output filename',
    )
    parser.add_argument(
        '--seed',
        type=int,
        help='Set the random latent seed',
    )
    parser.add_argument(
        '--guidance',
        type=float,
        default=6.0,
        help='Prompt strength',
    )
    parser.add_argument(
        '--width',
        type=int,
        default=1024,
        help='The output image width',
    )
    parser.add_argument(
        '--height',
        type=int,
        default=1024,
        help='The output image height',
    )
    parser.add_argument(
        '--weights',
        type=str,
        help='Custom path to weights',
    )
    parser.add_argument(
        '--timing',
        action='store_true',
        help='Print timing per step',
    )
    parser.add_argument(
        '--noshow',
        action='store_true',
        help="Don't show the image",
    )
    args = parser.parse_args()

    if args.seed is not None:
        Tensor.manual_seed(args.seed)

    model = Sdxl(CONFIGS['SDXL_Base'])

    default_weight_url = (
        'https://huggingface.co/stabilityai/'
        'stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors'
    )
    weights = (
        args.weights
        if args.weights
        else fetch(default_weight_url, 'sd_xl_base_1.0.safetensors')
    )
    load_state_dict(model, safe_load(weights), strict=False)

    n = 1
    c_ = 4
    f_ = 8

    check.state(args.width % f_ == 0, f'img_width must be multiple of {f_}, got {args.width}')
    check.state(args.height % f_ == 0, f'img_height must be multiple of {f_}, got {args.height}')

    c, uc = model.create_conditioning([args.prompt], args.width, args.height)
    del model.conditioner
    for v in c.values():
        v.realize()
    for v in uc.values():
        v.realize()
    print('created batch')

    # https://github.com/Stability-AI/generative-models/blob/fbdc58cab9f4ee2be7a5e1f2e2787ecd9311942f/sgm/inference/helpers.py#L101
    shape = (n, c_, args.height // f_, args.width // f_)
    randn = Tensor.randn(shape)

    sampler = Dpmpp2mSampler(args.guidance)
    z = sampler(model.denoise, randn, c, uc, args.steps, timing=args.timing)
    print('created samples')
    x = model.decode(z).realize()
    print('decoded samples')

    # make image correct size and scale
    x = (x + 1.0) / 2.0
    x = (
        x
        .reshape(3, args.height, args.width)
        .permute(1, 2, 0)
        .clip(0, 1)
        .mul(255)
        .cast(dtypes.uint8)
    )
    print(x.shape)

    im = Image.fromarray(x.numpy())
    print(f'saving {args.out}')
    im.save(args.out)

    if not args.noshow:
        im.show()

    # validation!
    if (
            args.prompt == default_prompt
            and args.steps == 10
            and args.seed == 0
            and args.guidance == 6.0
            and args.width == args.height == 1024
            and not args.weights
    ):
        ref_image = Tensor(
            np.array(Image.open(pathlib.Path(__file__).parent / 'sdxl_seed0.png')),
        )
        distance = (
            (((x.cast(dtypes.float) - ref_image.cast(dtypes.float)) / ref_image.max()) ** 2)
            .mean()
            .item()
        )
        check.state(distance < 4e-3, f'validation failed with {distance=}')
        print(colored(f'output validated with {distance=}', 'green'))


if __name__ == '__main__':
    _main()
