import dataclasses as dc
import os.path
import pprint as pp
import random
import typing as ta

import numpy as np
import sklearn.svm

from ommlx.datasets.library.movies import Movie
from ommlx.datasets.library.movies import MoviesData
from ommlx.datasets.library.movies import load_movies

from . import keras as mk  # noqa
from . import torch as mt  # noqa


##


@dc.dataclass(frozen=True)
class Embeddings:
    movies: np.ndarray  # (len(data.movies), embedding_size)
    links: np.ndarray  # (len(data.top_links), embedding_size)


def build_embeddings(data: MoviesData) -> Embeddings:
    # be = mk
    be = mt

    if be is mk:
        model = mk.make_embedding_model(data)
        mk.train_embedding_model(model, data)

        movie_weights = model.get_layer('movie_embedding').get_weights()[0]
        link_weights = model.get_layer('link_embedding').get_weights()[0]

    elif be is mt:
        model = mt.make_embedding_model(data)
        mt.train_embedding_model(model, data, lr=.01, num_epochs=10)

        movie_weights = model.movie_embedding.weight.detach().cpu().numpy()
        link_weights = model.link_embedding.weight.detach().cpu().numpy()

    else:
        raise TypeError(be)

    movie_lengths = np.linalg.norm(movie_weights, axis=1)
    normalized_movies = (movie_weights.T / movie_lengths).T

    link_lengths = np.linalg.norm(link_weights, axis=1)
    normalized_links = (link_weights.T / link_lengths).T

    return Embeddings(
        normalized_movies,
        normalized_links,
    )


##


def find_closest(emb: np.ndarray, idx: int, n: int = 10) -> list[tuple[int, float]]:
    dists = np.dot(emb, emb[idx])
    closest = np.argsort(dists)[-n:]
    return [
        (c, dists[c])
        for c in reversed(closest)
    ]


##


def build_movie_recommendations(
        data: MoviesData,
        embeddings: Embeddings,
        best: ta.Sequence[str],
        worst: ta.Sequence[str],
) -> np.ndarray:  # (len(data.movies),)
    y = np.asarray(
        [1 for _ in best] +
        [0 for _ in worst]
    )

    x = np.asarray([
        embeddings.movies[data.movie_to_idx[movie]]
        for movie in [*best, *worst]
    ])

    clf = sklearn.svm.SVC(kernel='linear')  # noqa
    clf.fit(x, y)

    return clf.decision_function(embeddings.movies)


##


# def train_linear_model(
#         x: np.ndarray,
#         y: np.ndarray,
#         *,
#         training_cutoff_ratio: float = .8,
# ) -> sklearn.linear_model._base.LinearModel:  # noqa
#     training_cut_off = int(len(x) * training_cutoff_ratio)
#     regr = sklearn.linear_model.LinearRegression()
#     regr.fit(x[:training_cut_off], y[:training_cut_off])
#     return regr


#


def _main() -> None:
    random.seed(5)

    ##

    cache_dir = os.path.join(os.path.dirname(__file__), 'data')
    data = MoviesData(load_movies(cache_dir))

    ##

    embeddings = build_embeddings(data)
    print()

    ##

    target_movie = 'Rogue One'
    pp.pprint([
        (data.movies[c].name, d) for c, d in find_closest(
            embeddings.movies,
            data.movie_to_idx[target_movie],
        )
    ])
    print()

    #

    target_link = 'George Lucas'
    pp.pprint([
        (data.top_links[c], d) for c, d in find_closest(
            embeddings.links,
            data.link_to_idx[target_link],
        )
    ])
    print()

    ##

    best = [
        'Star Wars: The Force Awakens',
        'The Martian (film)',
        'Tangerine (film)',
        'Straight Outta Compton (film)',
        'Brooklyn (film)',
        'Carol (film)',
        'Spotlight (film)',
    ]
    worst = [
        'American Ultra',
        'The Cobbler (2014 film)',
        'Entourage (film)',
        'Fantastic Four (2015 film)',
        'Get Hard',
        'Hot Pursuit (2015 film)',
        'Mortdecai (film)',
        'Serena (2014 film)',
        'Vacation (2015 film)',
    ]

    estimated_movie_ratings = build_movie_recommendations(
        data,
        embeddings,
        best,
        worst,
    )

    best = np.argsort(estimated_movie_ratings)
    print('best:')
    for c in reversed(best[-5:]):
        print((c, data.movies[c].name, estimated_movie_ratings[c]))
    print()

    print('worst:')
    for c in best[:5]:
        print((c, data.movies[c].name, estimated_movie_ratings[c]))
    print()

    ##

    rotten_y = np.asarray([
        float(movie.rat_pct[:-1]) / 100
        for movie in data.movies
        if movie.rat_pct
    ])
    rotten_x = np.asarray([
        embeddings.movies[data.movie_to_idx[movie.name]]
        for movie in data.movies
        if movie.rat_pct
    ])

    training_cut_off = int(len(rotten_x) * 0.8)
    regr = sklearn.linear_model.LinearRegression()
    regr.fit(rotten_x[:training_cut_off], rotten_y[:training_cut_off])

    error = (regr.predict(rotten_x[training_cut_off:]) - rotten_y[training_cut_off:])
    print('mean square error %2.2f' % np.mean(error ** 2))

    error = (np.mean(rotten_y[:training_cut_off]) - rotten_y[training_cut_off:])
    print('mean square error %2.2f' % np.mean(error ** 2))

    print()

    ##

    def gross(movie: Movie) -> float | None:
        v = movie.dct.get('gross')
        if not v or ' ' not in v:
            return None
        v, unit = v.split(' ', 1)
        unit = unit.lower()
        if unit not in ('million', 'billion'):
            return None
        if not v.startswith('$'):
            return None
        try:
            v = float(v[1:])
        except ValueError:
            return None
        if unit == 'billion':
            v *= 1000
        return v

    movie_gross = [gross(m) for m in data.movies]
    movie_gross = np.asarray([gr for gr in movie_gross if gr is not None])
    highest = np.argsort(movie_gross)[-10:]
    for c in reversed(highest):
        print((c, data.movies[c].name, movie_gross[c]))
    print()

    ##

    gross_y = np.asarray([gr for gr in movie_gross if gr])
    gross_x = np.asarray([
        embeddings.movies[data.movie_to_idx[movie.name]]
        for movie, gr in zip(data.movies, movie_gross)
        if gr
    ])

    training_cut_off = int(len(gross_x) * 0.8)
    regr = sklearn.linear_model.LinearRegression()
    regr.fit(gross_x[:training_cut_off], gross_y[:training_cut_off])

    ##

    error = (regr.predict(gross_x[training_cut_off:]) - gross_y[training_cut_off:])
    print('mean square error %2.2f' % np.mean(error ** 2))

    error = (np.mean(gross_y[:training_cut_off]) - gross_y[training_cut_off:])
    print('mean square error %2.2f' % np.mean(error ** 2))


if __name__ == '__main__':
    _main()
