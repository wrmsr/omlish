import torch


def get_device(no_accel=False):
    if not no_accel:
        if torch.cuda.is_available():
            # from .model.transformer import Transformer, MultiHeadAttention, fast_sdpa
            # Transformer.fast_style_mask = True
            # MultiHeadAttention.sdpa = staticmethod(fast_sdpa)
            return torch.device('cuda')
        if torch.backends.mps.is_available():
            return torch.device('mps')
    return torch.device('cpu')
