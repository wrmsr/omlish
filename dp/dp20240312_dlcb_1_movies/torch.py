import torch
import torch.nn.functional as F

from .batches import batchify
from .movies import MoviesData


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
        num_epochs: int = 15,
) -> EmbeddingModel:
    positive_samples_per_batch = 512
    batches = batchify(
        data,
        positive_samples=positive_samples_per_batch,
        negative_ratio=10,
    )

    lr = .001
    report_freq = 5
    epoch_size = 25000

    optimizer = torch.optim.NAdam(model.parameters(), lr=lr, eps=1e-7)
    loss_fn = torch.nn.MSELoss()

    model.train()

    total_loss = torch.tensor(0.)
    acc = torch.tensor(0)
    count = 0
    i = 0

    for e in range(num_epochs):
        print(f'epoch {e} / {num_epochs}')

        for batch_dct, labels in batches:
            link = torch.tensor(batch_dct['link'], dtype=torch.int32)
            movie = torch.tensor(batch_dct['movie'], dtype=torch.int32)
            labels = torch.tensor(labels, dtype=torch.float32)

            optimizer.zero_grad()

            out = model(link, movie)

            loss = loss_fn(out, labels)  # cross_entropy(out,labels)
            loss.backward()

            optimizer.step()

            total_loss += loss
            count += len(labels)

            i += 1
            if i % report_freq == 0:
                print(f"{count}: loss={loss}")

            if epoch_size and count > epoch_size:
                break

    return model
