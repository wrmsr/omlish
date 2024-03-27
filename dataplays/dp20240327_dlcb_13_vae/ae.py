import struct

from omlish import lang

import PIL.Image
import PIL.ImageDraw
import keras.layers as kl
import keras.models as km
import keras.preprocessing.image
import keras.utils
import numpy as np
import sklearn.model_selection


DATA_URL = 'https://storage.googleapis.com/quickdraw_dataset/full/binary/'


@lang.cached_nullary
def get_data_path() -> str:
    return keras.utils.get_file('cat', DATA_URL + 'cat.bin')


def load_icons(path, train_size=0.85):
    x = []
    with open(path, 'rb') as f:
        while True:
            img = PIL.Image.new('L', (32, 32), 'white')
            draw = PIL.ImageDraw.Draw(img)
            header = f.read(15)
            if len(header) != 15:
                break
            strokes, = struct.unpack('H', f.read(2))
            for i in range(strokes):
                n_points, = struct.unpack('H', f.read(2))
                fmt = str(n_points) + 'B'
                read_scaled = lambda: (p // 8 for p in struct.unpack(fmt, f.read(n_points)))
                points = [*zip(read_scaled(), read_scaled())]
                draw.line(points, fill=0, width=2)
            img = keras.preprocessing.image.img_to_array(img)
            x.append(img)
    x = np.asarray(x) / 255
    return sklearn.model_selection.train_test_split(x, train_size=train_size)


def create_autoencoder():
    input_img = kl.Input(shape=(32, 32, 1))

    channels = 2
    x = input_img
    for i in range(4):
        channels *= 2
        left = kl.Conv2D(channels, (3, 3), activation='relu', padding='same')(x)
        right = kl.Conv2D(channels, (2, 2), activation='relu', padding='same')(x)
        conc = kl.Concatenate()([left, right])
        x = kl.MaxPooling2D((2, 2), padding='same')(conc)

    x = kl.Dense(channels)(x)

    for i in range(4):
        x = kl.Conv2D(channels, (3, 3), activation='relu', padding='same')(x)
        x = kl.UpSampling2D((2, 2))(x)
        channels //= 2
    decoded = kl.Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)

    autoencoder = km.Model(input_img, decoded)
    autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')
    return autoencoder


def _main() -> None:
    x_train, x_test = load_icons(get_data_path())
    print((x_train.shape, x_test.shape))

    autoencoder = create_autoencoder()
    autoencoder.summary()


if __name__ == '__main__':
    _main()
