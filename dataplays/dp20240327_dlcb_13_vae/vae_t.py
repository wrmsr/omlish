import functools
import os.path  # noqa
import time

from keras import backend as K
from keras.callbacks import EarlyStopping
from keras.datasets import mnist
from keras.layers import Input, Dense, Lambda
from keras.models import Model
from keras.optimizers.legacy import Adam  # https://stackoverflow.com/a/75596562
from keras.utils import to_categorical
import PIL
import keras.callbacks
import keras.models as km
import numpy as np
import torchvision.datasets  # noqa
import torch
import torch.nn as nn
import torch.nn.functional as F


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


class VAE(nn.Module):
    def __init__(self, latent_space_depth: int, num_pixels: int, hidden_dim: int = 512) -> None:
        super().__init__()
        self.latent_space_depth = latent_space_depth
        self.num_pixels = num_pixels
        self.hidden_dim = hidden_dim

        self.encoder_hidden = nn.Linear(num_pixels, hidden_dim)  # , activation='relu')(pixels)
        self.z_mean = nn.Linear(hidden_dim, latent_space_depth)  # , activation='linear')(encoder_hidden)
        self.z_log_var = nn.Linear(hidden_dim, latent_space_depth)  # , activation='linear')(encoder_hidden)
        self.decoder_hidden = nn.Linear(latent_space_depth, hidden_dim)  # , activation='relu')
        self.reconstruct_pixels = nn.Linear(hidden_dim, num_pixels)  # , activation='sigmoid')

    def kl_loss(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> torch.Tensor:
        return (0.5 * K.sum(z_log_var.exp() + K.square(z_mean) - 1 - z_log_var, axis=1))

    def reconstruction_loss(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> torch.Tensor:
        return K.sum(K.binary_crossentropy(y_true, y_pred), axis=-1)

    def total_loss(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> torch.Tensor:
        return self.kl_loss(y_true, y_pred) + self.reconstruction_loss(y_true, y_pred)


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

    def KL_loss(y_true, y_pred):
        breakpoint()
        return (0.5 * K.sum(K.exp(z_log_var) + K.square(z_mean) - 1 - z_log_var, axis=1))

    def reconstruction_loss(y_true, y_pred):
        breakpoint()
        return K.sum(K.binary_crossentropy(y_true, y_pred), axis=-1)

    def total_loss(y_true, y_pred):
        breakpoint()
        return KL_loss(y_true, y_pred) + reconstruction_loss(y_true, y_pred)

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

    auto_encoder.compile(
        optimizer=Adam(lr=0.001),
        loss=total_loss,
        metrics=[KL_loss, reconstruction_loss],
    )

    return auto_encoder, decoder


LOCAL_DIR = os.path.dirname(__file__)


def _main() -> None:
    in_model_path = None
    # in_model_path = os.path.join(LOCAL_DIR, 'vae_1711652835.5188153')

    # out_model_path = os.path.join(LOCAL_DIR, f'vae_{time.time()}')
    out_model_path = None

    # https://github.com/keras-team/keras/issues/16066#issuecomment-1172622846
    from tensorflow.python.framework.ops import disable_eager_execution
    disable_eager_execution()

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
        ]
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
