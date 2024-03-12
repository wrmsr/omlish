import os

os.environ['GUTENBERG_MIRROR'] = 'http://mirrors.xmission.com/gutenberg/'

from gutenberg.acquire import load_etext
from gutenberg.query import get_etexts, get_metadata
from gutenberg.acquire import get_metadata_cache
from gutenberg.acquire.text import UnknownDownloadUriException
from gutenberg.cleanup import strip_headers
from gutenberg._domain_model.exceptions import CacheAlreadyExistsException

from keras import Input, Model
from keras.layers import Dense, Dropout
from keras.layers import LSTM
from keras.layers import TimeDistributed
import keras.callbacks
import keras.backend as K
import scipy.misc
import json

import os, sys
import re
import PIL
from PIL import ImageDraw

from keras.optimizers import RMSprop
import random
import numpy as np
import tensorflow as tf
from keras.utils import get_file

from IPython.display import clear_output, Image, display, HTML
from io import BytesIO


def _main() -> None:
    cache = get_metadata_cache()
    try:
        cache.populate()
    except CacheAlreadyExistsException:
        pass

    shakespeare = strip_headers(load_etext(100))

    training_text = shakespeare.split('\nTHE END', 1)[-1]

    chars = list(sorted(set(training_text)))
    char_to_idx = {ch: idx for idx, ch in enumerate(chars)}

    def char_rnn_model(num_chars, num_layers, num_nodes=512, dropout=0.1):
        input = Input(shape=(None, num_chars), name='input')
        prev = input
        for i in range(num_layers):
            lstm = LSTM(num_nodes, return_sequences=True, name='lstm_layer_%d' % (i + 1))(prev)
            if dropout:
                prev = Dropout(dropout)(lstm)
            else:
                prev = lstm
        dense = TimeDistributed(Dense(num_chars, name='dense', activation='softmax'))(prev)
        model = Model(inputs=[input], outputs=[dense])
        optimizer = RMSprop(lr=0.01)
        model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
        return model

    model = char_rnn_model(len(chars), num_layers=2, num_nodes=640, dropout=0)
    model.summary()

    CHUNK_SIZE = 160

    def data_generator(all_text, char_to_idx, batch_size, chunk_size):
        X = np.zeros((batch_size, chunk_size, len(char_to_idx)))
        y = np.zeros((batch_size, chunk_size, len(char_to_idx)))
        while True:
            for row in range(batch_size):
                idx = random.randrange(len(all_text) - chunk_size - 1)
                chunk = np.zeros((chunk_size + 1, len(char_to_idx)))
                for i in range(chunk_size + 1):
                    chunk[i, char_to_idx[all_text[idx + i]]] = 1
                X[row, :, :] = chunk[:chunk_size]
                y[row, :, :] = chunk[1:]
            yield X, y

    next(data_generator(training_text, char_to_idx, 4, chunk_size=CHUNK_SIZE))

    early = keras.callbacks.EarlyStopping(
        monitor='loss',
        min_delta=0.03,
        patience=3,
        verbose=0,
        mode='auto',
    )

    BATCH_SIZE = 256
    model.fit(
        data_generator(training_text, char_to_idx, batch_size=BATCH_SIZE, chunk_size=CHUNK_SIZE),
        epochs=40,
        callbacks=[early,],
        steps_per_epoch=int(2 * len(training_text) / (BATCH_SIZE * CHUNK_SIZE)),
        verbose=2
    )


if __name__ == '__main__':
    _main()
