import io

import numpy as np

from ..tensor import Tensor
from .transformer import TransformerBlock


class ViT:
    def __init__(
            self,
            layers=12,
            embed_dim=192,
            num_heads=3,
    ) -> None:
        super().__init__()
        self.embedding = (Tensor.uniform(embed_dim, 3, 16, 16), Tensor.zeros(embed_dim))
        self.embed_dim = embed_dim
        self.cls = Tensor.ones(1, 1, embed_dim)
        self.pos_embedding = Tensor.ones(1, 197, embed_dim)
        self.tbs = [
            TransformerBlock(
                embed_dim=embed_dim,
                num_heads=num_heads,
                ff_dim=embed_dim * 4,
                prenorm=True,
                act=lambda x: x.gelu(),
            )
            for i in range(layers)
        ]
        self.encoder_norm = (Tensor.uniform(embed_dim), Tensor.zeros(embed_dim))
        self.head = (Tensor.uniform(embed_dim, 1000), Tensor.zeros(1000))

    def patch_embed(self, x):
        x = x.conv2d(*self.embedding, stride=16)
        x = x.reshape(shape=(x.shape[0], x.shape[1], -1)).permute(order=(0, 2, 1))
        return x

    def forward(self, x):
        ce = self.cls.add(Tensor.zeros(x.shape[0], 1, 1))
        pe = self.patch_embed(x)
        x = ce.cat(pe, dim=1)
        x = x.add(self.pos_embedding).sequential(self.tbs)
        x = x.layernorm().linear(*self.encoder_norm)
        return x[:, 0].linear(*self.head)

    def load_from_pretrained(self):
        from ..helpers import fetch

        # https://github.com/rwightman/pytorch-image-models/blob/master/timm/models/vision_transformer.py
        base_url = "https://storage.googleapis.com/vit_models/augreg"
        if self.embed_dim == 192:
            url = base_url + "/Ti_16-i21k-300ep-lr_0.001-aug_none-wd_0.03-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.03-res_224.npz"
        elif self.embed_dim == 768:
            url = base_url + "/B_16-i21k-300ep-lr_0.001-aug_medium1-wd_0.1-do_0.0-sd_0.0--imagenet2012-steps_20k-lr_0.01-res_224.npz"
        else:
            raise Exception("no pretrained weights for configuration")
        dat = np.load(io.BytesIO(fetch(url)))

        # for x in dat.keys():
        #  print(x, dat[x].shape, dat[x].dtype)

        self.embedding[0].assign(np.transpose(dat['embedding/kernel'], (3, 2, 0, 1)))
        self.embedding[1].assign(dat['embedding/bias'])

        self.cls.assign(dat['cls'])

        self.head[0].assign(dat['head/kernel'])
        self.head[1].assign(dat['head/bias'])

        self.pos_embedding.assign(dat['Transformer/posembed_input/pos_embedding'])
        self.encoder_norm[0].assign(dat['Transformer/encoder_norm/scale'])
        self.encoder_norm[1].assign(dat['Transformer/encoder_norm/bias'])

        for i in range(12):
            pfx = f'Transformer/encoderblock_{i}'
            self.tbs[i].query[0].assign(dat[f'{pfx}/MultiHeadDotProductAttention_1/query/kernel'].reshape(self.embed_dim, self.embed_dim))
            self.tbs[i].query[1].assign(dat[f'{pfx}/MultiHeadDotProductAttention_1/query/bias'].reshape(self.embed_dim))
            self.tbs[i].key[0].assign(dat[f'{pfx}/MultiHeadDotProductAttention_1/key/kernel'].reshape(self.embed_dim, self.embed_dim))
            self.tbs[i].key[1].assign(dat[f'{pfx}/MultiHeadDotProductAttention_1/key/bias'].reshape(self.embed_dim))
            self.tbs[i].value[0].assign(dat[f'{pfx}/MultiHeadDotProductAttention_1/value/kernel'].reshape(self.embed_dim, self.embed_dim))
            self.tbs[i].value[1].assign(dat[f'{pfx}/MultiHeadDotProductAttention_1/value/bias'].reshape(self.embed_dim))
            self.tbs[i].out[0].assign(dat[f'{pfx}/MultiHeadDotProductAttention_1/out/kernel'].reshape(self.embed_dim, self.embed_dim))
            self.tbs[i].out[1].assign(dat[f'{pfx}/MultiHeadDotProductAttention_1/out/bias'].reshape(self.embed_dim))
            self.tbs[i].ff1[0].assign(dat[f'{pfx}/MlpBlock_3/Dense_0/kernel'])
            self.tbs[i].ff1[1].assign(dat[f'{pfx}/MlpBlock_3/Dense_0/bias'])
            self.tbs[i].ff2[0].assign(dat[f'{pfx}/MlpBlock_3/Dense_1/kernel'])
            self.tbs[i].ff2[1].assign(dat[f'{pfx}/MlpBlock_3/Dense_1/bias'])
            self.tbs[i].ln1[0].assign(dat[f'{pfx}/LayerNorm_0/scale'])
            self.tbs[i].ln1[1].assign(dat[f'{pfx}/LayerNorm_0/bias'])
            self.tbs[i].ln2[0].assign(dat[f'{pfx}/LayerNorm_2/scale'])
            self.tbs[i].ln2[1].assign(dat[f'{pfx}/LayerNorm_2/bias'])
