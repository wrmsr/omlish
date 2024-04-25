import torch


def precompute_freqs_cis(
        dim: int,
        end: int,
        theta: float = 10000.0,
) -> torch.Tensor:
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2)[: (dim // 2)].float() / dim))
    t = torch.arange(end, device=freqs.device)  # type: ignore
    freqs = torch.outer(t, freqs).float()  # type: ignore
    freqs_cis = torch.polar(torch.ones_like(freqs), freqs)  # complex64
    return freqs_cis


def reshape_for_broadcast(
        freqs_cis: torch.Tensor,
        x: torch.Tensor,
) -> torch.Tensor:
    ndim = x.ndim
    assert 0 <= 1 < ndim
    assert freqs_cis.shape == (x.shape[1], x.shape[-1])
    shape = [d if i == 1 or i == ndim - 1 else 1 for i, d in enumerate(x.shape)]
    return freqs_cis.view(*shape)


def apply_rotary_emb(
        xq: torch.Tensor,
        xk: torch.Tensor,
        freqs_cis: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    xq_ = torch.view_as_complex(xq.float().reshape(*xq.shape[:-1], -1, 2))
    xk_ = torch.view_as_complex(xk.float().reshape(*xk.shape[:-1], -1, 2))
    freqs_cis = reshape_for_broadcast(freqs_cis, xq_)
    xq_out = torch.view_as_real(xq_ * freqs_cis).flatten(3)
    xk_out = torch.view_as_real(xk_ * freqs_cis).flatten(3)
    return xq_out.type_as(xq), xk_out.type_as(xk)


def _main() -> None:
    torch.set_printoptions(threshold=10_000, linewidth=10_000, sci_mode=False)

    dim = 64
    max_context = 64
    n_heads = 4

    cis = precompute_freqs_cis(dim // n_heads, max_context * 2)  # (128, 8)
    print(cis)

    n = 4
    q = k = torch.full((n, dim), 1.)

    rq, rk = apply_rotary_emb(k.unsqueeze(0), q.unsqueeze(0), cis)
    rq, rk = rq.squeeze(), rk.squeeze()
    rqn, rkn = rq.numpy(), rk.numpy()
    print(rq)
    print(rk)


if __name__ == '__main__':
    _main()
