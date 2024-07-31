"""
https://github.com/lyeoni/pytorch-mnist-VAE/blob/master/pytorch-mnist-VAE.ipynb
"""
import random

from omlish.iterators import sliding_window
import PIL
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data


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


def prepare(images, labels, px_shuf):
    n, w, h = images.shape
    images = images.reshape(n, -1)[:, px_shuf].reshape(n, w, h)
    images = images.astype('float32') / 255
    return images.reshape((n, w * h)), to_categorical(labels)


def decode_img(a):
    a = np.clip(a * 256, 0, 255).astype('uint8')
    return PIL.Image.fromarray(a)


class Vae(nn.Module):
    def __init__(
            self,
            x_dim,
            h_dims,
            z_dim,
    ):
        super().__init__()

        self.x_dim = x_dim
        self.h_dims = h_dims
        self.z_dim = z_dim

        self.z_mean = nn.Linear(h_dims[-1], z_dim)
        self.z_log_var = nn.Linear(h_dims[-1], z_dim)

        self.encoder_hidden = [nn.Linear(f, t) for f, t in sliding_window([x_dim, *h_dims], 2)]
        self.decoder_hidden = [nn.Linear(f, t) for f, t in sliding_window([z_dim, *reversed(h_dims)], 2)]

        self.reconstruct_pixels = nn.Linear(h_dims[0], x_dim)

    def encoder(self, x):
        h = x
        for l in self.encoder_hidden:
            h = F.relu(l(h))
        return self.z_mean(h), self.z_log_var(h)

    def sampling(self, z_mean, z_log_var):
        std = torch.exp(0.5 * z_log_var)
        eps = torch.randn_like(std)
        return eps.mul(std).add_(z_mean)  # return z sample

    def decoder(self, z):
        h = z
        for l in self.decoder_hidden:
            h = F.relu(l(h))
        return F.sigmoid(self.reconstruct_pixels(h))

    def forward(self, x):
        z_mean, z_log_var = self.encoder(x.view(-1, self.x_dim))
        z = self.sampling(z_mean, z_log_var)
        return self.decoder(z), z_mean, z_log_var


def _main():
    from keras.datasets import mnist  # noqa
    train, test = mnist.load_data()
    img_width, img_height = train[0].shape[1:]

    px_shuf = list(range(img_width * img_height))
    random.shuffle(px_shuf)
    px_unshuf = [f for t, f in sorted((t, f) for f, t in enumerate(px_shuf))]

    x_train, y_train = prepare(*train, px_shuf)
    x_test, y_test = prepare(*test, px_shuf)

    batch_size = 250

    train_ds = torch.utils.data.TensorDataset(torch.tensor(x_train))
    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    test_ds = torch.utils.data.TensorDataset(torch.tensor(x_test))
    test_loader = torch.utils.data.DataLoader(test_ds, batch_size=batch_size, shuffle=True)

    # build model
    vae = Vae(
        x_dim=img_width * img_height,
        h_dims=[
            512,
            256,
        ],
        z_dim=2,
    )

    if torch.cuda.is_available():
        vae.cuda()

    optimizer = optim.Adam(vae.parameters())

    # return reconstruction error + KL divergence losses
    def loss_function(recon_x, x, z_mean, z_log_var):
        reconstruction_loss = F.binary_cross_entropy(recon_x, x.view(-1, img_width * img_height), reduction='sum')
        kl_loss = -0.5 * torch.sum(1 + z_log_var - z_mean.pow(2) - z_log_var.exp())
        return reconstruction_loss + kl_loss

    def train(epoch):
        vae.train()
        train_loss = 0
        for batch_idx, data in enumerate(train_loader):
            data = torch.stack(data).squeeze(0)

            if torch.cuda.is_available():
                data = data.cuda()

            optimizer.zero_grad()

            recon_batch, z_mean, z_log_var = vae(data)
            loss = loss_function(recon_batch, data, z_mean, z_log_var)

            loss.backward()
            train_loss += loss.item()
            optimizer.step()

            if batch_idx % 100 == 0:
                print(
                    'Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                    epoch,
                        batch_idx * len(data),
                        -len(train_loader.dataset),
                        100. * batch_idx / len(train_loader),
                        loss.item() / len(data),
                    ),
                )

        print(
            '====> Epoch: {} Average loss: {:.4f}'.format(
                epoch,
                train_loss / len(train_loader.dataset),
            ),
        )

    def test():
        vae.eval()
        test_loss = 0
        with torch.no_grad():
            for data in test_loader:
                data = torch.stack(data).squeeze(0)

                if torch.cuda.is_available():
                    data = data.cuda()
                recon, z_mean, z_log_var = vae(data)

                # sum up batch loss
                test_loss += loss_function(recon, data, z_mean, z_log_var).item()

        test_loss /= len(test_loader.dataset)
        print('====> Test set loss: {:.4f}'.format(test_loss))

        random_number = np.asarray([[np.random.normal() for _ in range(vae.z_dim)]])
        dn = vae.decoder(torch.Tensor(random_number)).reshape(img_width, img_height).detach().numpy()
        dn = dn.reshape(-1)[px_unshuf].reshape(img_width, img_height)
        decode_img(dn).resize((56, 56)).show()

    for epoch in range(1, 51):
        train(epoch)
        test()


if __name__ == '__main__':
    _main()
