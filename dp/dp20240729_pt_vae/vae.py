"""
https://github.com/lyeoni/pytorch-mnist-VAE/blob/master/pytorch-mnist-VAE.ipynb
"""
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


def prepare(images, labels):
    images = images.astype('float32') / 255
    n, w, h = images.shape
    return images.reshape((n, w * h)), to_categorical(labels)


def decode_img(a):
    a = np.clip(a * 256, 0, 255).astype('uint8')
    return PIL.Image.fromarray(a)


def _main():
    bs = 100

    # MNIST Dataset
    # train_dataset = datasets.MNIST(root='./mnist_data/', train=True, transform=transforms.ToTensor(), download=True)
    # test_dataset = datasets.MNIST(root='./mnist_data/', train=False, transform=transforms.ToTensor(), download=False)
    #
    # train_ds = torch.utils.data.TensorDataset(torch.tensor(x_train))
    # train_dl = torch.utils.data.DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    #
    # # Data Loader (Input Pipeline)
    # train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=bs, shuffle=True)
    # test_loader = torch.utils.data.DataLoader(dataset=test_dataset, batch_size=bs, shuffle=False)

    from keras.datasets import mnist  # noqa
    train, test = mnist.load_data()
    x_train, y_train = prepare(*train)
    x_test, y_test = prepare(*test)
    img_width, img_height = train[0].shape[1:]

    batch_size = 250

    train_ds = torch.utils.data.TensorDataset(torch.tensor(x_train))
    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    test_ds = torch.utils.data.TensorDataset(torch.tensor(x_test))
    test_loader = torch.utils.data.DataLoader(test_ds, batch_size=batch_size, shuffle=True)

    class Vae(nn.Module):
        def __init__(
                self,
                x_dim,
                h_dim1,
                h_dim2,
                z_dim,
        ):
            super().__init__()

            self.x_dim = x_dim
            self.h_dim1 = h_dim1
            self.h_dim2 = h_dim2
            self.z_dim = z_dim

            # encoder part
            self.fc1 = nn.Linear(x_dim, h_dim1)
            self.fc2 = nn.Linear(h_dim1, h_dim2)
            self.fc31 = nn.Linear(h_dim2, z_dim)
            self.fc32 = nn.Linear(h_dim2, z_dim)
            # decoder part
            self.fc4 = nn.Linear(z_dim, h_dim2)
            self.fc5 = nn.Linear(h_dim2, h_dim1)
            self.fc6 = nn.Linear(h_dim1, x_dim)

        def encoder(self, x):
            h = F.relu(self.fc1(x))
            h = F.relu(self.fc2(h))
            return self.fc31(h), self.fc32(h)  # mu, log_var

        def sampling(self, mu, log_var):
            std = torch.exp(0.5 * log_var)
            eps = torch.randn_like(std)
            return eps.mul(std).add_(mu)  # return z sample

        def decoder(self, z):
            h = F.relu(self.fc4(z))
            h = F.relu(self.fc5(h))
            return F.sigmoid(self.fc6(h))

        def forward(self, x):
            mu, log_var = self.encoder(x.view(-1, 784))
            z = self.sampling(mu, log_var)
            return self.decoder(z), mu, log_var

    # build model
    vae = Vae(x_dim=784, h_dim1=512, h_dim2=256, z_dim=2)
    if torch.cuda.is_available():
        vae.cuda()

    optimizer = optim.Adam(vae.parameters())

    # return reconstruction error + KL divergence losses
    def loss_function(recon_x, x, mu, log_var):
        BCE = F.binary_cross_entropy(recon_x, x.view(-1, 784), reduction='sum')
        KLD = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        return BCE + KLD

    def train(epoch):
        vae.train()
        train_loss = 0
        for batch_idx, data in enumerate(train_loader):
            data = torch.stack(data).squeeze(0)

            if torch.cuda.is_available():
                data = data.cuda()

            optimizer.zero_grad()

            recon_batch, mu, log_var = vae(data)
            loss = loss_function(recon_batch, data, mu, log_var)

            loss.backward()
            train_loss += loss.item()
            optimizer.step()

            if batch_idx % 100 == 0:
                print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                    epoch, batch_idx * len(data), len(train_loader.dataset),
                           100. * batch_idx / len(train_loader), loss.item() / len(data)))
        print('====> Epoch: {} Average loss: {:.4f}'.format(epoch, train_loss / len(train_loader.dataset)))

    def test():
        vae.eval()
        test_loss = 0
        with torch.no_grad():
            for data in test_loader:
                data = torch.stack(data).squeeze(0)

                if torch.cuda.is_available():
                    data = data.cuda()
                recon, mu, log_var = vae(data)

                # sum up batch loss
                test_loss += loss_function(recon, data, mu, log_var).item()

        test_loss /= len(test_loader.dataset)
        print('====> Test set loss: {:.4f}'.format(test_loss))

        random_number = np.asarray([[np.random.normal() for _ in range(vae.z_dim)]])
        decode_img(vae.decoder(torch.Tensor(random_number)).reshape(img_width, img_height).detach().numpy()).resize((56, 56)).show()

    for epoch in range(1, 51):
        train(epoch)
        test()


if __name__ == '__main__':
    _main()
