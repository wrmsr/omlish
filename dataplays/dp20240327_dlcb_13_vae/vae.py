import os.path

import torchvision.datasets


def _main() -> None:
    ds = torchvision.datasets.MNIST(
        root=os.path.join(os.path.dirname(__file__), 'data'),
        download=True,
    )
    print(ds)


if __name__ == '__main__':
    _main()
