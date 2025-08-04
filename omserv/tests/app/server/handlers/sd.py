# Copyright (c) 2024, the tiny corp
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
# https://github.com/tinygrad/tinygrad/blob/2fe9d62451a76b75e2b54f300f6de1c6dbef2762/examples/stable_diffusion.py
import dataclasses as dc
import functools
import io
import logging
import typing as ta

import anyio.to_thread
import httpx

from omlish import lang
from omlish.formats import json
from omlish.http import all as hu
from omlish.http import asgi
from omlish.secrets import all as sec

from .....apps.routes import Route
from .....apps.routes import RouteHandlerHolder
from .....apps.routes import handles


# fmt: off

if ta.TYPE_CHECKING:
    import numpy as np  # noqa

    import tinygrad as tg
    import tinygrad.helpers as tg_helpers
    import tinygrad.nn as tg_nn
    import tinygrad.tensor as tg_tensor

    from examples import stable_diffusion as sd
    from PIL import Image as pi  # noqa

else:
    np = lang.proxy_import('numpy')

    tg = lang.proxy_import('tinygrad')
    tg_helpers = lang.proxy_import('tinygrad.helpers')
    tg_nn = lang.proxy_import('tinygrad.nn')
    tg_tensor = lang.proxy_import('tinygrad.tensor')

    sd = lang.proxy_import('examples.stable_diffusion')
    pi = lang.proxy_import('PIL.Image')

# fmt: on


log = logging.getLogger(__name__)


##


@dc.dataclass(frozen=True)
class SdArgs:
    prompt: str
    steps: int = 5
    seed: int | None = None
    guidance: float = 7.5


def run_sd(args: SdArgs) -> bytes:
    tg_tensor.Tensor.no_grad = True
    model = sd.StableDiffusion()

    # load in weights
    weights_url = 'https://huggingface.co/CompVis/stable-diffusion-v-1-4-original/resolve/main/sd-v1-4.ckpt'
    fetched_weights = tg_helpers.fetch(weights_url, 'sd-v1-4.ckpt')
    fw: dict[str, ta.Any] = tg_nn.state.torch_load(str(fetched_weights))
    tg_nn.state.load_state_dict(model, fw['state_dict'], strict=False)

    # run through CLIP to get context
    tokenizer = sd.Tokenizer.ClipTokenizer()
    prompt = tg_tensor.Tensor([tokenizer.encode(args.prompt)])
    context = model.cond_stage_model.transformer.text_model(prompt).realize()
    log.info('Got CLIP context: %r', context.shape)

    prompt = tg_tensor.Tensor([tokenizer.encode('')])
    unconditional_context = model.cond_stage_model.transformer.text_model(prompt).realize()
    log.info('Got unconditional CLIP context: %r', unconditional_context.shape)

    # done with clip model
    del model.cond_stage_model

    timesteps = list(range(1, 1000, 1000 // args.steps))
    log.info('Running for timesteps %r', timesteps)
    alphas = model.alphas_cumprod[tg_tensor.Tensor(timesteps)]
    alphas_prev = tg_tensor.Tensor([1.0]).cat(alphas[:-1])

    # start with random noise
    if args.seed is not None:
        tg_tensor.Tensor.manual_seed(args.seed)
    latent = tg_tensor.Tensor.randn(1, 4, 64, 64)

    @tg.TinyJit
    def run(model, *x):
        return model(*x).realize()

    # this is diffusion
    for index, timestep in list(enumerate(timesteps))[::-1]:
        tid = tg_tensor.Tensor([index])
        latent = run(
            model,
            unconditional_context,
            context,
            latent,
            tg_tensor.Tensor([timestep]),
            alphas[tid],
            alphas_prev[tid],
            tg_tensor.Tensor([args.guidance]),
        )

    # upsample latent space to image with autoencoder
    x = model.decode(latent)
    log.info('Shape: %r', x.shape)

    # save image
    im = pi.fromarray(x.numpy().astype(np.uint8, copy=False))
    img_byte_arr = io.BytesIO()
    im.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


##


def _check_auth(scope: asgi.Scope, sec_token: str) -> bool:
    if not sec_token:
        return False

    hdrs = dict(scope['headers'])
    auth = hdrs.get(hu.consts.HEADER_AUTH.lower())
    if not auth or not auth.startswith(hu.consts.BEARER_AUTH_HEADER_PREFIX):
        return False

    auth_token = auth[len(hu.consts.BEARER_AUTH_HEADER_PREFIX):].decode()
    if auth_token != sec_token:
        return False

    return True


@dc.dataclass(frozen=True)
class SdHandler(RouteHandlerHolder):
    _secrets: sec.Secrets

    @handles(Route.post('/sd'))
    async def handle_post_sd(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        if not _check_auth(scope, self._secrets.get('sd_auth_token').reveal()):
            await asgi.send_response(send, 401)
            return

        req_body = await asgi.read_body(recv)
        sd_args = SdArgs(**json.loads(req_body))
        sd_out_png = await anyio.to_thread.run_sync(functools.partial(run_sd, sd_args))

        await asgi.send_response(send, 200, hu.consts.CONTENT_TYPE_PNG, body=sd_out_png)

    @handles(Route.post('/sd2'))
    async def handle_post_sd2(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        if not _check_auth(scope, self._secrets.get('sd_auth_token').reveal()):
            await asgi.send_response(send, 401)
            return

        sd2_url = self._secrets.get('sd2_url').reveal()

        req_body = await asgi.read_body(recv)

        async with httpx.AsyncClient(timeout=180) as client:
            resp = await client.post(f'{sd2_url}/sd', content=req_body)
            await asgi.send_response(send, resp.status_code, hu.consts.CONTENT_TYPE_PNG, body=resp.content)
