import collections
import json
import random
import typing as ta

from omlish import cached
from omlish import dataclasses as dc
import keras
import numpy as np


@dc.dataclass(frozen=True)
class Movie:
    name: str
    dct: ta.Mapping[str, ta.Any]
    links: ta.Sequence[str]
    rat_pct: str
    rat_10: str


class MovieReqs:
    @cached.nullary
    def movies(self) -> ta.Sequence[Movie]:
        movies = []
        with open('../../../../DOsinga/deep_learning_cookbook/data/wp_movies_10k.ndjson', 'r') as f:
            for l in f.readlines():
                movies.append(Movie(*json.loads(l)))
        return movies

    @cached.nullary
    def top_links(self) -> ta.Sequence[str]:
        link_counts = collections.Counter()
        for movie in self.movies():
            link_counts.update(movie.links)
        return [link for link, c in link_counts.items() if c >= 3]

    @cached.nullary
    def link_to_idx(self) -> ta.Mapping[str, int]:
        return {link: idx for idx, link in enumerate(self.top_links())}

    @cached.nullary
    def movie_to_idx(self) -> ta.Mapping[str, int]:
        return {movie.name: idx for idx, movie in enumerate(self.movies())}

    @cached.nullary
    def pairs(self) -> ta.Sequence[tuple[int, int]]:
        pairs = []
        for movie in self.movies():
            pairs.extend(
                (self.link_to_idx()[link], self.movie_to_idx()[movie.name])
                for link in movie.links
                if link in self.link_to_idx()
            )
        return pairs

    @cached.nullary
    def pairs_set(self) -> ta.AbstractSet[tuple[int, int]]:
        pairs_set = set(self.pairs())
        return pairs_set

    def make_embedding_model(self, embedding_size=50) -> keras.Model:
        link = keras.Input(name='link', shape=(1,))
        movie = keras.Input(name='movie', shape=(1,))
        link_embedding = keras.layers.Embedding(
            name='link_embedding',
            input_dim=len(self.top_links()),
            output_dim=embedding_size,
        )(link)
        movie_embedding = keras.layers.Embedding(

            name='movie_embedding',
            input_dim=len(self.movie_to_idx()),
            output_dim=embedding_size,
        )(movie)
        dot = keras.layers.Dot(
            name='dot_product',
            normalize=True,
            axes=2,
        )([link_embedding, movie_embedding])
        merged = keras.layers.Reshape((1,))(dot)
        model = keras.Model(inputs=[link, movie], outputs=[merged])
        model.compile(optimizer='nadam', loss='mse')
        return model

    def batchify(self, positive_samples=50, negative_ratio=10) -> ta.Iterator:
        batch_size = positive_samples * (1 + negative_ratio)
        batch = np.zeros((batch_size, 3))
        while True:
            for idx, (link_id, movie_id) in enumerate(random.sample(self.pairs(), positive_samples)):
                batch[idx, :] = (link_id, movie_id, 1)
            idx = positive_samples
            while idx < batch_size:
                movie_id = random.randrange(len(self.movie_to_idx()))
                link_id = random.randrange(len(self.top_links()))
                if not (link_id, movie_id) in self.pairs_set():
                    batch[idx, :] = (link_id, movie_id, -1)
                    idx += 1
            np.random.shuffle(batch)
            yield {'link': batch[:, 0], 'movie': batch[:, 1]}, batch[:, 2]


def _main() -> None:
    mr = MovieReqs()

    model = mr.make_embedding_model()

    random.seed(5)

    positive_samples_per_batch = 512

    model.fit_generator(
        mr.batchify(positive_samples=positive_samples_per_batch, negative_ratio=10),
        epochs=15,
        steps_per_epoch=len(mr.pairs()) // positive_samples_per_batch,
        verbose=2
    )


if __name__ == '__main__':
    _main()
