import typing as ta

import pytest

from omlish import lang


if ta.TYPE_CHECKING:
    import torch.nn
    import torch.nn.functional as F  # noqa
else:
    torch = lang.proxy_import('torch', extras=['nn'])
    F = lang.proxy_import('torch.nn.functional')


class SimpleGraphEmbeddingModel(torch.nn.Module):  # FIXME: lol
    def __init__(
            self,
            *,
            num_edges: int,
            num_vertexes: int,
            embedding_size: int,
    ) -> None:
        super().__init__()

        self.embedding_size = embedding_size
        self.edge_embedding = torch.nn.Embedding(
            num_edges,
            embedding_size,
        )
        self.vertex_embedding = torch.nn.Embedding(
            num_vertexes,
            embedding_size,
        )

    def forward(self, edge, vertex):
        edge_emb = self.edge_embedding.forward(edge)
        vert_emb = self.vertex_embedding.forward(vertex)

        edge_emb = F.normalize(edge_emb, dim=-1)
        vert_emb = F.normalize(vert_emb, dim=-1)

        dot = torch.bmm(
            edge_emb.view(-1, 1, self.embedding_size),
            vert_emb.view(-1, self.embedding_size, 1),
        )

        merged = dot.reshape(-1)
        return merged


@pytest.mark.slow
def test_embed():
    pass
