import numpy as np
import torch


def get_rotary_matrix(context_window, embedding_dim):
    R = torch.zeros((context_window, embedding_dim, embedding_dim), requires_grad=False)
    for position in range(context_window):
        for i in range(embedding_dim // 2):
            theta = 10000. ** (-2. * (i - 1) / embedding_dim)
            m_theta = position * theta
            R[position, 2 * i, 2 * i] = np.cos(m_theta)
            R[position, 2 * i, 2 * i + 1] = - np.sin(m_theta)
            R[position, 2 * i + 1, 2 * i] = np.sin(m_theta)
            R[position, 2 * i + 1, 2 * i + 1] = np.cos(m_theta)
    return R


def plot():
    from matplotlib import pyplot as plt

    K = 3
    config = {
        'batch_size': 10,
        'd_model': 32,
        'n_heads': 8,
        'context_window': K ** 2,
    }
    batch = torch.randn(1, config['context_window'], config['d_model'])
    R = get_rotary_matrix(config['context_window'], config['d_model'])
    fig, ax = plt.subplots(K, K, figsize=(K * 3, K * 4))

    for i in range(K):
        for j in range(K):
            ax[i, j].imshow(R[i * K + j, :, :].detach().numpy())
            ax[i, j].set_title(f'rotation at {i * K + j}')


def test():
    config = {
        'd_model': 128,
        'context_window': 16,
    }

    R = get_rotary_matrix(config['context_window'], config['d_model'])
    x = torch.randn(config['d_model'])
    y = torch.randn(config['d_model'])

    m = 3
    n = 13

    x_m = R[m, :, :] @ x
    x_n = R[n, :, :] @ y

    assert torch.isclose(x_m @ x_n, x @ R[n - m, :, :] @ y)
