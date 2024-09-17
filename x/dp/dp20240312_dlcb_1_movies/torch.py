import torch
import torch.nn.functional as F

from ommlx import torch as toru
from ommlx.datasets.library.movies import MoviesData

from .batches import batchify


class EmbeddingModel(torch.nn.Module):
    def __init__(
            self,
            *,
            num_links: int,
            num_movies: int,
            embedding_size: int,
    ) -> None:
        super().__init__()

        self.embedding_size = embedding_size
        self.link_embedding = torch.nn.Embedding(
            num_links,
            embedding_size,
        )
        self.movie_embedding = torch.nn.Embedding(
            num_movies,
            embedding_size,
        )

    def forward(self, link, movie):
        le = self.link_embedding.forward(link)
        me = self.movie_embedding.forward(movie)
        le = F.normalize(le, dim=-1)
        me = F.normalize(me, dim=-1)
        dot = torch.bmm(le.view(-1, 1, self.embedding_size), me.view(-1, self.embedding_size, 1))
        merged = dot.reshape(-1)
        return merged


def make_embedding_model(
        data: MoviesData,
        embedding_size: int = 50,
) -> EmbeddingModel:
    return EmbeddingModel(
        num_links=len(data.top_links),
        num_movies=len(data.movie_to_idx),
        embedding_size=embedding_size,
    )


def train_embedding_model(
        model: EmbeddingModel,
        data: MoviesData,
        *,
        num_epochs: int = 1_500,
        positive_samples_per_batch: int = 512,
        negative_ratio: int = 10,
        epoch_size: int = 25000,
        lr: float = .001,
        report_freq: int = 5,
        device: str | None = None,
) -> EmbeddingModel:
    if device is None:
        device = toru.get_best_device()

    batches = batchify(
        data,
        positive_samples=positive_samples_per_batch,
        negative_ratio=negative_ratio,
    )

    optimizer = torch.optim.NAdam(model.parameters(), lr=lr, eps=1e-7)
    loss_fn = torch.nn.MSELoss()

    model.train()
    if device:
        model.to(device)

    total_loss = torch.tensor(0.)
    # acc = torch.tensor(0)
    i = 0

    for e in range(num_epochs):
        print(f'epoch {e} / {num_epochs}')

        count = 0

        for batch_dct, labels in batches:
            link = toru.to(torch.tensor(batch_dct['link'], dtype=torch.int32), device)
            movie = toru.to(torch.tensor(batch_dct['movie'], dtype=torch.int32), device)
            labels = toru.to(torch.tensor(labels, dtype=torch.float32), device)

            optimizer.zero_grad()

            out = model(link, movie)

            loss = loss_fn(out, labels)  # cross_entropy(out,labels)
            loss.backward()

            optimizer.step()

            total_loss += loss.cpu()
            count += len(labels)

            i += 1
            if i % report_freq == 0:
                print(f'{count}: loss={loss}')

            if epoch_size and count > epoch_size:
                break

    return model
