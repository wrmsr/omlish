import random
import typing as ta

import numpy as np

from ommlx.datasets.library.movies import MoviesData


def batchify(
        data: MoviesData,
        *,
        positive_samples: int = 50,
        negative_ratio: int = 10,
) -> ta.Iterator:
    batch_size = positive_samples * (1 + negative_ratio)
    batch = np.zeros((batch_size, 3), dtype=int)
    while True:
        for idx, (link_id, movie_id) in enumerate(random.sample(data.pairs, positive_samples)):
            batch[idx, :] = (link_id, movie_id, 1)
        idx = positive_samples
        while idx < batch_size:
            movie_id = random.randrange(len(data.movie_to_idx))
            link_id = random.randrange(len(data.top_links))
            if not (link_id, movie_id) in data.pairs_set:
                batch[idx, :] = (link_id, movie_id, -1)
                idx += 1
        np.random.shuffle(batch)
        yield {'link': batch[:, 0], 'movie': batch[:, 1]}, batch[:, 2]
