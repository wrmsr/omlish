import torch

from . import rotary_embedding_torch as ret


def _main() -> None:
    torch.set_printoptions(threshold=10_000, linewidth=10_000, sci_mode=False)

    h_dim = 16
    re = ret.RotaryEmbedding(h_dim)

    n = 4
    t = torch.normal(torch.zeros((n, h_dim))).unsqueeze(0)

    rt = re.rotate_queries_or_keys(t.unsqueeze(0)).squeeze(0)
    print(rt)


if __name__ == '__main__':
    _main()
