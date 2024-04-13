import keras
import numpy as np
import torch
import torch.nn.functional as F


def make_keras_model(n_x, n_y, n_e):
    x = keras.Input(name='x', shape=(1,))
    y = keras.Input(name='y', shape=(1,))
    x_e = keras.layers.Embedding(
        name='x_e',
        input_dim=n_x,
        output_dim=n_e,
    )(x)
    y_e = keras.layers.Embedding(
        name='y_e',
        input_dim=n_y,
        output_dim=n_e,
    )(y)
    dot = keras.layers.Dot(
        name='dp',
        normalize=True,
        axes=2,
    )([x_e, y_e])
    out = keras.layers.Reshape((1,))(dot)
    model = keras.Model(inputs=[x, y], outputs=[out])
    model.compile(optimizer='nadam', loss='mse')
    return model


class TorchModel(torch.nn.Module):
    def __init__(self, n_x, n_y, n_e):
        super().__init__()
        self.n_x = n_x
        self.n_y = n_y
        self.n_e = n_e
        self.x_e = torch.nn.Embedding(n_x, n_e)
        self.y_e = torch.nn.Embedding(n_y, n_e)

    def forward(self, x, y):
        x_e = self.x_e.forward(x)
        y_e = self.y_e.forward(y)
        x_e = F.normalize(x_e, dim=-1)
        y_e = F.normalize(y_e, dim=-1)
        dot = torch.bmm(
            x_e.view(-1, 1, self.n_e),
            y_e.view(-1, self.n_e, 1),
        )
        out = dot.reshape(-1)
        return out


def _main():
    n_x = 8
    n_y = 8
    n_e = 4

    m_k = make_keras_model(n_x, n_y, n_e)
    m_t = TorchModel(n_x, n_y, n_e)

    ew_x = m_k.layers[2].weights[0].numpy()
    ew_y = m_k.layers[3].weights[0].numpy()

    m_t.x_e.weight.data[:] = torch.Tensor(ew_x)
    m_t.y_e.weight.data[:] = torch.Tensor(ew_y)

    x = np.arange(8, dtype=int)
    y = np.arange(8, dtype=int)
    l = np.asarray([1, -1] * 4)

    np.random.seed(0)
    np.random.shuffle(x)
    np.random.shuffle(y)

    def dump_weights():
        print(m_k([x, y]).numpy())
        print(m_t(torch.tensor(x, dtype=torch.int32), torch.tensor(y, dtype=torch.int32)).detach().numpy())
    
    dump_weights()

    def step_k():
        m_k.fit(
            (x, y),
            l,
            epochs=1,
            steps_per_epoch=1,
            verbose=2
        )

    lr = 0.001
    optimizer = torch.optim.NAdam(m_t.parameters(), lr=lr, eps=1e-7)
    loss_fn = torch.nn.MSELoss()

    def step_t():
        m_t.train()
        optimizer.zero_grad()
        out = m_t(torch.tensor(x, dtype=torch.int32), torch.tensor(y, dtype=torch.int32))
        loss = loss_fn(out, torch.tensor(l, dtype=torch.float32))
        loss.backward()
        optimizer.step()
        print(loss)

    for _ in range(2):
        step_k()
        step_t()
        dump_weights()


if __name__ == '__main__':
    _main()
