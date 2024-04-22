import torch


def get_device(no_accel=False):
    if not no_accel:
        if torch.cuda.is_available():
            return torch.device('cuda')
        if torch.backends.mps.is_available():
            return torch.device('mps')
    return torch.device('cpu')
