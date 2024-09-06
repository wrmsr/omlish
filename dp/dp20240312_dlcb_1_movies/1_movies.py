import os.path
import pprint as pp
import random

import numpy as np
import sklearn.svm

from ommlx.datasets.library.movies import Movie
from ommlx.datasets.library.movies import MoviesData
from ommlx.datasets.library.movies import load_movies

from . import keras as mk  # noqa
from . import torch as mt  # noqa


def _main() -> None:
    random.seed(5)

    ##

    cache_dir = os.path.join(os.path.dirname(__file__), 'data')
    data = MoviesData(load_movies(cache_dir))

    # be = mk
    be = mt

    if be is mk:
        model = mk.make_embedding_model(data)
        mk.train_embedding_model(model, data)

        movie_weights = model.get_layer('movie_embedding').get_weights()[0]
        link_weights = model.get_layer('link_embedding').get_weights()[0]

    elif be is mt:
        model = mt.make_embedding_model(data)
        mt.train_embedding_model(model, data, lr=.01)

        movie_weights = model.movie_embedding.weight.detach().cpu().numpy()
        link_weights = model.link_embedding.weight.detach().cpu().numpy()

    else:
        raise TypeError(be)

    ##

    movie_lengths = np.linalg.norm(movie_weights, axis=1)
    normalized_movies = (movie_weights.T / movie_lengths).T

    def similar_movies(movie, n=10):
        dists = np.dot(normalized_movies, normalized_movies[data.movie_to_idx[movie]])
        return np.argsort(dists)[-n:][::-1]

    pp.pprint(similar_movies('Rogue One'))
    print()

    ##

    link_lengths = np.linalg.norm(link_weights, axis=1)
    normalized_links = (link_weights.T / link_lengths).T

    def similar_links(link, n=10):
        dists = np.dot(normalized_links, normalized_links[data.link_to_idx[link]])
        return np.argsort(dists)[-n:][::-1]

    pp.pprint(similar_links('George Lucas'))
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
    y = np.asarray([1 for _ in best] + [0 for _ in worst])
    X = np.asarray([normalized_movies[data.movie_to_idx[movie]] for movie in best + worst])
    pp.pprint(X.shape)
    print()

    clf = sklearn.svm.SVC(kernel='linear')
    clf.fit(X, y)

    ##

    estimated_movie_ratings = clf.decision_function(normalized_movies)
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

    rotten_y = np.asarray([float(movie.rat_pct[:-1]) / 100 for movie in data.movies if movie.rat_pct])
    rotten_X = np.asarray([normalized_movies[data.movie_to_idx[movie.name]] for movie in data.movies if movie.rat_pct])

    training_cut_off = int(len(rotten_X) * 0.8)
    regr = sklearn.linear_model.LinearRegression()
    regr.fit(rotten_X[:training_cut_off], rotten_y[:training_cut_off])

    error = (regr.predict(rotten_X[training_cut_off:]) - rotten_y[training_cut_off:])
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
    gross_X = np.asarray([normalized_movies[data.movie_to_idx[movie.name]] for movie, gr in zip(data.movies, movie_gross) if gr])

    training_cut_off = int(len(gross_X) * 0.8)
    regr = sklearn.linear_model.LinearRegression()
    regr.fit(gross_X[:training_cut_off], gross_y[:training_cut_off])

    ##

    error = (regr.predict(gross_X[training_cut_off:]) - gross_y[training_cut_off:])
    print('mean square error %2.2f' % np.mean(error ** 2))

    error = (np.mean(gross_y[:training_cut_off]) - gross_y[training_cut_off:])
    print('mean square error %2.2f' % np.mean(error ** 2))


if __name__ == '__main__':
    _main()
