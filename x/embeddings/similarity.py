import numpy as np


def cosine_similarity(
        a: np.ndarray,  # (n, d)
        b: np.ndarray,  # (d,)
) -> np.ndarray:  # (n,)
    return np.dot(a, b) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b))


def _main():
    a = np.array([
        [2, 1, 2],
        [3, 2, 9],
        [-1, 2, -3],
        [-2, 3, -4],
    ])
    b = np.array([3, 4, 2])

    print(f'a:\n{a}\n')
    print(f'b:\n{b}\n')

    print(f'cosine_similarity:\n{cosine_similarity(a, b)}\n', )


if __name__ == '__main__':
    _main()
