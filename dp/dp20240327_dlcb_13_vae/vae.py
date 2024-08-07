# import os
# os.environ['TF_USE_LEGACY_KERAS'] = 'True'

import functools
import os.path  # noqa
import time

import tensorflow.keras.backend as K
import tensorflow as tf
import tensorflow.keras.ops as KO
from keras.api.callbacks import EarlyStopping
from keras.api.datasets import mnist
from keras.api.layers import Input, Dense, Lambda
from keras.api.models import Model
from keras.api.optimizers import Adam  # https://stackoverflow.com/a/75596562
from keras.api.utils import to_categorical
import PIL
import keras.api.callbacks
import keras.api.models as km
import numpy as np
import torchvision.datasets  # noqa


def prepare(images, labels):
    images = images.astype('float32') / 255
    n, w, h = images.shape
    return images.reshape((n, w * h)), to_categorical(labels)


def sample_z(batch_size, latent_space_depth, args):
    z_mean, z_log_var = args
    eps = K.random_normal(shape=(batch_size, latent_space_depth), mean=0., stddev=1.)
    return z_mean + K.exp(z_log_var / 2) * eps


def decode_img(a):
    a = np.clip(a * 256, 0, 255).astype('uint8')
    return PIL.Image.fromarray(a)


from keras.api.layers import Layer


class KL_loss(Layer):
    def __init__(self, z_log_var, z_mean):
        super().__init__()
        self.z_log_var = z_log_var
        self.z_mean = z_mean

    def call(self, y_true, y_pred):
        # breakpoint()
        return (0.5 * KO.sum(KO.exp(self.z_log_var) + KO.square(self.z_mean) - 1 - self.z_log_var, axis=1))


class reconstruction_loss(Layer):
    def call(self, y_true, y_pred):
        # breakpoint()
        return K.sum(K.binary_crossentropy(y_true, y_pred), axis=-1)


class total_loss(Layer):
    def __init__(self, kl_loss):
        super().__init__()
        self.kl_loss = kl_loss

    def call(self, y_true, y_pred):
        # breakpoint()
        return self.kl_loss(y_true, y_pred) + reconstruction_loss()(y_true, y_pred)


"""
__________________________________________________________________________________________________
 Layer (type)                Output Shape                 Param #   Connected to                  
==================================================================================================
 input_1 (InputLayer)        [(None, 784)]                0         []                            

 dense (Dense)               (None, 512)                  401920    ['input_1[0][0]']             

 dense_1 (Dense)             (None, 2)                    1026      ['dense[0][0]']               

 dense_2 (Dense)             (None, 2)                    1026      ['dense[0][0]']               

 lambda (Lambda)             (250, 2)                     0         ['dense_1[0][0]',             
                                                                     'dense_2[0][0]']             

 dense_3 (Dense)             multiple                     1536      ['lambda[0][0]']              

 dense_4 (Dense)             multiple                     402192    ['dense_3[1][0]']             

==================================================================================================
Total params: 807700 (3.08 MB)
Trainable params: 807700 (3.08 MB)
Non-trainable params: 0 (0.00 Byte)
__________________________________________________________________________________________________
"""
def VariationalAutoEncoder(batch_size, latent_space_depth, num_pixels):
    pixels = Input(shape=(num_pixels,))
    encoder_hidden = Dense(512, activation='relu')(pixels)

    z_mean = Dense(latent_space_depth, activation='linear')(encoder_hidden)
    z_log_var = Dense(latent_space_depth, activation='linear')(encoder_hidden)

    z = Lambda(
        functools.partial(sample_z, batch_size, latent_space_depth),
        output_shape=(latent_space_depth,),
    )([z_mean, z_log_var])

    decoder_hidden = Dense(512, activation='relu')

    reconstruct_pixels = Dense(num_pixels, activation='sigmoid')

    decoder_in = Input(shape=(latent_space_depth,))
    hidden = decoder_hidden(decoder_in)
    decoder_out = reconstruct_pixels(hidden)
    decoder = Model(decoder_in, decoder_out)

    hidden = decoder_hidden(z)
    outputs = reconstruct_pixels(hidden)
    auto_encoder = Model(pixels, outputs)

    kll = KL_loss(z_log_var, z_mean)
    auto_encoder.compile(
        optimizer=Adam(0.001),
        loss=total_loss(kll),
        metrics=[kll, reconstruction_loss()],
    )

    return auto_encoder, decoder


def calc_KL_loss(z_log_var, z_mean):
    return (0.5 * K.sum(K.exp(z_log_var) + K.square(z_mean) - 1 - z_log_var, axis=1))


def calc_reconstruction_loss(y_true, y_pred):
    return K.sum(K.binary_crossentropy(y_true, y_pred), axis=-1)


def calc_total_loss(y_true, y_pred, z_log_var, z_mean):
    return calc_KL_loss(z_log_var, z_mean) + calc_reconstruction_loss(y_true, y_pred)


LOCAL_DIR = os.path.dirname(__file__)


def _main() -> None:
    in_model_path = None
    # in_model_path = os.path.join(LOCAL_DIR, 'vae_1711652835.5188153')

    # out_model_path = os.path.join(LOCAL_DIR, f'vae_{time.time()}')
    out_model_path = None

    # https://github.com/keras-team/keras/issues/16066#issuecomment-1172622846
    from tensorflow.python.framework.ops import disable_eager_execution  # noqa
    # disable_eager_execution()

    ##

    # ds = torchvision.datasets.MNIST(
    #     root=os.path.join(os.path.dirname(__file__), 'data'),
    #     download=True,
    # )

    ##

    train, test = mnist.load_data()
    x_train, y_train = prepare(*train)
    x_test, y_test = prepare(*test)
    img_width, img_height = train[0].shape[1:]

    batch_size = 250
    latent_space_depth = 2

    ##

    auto_encoder, decoder = VariationalAutoEncoder(
        batch_size,
        latent_space_depth,
        x_train.shape[1],
    )
    if in_model_path and os.path.exists(in_model_path + '_e.keras'):
        auto_encoder.load_weights(in_model_path + '_e.keras')
        decoder.load_weights(in_model_path + '_d.keras')
    auto_encoder.summary()

    ##

    class SaveModelCallback(keras.callbacks.Callback):
        def __init__(self, n, out_path):
            super().__init__()
            self.out_path = out_path
            self.n = n

        def on_epoch_end(self, epoch, logs=None):
            if epoch % self.n == 0:
                auto_encoder.save(self.out_path + '_e.keras')
                decoder.save(self.out_path + '_d.keras')

    auto_encoder.fit(
        x_train,
        x_train,
        verbose=1,
        batch_size=batch_size,
        epochs=100,
        validation_data=(x_test, x_test),
        callbacks=[
            *([SaveModelCallback(10, out_model_path)] if out_model_path else []),
        ],
    )

    ##

    random_number = np.asarray([[np.random.normal() for _ in range(latent_space_depth)]])

    decode_img(decoder.predict(random_number).reshape(img_width, img_height)).resize((56, 56)).show()

    ##

    num_cells = 10

    overview = PIL.Image.new(
        'RGB',
        (
            num_cells * (img_width + 4) + 8,
            num_cells * (img_height + 4) + 8,
        ),
        (128, 128, 128),
    )

    vec = np.zeros((1, latent_space_depth))
    for x in range(num_cells):
        vec[:, 0] = (x * 3) / (num_cells - 1) - 1.5
        for y in range(num_cells):
            vec[:, 1] = (y * 3) / (num_cells - 1) - 1.5
            decoded = decoder.predict(vec)
            img = decode_img(decoded.reshape(img_width, img_height))
            overview.paste(img, (x * (img_width + 4) + 6, y * (img_height + 4) + 6))

    overview.show()


if __name__ == '__main__':
    _main()
