import keras

from .batches import batchify
from .movies import MoviesData


def make_embedding_model(
        data: MoviesData,
        embedding_size: int = 50,
) -> keras.Model:
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
        input_dim=len(data.top_links),
        output_dim=embedding_size,
    )(link)
    movie_embedding = keras.layers.Embedding(
        name='movie_embedding',
        input_dim=len(data.movie_to_idx),
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


def train_embedding_model(
        model: keras.Model,
        data: MoviesData,
) -> keras.Model:
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

    positive_samples_per_batch = 512
    batches = batchify(
        data,
        positive_samples=positive_samples_per_batch,
        negative_ratio=10,
    )

    model.fit(
        batches,
        epochs=15,
        steps_per_epoch=len(data.pairs) // positive_samples_per_batch,
        verbose=2
    )

    return model
