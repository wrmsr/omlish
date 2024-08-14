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

from omlish import http as hu
from omlish import lang
from omlish import secrets as sec
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import read_body
from omlish.http.asgi import send_response
from omlish.serde import json
from omserv.apps.routes import Handler_
from omserv.apps.routes import Route
from omserv.apps.routes import handles


# fmt: off
if ta.TYPE_CHECKING:
    import numpy as np  # noqa
    import tinygrad as tg
    import tinygrad.tensor  # noqa
    from tinygrad import nn  # type: ignore
    from examples import stable_diffusion as sd
    from PIL import Image as pi  # noqa
else:
    np = lang.proxy_import('numpy')
    tg = lang.proxy_import('tinygrad')
    nn = lang.proxy_import('tinygrad.nn')
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
    tg.tensor.Tensor.no_grad = True
    model = sd.StableDiffusion()

    # load in weights
    weights_url = 'https://huggingface.co/CompVis/stable-diffusion-v-1-4-original/resolve/main/sd-v1-4.ckpt'
    fetched_weights = tg.helpers.fetch(weights_url, 'sd-v1-4.ckpt')  # type: ignore
    nn.state.load_state_dict(model, nn.state.torch_load(str(fetched_weights))['state_dict'], strict=False)

    # run through CLIP to get context
    tokenizer = sd.Tokenizer.ClipTokenizer()
    prompt = tg.tensor.Tensor([tokenizer.encode(args.prompt)])
    context = model.cond_stage_model.transformer.text_model(prompt).realize()
    log.info('Got CLIP context: %r', context.shape)

    prompt = tg.tensor.Tensor([tokenizer.encode('')])
    unconditional_context = model.cond_stage_model.transformer.text_model(prompt).realize()
    log.info('Got unconditional CLIP context: %r', unconditional_context.shape)

    # done with clip model
    del model.cond_stage_model

    timesteps = list(range(1, 1000, 1000 // args.steps))
    log.info('Running for %d timesteps', timesteps)
    alphas = model.alphas_cumprod[tg.tensor.Tensor(timesteps)]
    alphas_prev = tg.tensor.Tensor([1.0]).cat(alphas[:-1])

    # start with random noise
    if args.seed is not None:
        tg.tensor.Tensor.manual_seed(args.seed)
    latent = tg.tensor.Tensor.randn(1, 4, 64, 64)

    @tg.TinyJit  # type: ignore
    def run(model, *x):
        return model(*x).realize()

    # this is diffusion
    for index, timestep in list(enumerate(timesteps))[::-1]:
        tid = tg.tensor.Tensor([index])
        latent = run(
            model,
            unconditional_context,
            context,
            latent,
            tg.tensor.Tensor([timestep]),
            alphas[tid],
            alphas_prev[tid],
            tg.tensor.Tensor([args.guidance]),
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


@dc.dataclass(frozen=True)
class SdHandler(Handler_):
    _secrets: sec.Secrets

    @handles(Route.post('/sd'))
    async def handle_post_sd(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        hdrs = dict(scope['headers'])
        auth = hdrs.get(hu.consts.HEADER_AUTH.lower())
        if not auth or not auth.startswith(hu.consts.BEARER_AUTH_HEADER_PREFIX):
            await send_response(send, 401)
            return

        auth_token = auth[len(hu.consts.BEARER_AUTH_HEADER_PREFIX):].decode()
        if auth_token != self._secrets.get('sd_auth_token'):
            await send_response(send, 401)
            return

        req_body = await read_body(recv)
        sd_args = SdArgs(**json.loads(req_body))
        sd_out_png = await anyio.to_thread.run_sync(functools.partial(run_sd, sd_args))

        await send_response(send, 200, hu.consts.CONTENT_TYPE_PNG, body=sd_out_png)
