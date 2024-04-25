import torch

from . import rotary_embedding_torch as ret


def _main() -> None:
    torch.set_printoptions(threshold=10_000, linewidth=10_000, sci_mode=False)

    h_dim = 32
    re = ret.RotaryEmbedding(h_dim)

    n = 64

    # t = torch.normal(torch.zeros((n, h_dim))).unsqueeze(0)
    # t = (torch.arange(h_dim) / h_dim).repeat(n).reshape(n, h_dim)
    t = torch.full((n, h_dim), 1.)

    rt = re.rotate_queries_or_keys(t.unsqueeze(0)).squeeze(0)
    rtn = rt.numpy()
    print(rt)


if __name__ == '__main__':
    _main()
