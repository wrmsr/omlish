from ommlx.datasets.library.movies import Movie
from ommlx.datasets.library.movies import MoviesData

from .. import torch as mt


TEST_MOVIES = [
    Movie(
        name=name,
        dct={},
        links=links,
        rat_pct='',
        rat_10='',
    )
    for name, links in [
        ('funny movie', ['funny link']),
        ('scary movie', ['scary link']),

        ('space movie', ['space link']),
        ('western movie', ['western link']),

        ('funny space movie', ['funny link', 'space link']),
        ('scary space movie', ['scary link', 'space link']),

        ('funny western movie', ['funny link', 'western link']),
        ('scary western movie', ['scary link', 'western link']),
    ]
]


def test_torch():
    data = MoviesData(TEST_MOVIES)

    model = mt.make_embedding_model(data, 4)
    mt.train_embedding_model(
        model,
        data,
        positive_samples_per_batch=4,
        negative_ratio=2,
        epoch_size=4,
        report_freq=1,
    )
