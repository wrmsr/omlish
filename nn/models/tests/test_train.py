import unittest
import time

import numpy as np

from ...extra.training import train
from ...helpers import getenv
from ...nn import optim
from ...nn.state import get_parameters
from ...tensor import Device


BS = getenv("BS", 2)


def train_one_step(model, X, Y):
    params = get_parameters(model)
    pcount = 0
    for p in params:
        pcount += np.prod(p.shape)
    optimizer = optim.SGD(params, lr=0.001)
    print("stepping %r with %.1fM params bs %d" % (type(model), pcount / 1e6, BS))
    st = time.time()
    train(model, X, Y, optimizer, steps=1, BS=BS)
    et = time.time() - st
    print("done in %.2f ms" % (et * 1000.))


class TestTrain(unittest.TestCase):
    def test_convnext(self):
        from ...models.convnext import ConvNeXt

        model = ConvNeXt(depths=[1], dims=[16])
        X = np.zeros((BS, 3, 224, 224), dtype=np.float32)
        Y = np.zeros((BS), dtype=np.int32)
        train_one_step(model, X, Y)

    # def test_efficientnet(self):
    #     from ...models.efficientnet import EfficientNet
    #
    #     model = EfficientNet(0)
    #     X = np.zeros((BS, 3, 224, 224), dtype=np.float32)
    #     Y = np.zeros((BS), dtype=np.int32)
    #     train_one_step(model, X, Y)

    @unittest.skipIf(Device.DEFAULT == "WEBGPU", "too many buffers for webgpu")
    def test_vit(self):
        from ...models.vit import ViT

        model = ViT()
        X = np.zeros((BS, 3, 224, 224), dtype=np.float32)
        Y = np.zeros((BS,), dtype=np.int32)
        train_one_step(model, X, Y)

    def test_transformer(self):
        from ...models.transformer import Transformer

        # this should be small GPT-2, but the param count is wrong
        # (real ff_dim is 768*4)
        model = Transformer(syms=10, maxlen=6, layers=12, embed_dim=768, num_heads=12, ff_dim=768 // 4)
        X = np.zeros((BS, 6), dtype=np.float32)
        Y = np.zeros((BS, 6), dtype=np.int32)
        train_one_step(model, X, Y)

    # def test_resnet(self):
    #     from ...models.resnet import ResNet18
    #
    #     X = np.zeros((BS, 3, 224, 224), dtype=np.float32)
    #     Y = np.zeros((BS), dtype=np.int32)
    #     for resnet_v in [ResNet18]:
    #         model = resnet_v()
    #         model.load_from_pretrained()
    #         train_one_step(model, X, Y)


if __name__ == '__main__':
    unittest.main()
