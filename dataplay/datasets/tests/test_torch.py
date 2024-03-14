"""
https://pytorch.org/tutorials/beginner/basics/data_tutorial.html
"""
import torch
from torch.utils.data import Dataset
from torchvision import datasets
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt


def test_torch():
    root = '.cache/torch_data'
    training_data = datasets.FashionMNIST(
        root=root,
        train=True,
        download=True,
        transform=ToTensor()
    )

    test_data = datasets.FashionMNIST(
        root=root,
        train=False,
        download=True,
        transform=ToTensor()
    )
