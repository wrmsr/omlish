import collections
import os.path
import typing as ta
import urllib.request

from omlish import cached
from omlish import dataclasses as dc
from omlish import lang
import ujson as json


@dc.dataclass(frozen=True)
class Movie:
    name: str
    dct: ta.Mapping[str, ta.Any]
    links: ta.Sequence[str]
    rat_pct: str
    rat_10: str


MOVIES_DATA_URL = 'https://raw.githubusercontent.com/DOsinga/deep_learning_cookbook/04f56a7fe11e16c19ec6269bc5a138efdcb522a7/data/wp_movies_10k.ndjson'  # noqa


@lang.cached_function
def load_movies() -> ta.Sequence[Movie]:
    movies = []

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    data_file = os.path.join(data_dir, 'wp_movies_10k.ndjson')
    if not os.path.isfile(data_file):
        with urllib.request.urlopen(MOVIES_DATA_URL) as resp:
            data = resp.read()
        with open(data_file, 'wb') as f:
            f.write(data)

    with open(data_file) as f:
        for l in f.readlines():
            movies.append(Movie(*json.loads(l)))

    return movies


@dc.dataclass(frozen=True)
class MoviesData:
    movies: ta.Sequence[Movie]

    @cached.property
    def top_links(self) -> ta.Sequence[str]:
        link_counts = collections.Counter()
        for movie in self.movies:
            link_counts.update(movie.links)
        return [link for link, c in link_counts.items() if c >= 3]

    @cached.property
    def link_to_idx(self) -> ta.Mapping[str, int]:
        return {link: idx for idx, link in enumerate(self.top_links)}

    @cached.property
    def movie_to_idx(self) -> ta.Mapping[str, int]:
        return {movie.name: idx for idx, movie in enumerate(self.movies)}

    @cached.property
    def pairs(self) -> ta.Sequence[tuple[int, int]]:
        pairs = []
        for movie in self.movies:
            pairs.extend(
                (self.link_to_idx[link], self.movie_to_idx[movie.name])
                for link in movie.links
                if link in self.link_to_idx
            )
        return pairs

    @cached.property
    def pairs_set(self) -> ta.AbstractSet[tuple[int, int]]:
        pairs_set = set(self.pairs)
        return pairs_set
