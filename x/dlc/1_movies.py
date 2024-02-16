import collections
import json
import typing as ta

from omlish import cached
from omlish import dataclasses as dc
import keras


class MovieReqs:
    @cached.nullary
    def movies(self) -> ta.Sequence[ta.Any]:
        movies = []
        with open('../../../../DOsinga/deep_learning_cookbook/data/wp_movies_10k.ndjson', 'r') as f:
            for l in f.readlines():
                movies.append(json.loads(l))
        return movies

    @cached.nullary
    def pairs_set(self) -> ta.AbstractSet[tuple[int, int]]:
        link_counts = collections.Counter()
        for m in self.movies():
            link_counts.update(m[2])

        top_links = [link for link, c in link_counts.items() if c >= 3]
        link_to_idx = {link: idx for idx, link in enumerate(top_links)}
        movie_to_idx = {movie[0]: idx for idx, movie in enumerate(movies)}
        pairs = []
        for movie in self.movies():
            pairs.extend(
                (link_to_idx[link], movie_to_idx[movie[0]])
                for link in movie[2]
                if link in link_to_idx
            )
        pairs_set = set(pairs)
        return pairs_set

    @cached.nullary
    def embedding_model(self, embedding_size=50):
        link = keras.Input(name='link', shape=(1,))
        movie = keras.Input(name='movie', shape=(1,))
        link_embedding = keras.layers.Embedding(
            name='link_embedding',
            input_dim=len(top_links),
            output_dim=embedding_size,
        )(link)
        movie_embedding = keras.layers.Embedding(
            name='movie_embedding',
            input_dim=len(movie_to_idx),
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


def _main() -> None:
    mr = MovieReqs()
    print(len(mr.movies()))


if __name__ == '__main__':
    _main()
