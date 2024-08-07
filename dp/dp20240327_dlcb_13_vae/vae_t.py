import os.path  # noqa
import time
import typing as ta

import PIL
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data
import torchvision.datasets  # noqa


def to_categorical(y, num_classes=None, dtype="float32"):
    y = np.array(y, dtype="int")
    input_shape = y.shape

    if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
        input_shape = tuple(input_shape[:-1])

    y = y.reshape(-1)
    if not num_classes:
        num_classes = np.max(y) + 1

    n = y.shape[0]
    categorical = np.zeros((n, num_classes), dtype=dtype)
    categorical[np.arange(n), y] = 1
    output_shape = input_shape + (num_classes,)
    categorical = np.reshape(categorical, output_shape)
    return categorical


def prepare(images, labels):
    images = images.astype('float32') / 255
    n, w, h = images.shape
    return images.reshape((n, w * h)), to_categorical(labels)


def decode_img(a):
    a = np.clip(a * 256, 0, 255).astype('uint8')
    return PIL.Image.fromarray(a)


class VAE(nn.Module):

    def __init__(self, latent_space_depth: int, num_pixels: int, hidden_dim: int = 512) -> None:
        super().__init__()
        self.latent_space_depth = latent_space_depth
        self.num_pixels = num_pixels
        self.hidden_dim = hidden_dim

        self.encoder_hidden = nn.Linear(num_pixels, hidden_dim)  # , activation='relu')(pixels)
        self.z_mean = nn.Linear(hidden_dim, latent_space_depth)  # , activation='linear')(encoder_hidden)
        self.z_log_var = nn.Linear(hidden_dim, latent_space_depth)  # , activation='linear')(encoder_hidden)
        self.decoder_hidden = nn.Linear(latent_space_depth, hidden_dim)  # , activation='relu')
        self.reconstruct_pixels = nn.Linear(hidden_dim, num_pixels)  # , activation='sigmoid')

    def sample_z(self, z_mean: torch.Tensor, z_log_var: torch.Tensor) -> torch.Tensor:
        eps = torch.empty(z_mean.shape[0], self.latent_space_depth).normal_(mean=0., std=1.)
        return z_mean + (z_log_var / 2).exp() * eps

    def kl_loss(self, z_log_var: torch.Tensor, z_mean: torch.Tensor) -> torch.Tensor:
        return .5 * (z_log_var.exp() + z_mean.square() - 1 - z_log_var).sum(1)

    def reconstruction_loss(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> torch.Tensor:
        print((y_true.min(), y_true.max(), y_pred.min(), y_pred.max()))
        return F.binary_cross_entropy(y_true, y_pred, reduction='none').sum(-1)

    def total_loss(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> torch.Tensor:
        return self.kl_loss(y_true, y_pred) + self.reconstruction_loss(y_true, y_pred)

    class Forward(ta.NamedTuple):
        outputs: torch.Tensor  # (bs, np)
        losses: torch.Tensor  # (bs,)

    def forward(
            self,
            pixels: torch.Tensor,  # (bs, np)
    ) -> Forward:
        encoder_hidden = F.relu(self.encoder_hidden(pixels))  # (bs, hd)

        z_mean = self.z_mean(encoder_hidden)  # (bs, lsd)
        z_log_var = self.z_mean(encoder_hidden)  # (bs, lsd)

        z = self.sample_z(z_mean, z_log_var)  # (bs, lsd)

        hidden = F.relu(self.decoder_hidden(z))  # (bs, hd)
        outputs = F.sigmoid(self.reconstruct_pixels(hidden))  # (bs, np)

        losses = self.total_loss(pixels, outputs)  # (bs,)

        return VAE.Forward(outputs, losses)

    def decode(self, decoder_in: torch.Tensor) -> torch.Tensor:
        hidden = F.relu(self.decoder_hidden(decoder_in))
        decoder_out = F.sigmoid(self.reconstruct_pixels(hidden))
        return decoder_out


LOCAL_DIR = os.path.dirname(__file__)


def _main() -> None:
    from keras.datasets import mnist  # noqa
    train, test = mnist.load_data()
    x_train, y_train = prepare(*train)
    x_test, y_test = prepare(*test)
    img_width, img_height = train[0].shape[1:]

    batch_size = 250

    train_ds = torch.utils.data.TensorDataset(torch.tensor(x_train))
    train_dl = torch.utils.data.DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    latent_space_depth = 2
    num_pixels = x_train.shape[1]

    ##

    vae = VAE(latent_space_depth, num_pixels)

    ##

    lr = .001
    epochs = 100

    opt = torch.optim.Adam(vae.parameters(), lr=lr)

    vae.train()
    for epoch in range(epochs):
        for nb, [pixels] in enumerate(train_dl):
            outputs, losses = vae(pixels)
            total_loss = losses.mean()
            print((epoch, nb, total_loss.item()))
            total_loss.backward()
            opt.step()
            opt.zero_grad()

    # auto_encoder.fit(
    #     x_train,
    #     x_train,
    #     verbose=1,
    #     batch_size=batch_size,
    #     epochs=100,
    #     validation_data=(x_test, x_test),
    #     callbacks=[
    #         *([SaveModelCallback(10, out_model_path)] if out_model_path else []),
    #     ]
    # )
    #
    # ##
    #
    # random_number = np.asarray([[np.random.normal() for _ in range(latent_space_depth)]])
    #
    # decode_img(decoder.predict(random_number).reshape(img_width, img_height)).resize((56, 56)).show()
    #
    # ##
    #
    # num_cells = 10
    #
    # overview = PIL.Image.new(
    #     'RGB',
    #     (
    #         num_cells * (img_width + 4) + 8,
    #         num_cells * (img_height + 4) + 8,
    #     ),
    #     (128, 128, 128),
    # )
    #
    # vec = np.zeros((1, latent_space_depth))
    # for x in range(num_cells):
    #     vec[:, 0] = (x * 3) / (num_cells - 1) - 1.5
    #     for y in range(num_cells):
    #         vec[:, 1] = (y * 3) / (num_cells - 1) - 1.5
    #         decoded = decoder.predict(vec)
    #         img = decode_img(decoded.reshape(img_width, img_height))
    #         overview.paste(img, (x * (img_width + 4) + 6, y * (img_height + 4) + 6))
    #
    # overview.show()


if __name__ == '__main__':
    _main()
