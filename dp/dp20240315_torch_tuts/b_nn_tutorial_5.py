import gzip
import pathlib
import pickle

from matplotlib import pyplot  # noqa
import numpy as np
import requests
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data


def load_data() -> tuple[np.ndarray, ...]:
    data_path = pathlib.Path('data')
    path = data_path / 'mnist'

    path.mkdir(parents=True, exist_ok=True)

    url = 'https://github.com/pytorch/tutorials/raw/main/_static/'
    filename = 'mnist.pkl.gz'

    if not (path / filename).exists():
        content = requests.get(url + filename).content
        (path / filename).open('wb').write(content)

    with gzip.open((path / filename).as_posix(), 'rb') as f:
        (x_train, y_train), (x_valid, y_valid), _ = pickle.load(f, encoding='latin-1')

    return x_train, y_train, x_valid, y_valid


def get_data(train_ds, valid_ds, bs):
    return (
        torch.utils.data.DataLoader(train_ds, batch_size=bs, shuffle=True),
        torch.utils.data.DataLoader(valid_ds, batch_size=bs * 2),
    )


def loss_batch(model, loss_func, xb, yb, opt=None):
    loss = loss_func(model(xb), yb)

    if opt is not None:
        loss.backward()
        opt.step()
        opt.zero_grad()

    return loss.item(), len(xb)


def fit(epochs, model, loss_func, opt, train_dl, valid_dl):
    for epoch in range(epochs):
        model.train()
        for xb, yb in train_dl:
            loss_batch(model, loss_func, xb, yb, opt)

        model.eval()
        with torch.no_grad():
            losses, nums = zip(
                *[loss_batch(model, loss_func, xb, yb) for xb, yb in valid_dl]
            )
        val_loss = np.sum(np.multiply(losses, nums)) / np.sum(nums)

        print(epoch, val_loss)


class Mnist_CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1)
        self.conv2 = nn.Conv2d(16, 16, kernel_size=3, stride=2, padding=1)
        self.conv3 = nn.Conv2d(16, 10, kernel_size=3, stride=2, padding=1)

    def forward(
            self,
            xb,  # B x 1 x 28 x 28
    ):
        xb = F.relu(self.conv1(xb))
        xb = F.relu(self.conv2(xb))
        xb = F.relu(self.conv3(xb))
        xb = F.adaptive_avg_pool2d(xb, 1)
        return xb.view(xb.size(0), -1)


class WrappedDataLoader:
    def __init__(self, dl, func):
        super().__init__()
        self.dl = dl
        self.func = func

    def __len__(self):
        return len(self.dl)

    def __iter__(self):
        for b in self.dl:
            yield (self.func(*b))


def _main():
    x_train, y_train, x_valid, y_valid = map(torch.tensor, load_data())
    train_ds = torch.utils.data.TensorDataset(x_train, y_train)
    valid_ds = torch.utils.data.TensorDataset(x_valid, y_valid)

    bs = 64  # batch size

    dev = torch.device('mps')

    def preprocess(x, y):
        return x.view(-1, 1, 28, 28).to(dev), y.to(dev)

    train_dl, valid_dl = get_data(train_ds, valid_ds, bs)
    train_dl = WrappedDataLoader(train_dl, preprocess)
    valid_dl = WrappedDataLoader(valid_dl, preprocess)

    model = Mnist_CNN()
    model.to(dev)

    lr = 0.1
    opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)

    epochs = 10
    loss_func = F.cross_entropy
    fit(epochs, model, loss_func, opt, train_dl, valid_dl)


if __name__ == '__main__':
    _main()
