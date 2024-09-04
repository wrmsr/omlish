"""
https://pytorch.org/tutorials/beginner/basics/data_tutorial.html
"""
from torchvision import datasets
from torchvision.transforms import ToTensor


def test_torch():
    root = '.cache/torch_data'
    training_data = datasets.FashionMNIST(  # noqa
        root=root,
        train=True,
        download=True,
        transform=ToTensor(),
    )

    test_data = datasets.FashionMNIST(  # noqa
        root=root,
        train=False,
        download=True,
        transform=ToTensor(),
    )
