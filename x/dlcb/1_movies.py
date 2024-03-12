import collections
import os.path
import pprint as pp
import random
import typing as ta

from omlish import cached
from omlish import dataclasses as dc
import keras
import numpy as np
import sklearn.svm
import torch
import torch.nn.functional as F
import ujson as json


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

    class TorchEmbeddingModel(torch.nn.Module):
        def __init__(self, *, num_links: int, num_movies: int, embedding_size: int) -> None:
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

    def make_torch_embedding_model(self, embedding_size=50):
        return MovieReqs.TorchEmbeddingModel(
            num_links=len(self.top_links()),
            num_movies=len(self.movie_to_idx()),
            embedding_size=embedding_size,
        )

    def make_embedding_model(self, embedding_size=50) -> keras.Model:
        """
        __________________________________________________________________________________________________
         Layer (type)                Output Shape                 Param #   Connected to
        ==================================================================================================
         link (InputLayer)           [(None, 1)]                  0         []

         movie (InputLayer)          [(None, 1)]                  0         []

         link_embedding (Embedding)  (None, 1, 50)                3345650   ['link[0][0]']

         movie_embedding (Embedding  (None, 1, 50)                500000    ['movie[0][0]']


         dot_product (Dot)           (None, 1, 1)                 0         ['link_embedding[0][0]',
                                                                             'movie_embedding[0][0]']

         reshape (Reshape)           (None, 1)                    0         ['dot_product[0][0]']

        ==================================================================================================
        Total params: 3845650 (14.67 MB)
        Trainable params: 3845650 (14.67 MB)
        Non-trainable params: 0 (0.00 Byte)
        __________________________________________________________________________________________________
        """
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
        batch = np.zeros((batch_size, 3), dtype=int)
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

    @cached.nullary
    def trained_model(self) -> keras.Model:
        # fp = '../../.cache/1_movies.keras'
        # if os.path.exists(fp):
        #     return keras.models.load_model(fp)

        model = self.make_embedding_model()

        # import tensorflow as tf
        # tf.keras.utils.plot_model(
        #     model,
        #     to_file='model.png',
        #     show_shapes=True,
        #     show_dtype=True,
        #     show_layer_names=True,
        #     rankdir='TB',
        #     expand_nested=True,
        #     dpi=96,
        #     layer_range=None,
        #     show_layer_activations=True,
        #     show_trainable=True
        # )

        random.seed(5)
        positive_samples_per_batch = 512
        batches = self.batchify(positive_samples=positive_samples_per_batch, negative_ratio=10)

        net = self.make_torch_embedding_model()

        lr = 0.001
        report_freq = 5
        epoch_size = 25000

        optimizer = torch.optim.NAdam(net.parameters(), lr=lr, eps=1e-7)
        loss_fn = torch.nn.MSELoss()

        net.train()

        total_loss = torch.tensor(0.)
        acc = torch.tensor(0)
        count = 0
        i = 0

        # while True:
        #     for batch_dct, labels in batches:
        #         link = torch.tensor(batch_dct['link'], dtype=torch.int32)
        #         movie = torch.tensor(batch_dct['movie'], dtype=torch.int32)
        #         labels = torch.tensor(labels, dtype=torch.float32)
        #
        #         optimizer.zero_grad()
        #
        #         out = net(link, movie)
        #
        #         loss = loss_fn(out, labels)  # cross_entropy(out,labels)
        #         loss.backward()
        #
        #         optimizer.step()
        #
        #         total_loss += loss
        #         count += len(labels)
        #
        #         i += 1
        #         if i % report_freq == 0:
        #             print(f"{count}: loss={loss}")
        #
        #         if epoch_size and count > epoch_size:
        #             break

        model.fit(
            batches,
            epochs=15,
            steps_per_epoch=len(self.pairs()) // positive_samples_per_batch,
            verbose=2
        )

        # model.save(fp)
        return model


def _main() -> None:
    mr = MovieReqs()

    model = mr.trained_model()

    ##

    movie = model.get_layer('movie_embedding')
    movie_weights = movie.get_weights()[0]
    movie_lengths = np.linalg.norm(movie_weights, axis=1)
    normalized_movies = (movie_weights.T / movie_lengths).T

    def similar_movies(movie):
        dists = np.dot(normalized_movies, normalized_movies[mr.movie_to_idx()[movie]])
        closest = np.argsort(dists)[-10:]
        for c in reversed(closest):
            print(c, mr.movies()[c].name, dists[c])

    pp.pprint(similar_movies('Rogue One'))

    ##

    link = model.get_layer('link_embedding')
    link_weights = link.get_weights()[0]
    link_lengths = np.linalg.norm(link_weights, axis=1)
    normalized_links = (link_weights.T / link_lengths).T

    def similar_links(link):
        dists = np.dot(normalized_links, normalized_links[mr.link_to_idx()[link]])
        closest = np.argsort(dists)[-10:]
        for c in reversed(closest):
            print(c, mr.top_links()[c], dists[c])

    pp.pprint(similar_links('George Lucas'))

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
    X = np.asarray([normalized_movies[mr.movie_to_idx()[movie]] for movie in best + worst])
    pp.pprint(X.shape)

    clf = sklearn.svm.SVC(kernel='linear')
    clf.fit(X, y)

    ##

    estimated_movie_ratings = clf.decision_function(normalized_movies)
    best = np.argsort(estimated_movie_ratings)
    print('best:')
    for c in reversed(best[-5:]):
        print(c, mr.movies()[c].name, estimated_movie_ratings[c])

    print('worst:')
    for c in best[:5]:
        print(c, mr.movies()[c].name, estimated_movie_ratings[c])

    ##

    rotten_y = np.asarray([float(movie.rat_pct[:-1]) / 100 for movie in mr.movies() if movie.rat_pct])
    rotten_X = np.asarray([normalized_movies[mr.movie_to_idx()[movie.name]] for movie in mr.movies() if movie.rat_pct])

    TRAINING_CUT_OFF = int(len(rotten_X) * 0.8)
    regr = sklearn.linear_model.LinearRegression()
    regr.fit(rotten_X[:TRAINING_CUT_OFF], rotten_y[:TRAINING_CUT_OFF])

    error = (regr.predict(rotten_X[TRAINING_CUT_OFF:]) - rotten_y[TRAINING_CUT_OFF:])
    print('mean square error %2.2f' % np.mean(error ** 2))

    error = (np.mean(rotten_y[:TRAINING_CUT_OFF]) - rotten_y[TRAINING_CUT_OFF:])
    print('mean square error %2.2f' % np.mean(error ** 2))

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

    movie_gross = [gross(m) for m in mr.movies()]
    movie_gross = np.asarray([gr for gr in movie_gross if gr is not None])
    highest = np.argsort(movie_gross)[-10:]
    for c in reversed(highest):
        print(c, mr.movies()[c].name, movie_gross[c])

    ##

    gross_y = np.asarray([gr for gr in movie_gross if gr])
    gross_X = np.asarray([normalized_movies[mr.movie_to_idx()[movie.name]] for movie, gr in zip(mr.movies(), movie_gross) if gr])

    TRAINING_CUT_OFF = int(len(gross_X) * 0.8)
    regr = sklearn.linear_model.LinearRegression()
    regr.fit(gross_X[:TRAINING_CUT_OFF], gross_y[:TRAINING_CUT_OFF])

    ##

    error = (regr.predict(gross_X[TRAINING_CUT_OFF:]) - gross_y[TRAINING_CUT_OFF:])
    print('mean square error %2.2f' % np.mean(error ** 2))

    error = (np.mean(gross_y[:TRAINING_CUT_OFF]) - gross_y[TRAINING_CUT_OFF:])
    print('mean square error %2.2f' % np.mean(error ** 2))


if __name__ == '__main__':
    _main()
