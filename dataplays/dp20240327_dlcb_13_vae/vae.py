import os.path

import torchvision.datasets

import numpy as np
from keras.layers import Input, Dense, Lambda
from keras.layers import concatenate as concat
from keras.models import Model
from keras import backend as K
from keras.datasets import mnist
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping
from keras.optimizers import Adam

from io import BytesIO
import PIL


def _main() -> None:
    ds = torchvision.datasets.MNIST(
        root=os.path.join(os.path.dirname(__file__), 'data'),
        download=True,
    )
    print(ds)


    def prepare(images, labels):
        images = images.astype('float32') / 255
        n, w, h = images.shape
        return images.reshape((n, w * h)), to_categorical(labels)


    train, test = mnist.load_data()
    x_train, y_train = prepare(*train)
    x_test, y_test = prepare(*test)
    img_width, img_height = train[0].shape[1:]

    batch_size = 250
    latent_space_depth = 2

    def sample_z(args):
        z_mean, z_log_var = args
        eps = K.random_normal(shape=(batch_size, latent_space_depth), mean=0., stddev=1.)
        return z_mean + K.exp(z_log_var / 2) * eps

    def VariationalAutoEncoder(num_pixels):
        pixels = Input(shape=(num_pixels,))
        encoder_hidden = Dense(512, activation='relu')(pixels)

        z_mean = Dense(latent_space_depth, activation='linear')(encoder_hidden)
        z_log_var = Dense(latent_space_depth, activation='linear')(encoder_hidden)

        def KL_loss(y_true, y_pred):
            return (0.5 * K.sum(K.exp(z_log_var) + K.square(z_mean) - 1 - z_log_var, axis=1))

        def reconstruction_loss(y_true, y_pred):
            return K.sum(K.binary_crossentropy(y_true, y_pred), axis=-1)

        def total_loss(y_true, y_pred):
            return KL_loss(y_true, y_pred) + reconstruction_loss(y_true, y_pred)

        z = Lambda(sample_z, output_shape=(latent_space_depth,))([z_mean, z_log_var])

        decoder_hidden = Dense(512, activation='relu')

        reconstruct_pixels = Dense(num_pixels, activation='sigmoid')

        decoder_in = Input(shape=(latent_space_depth,))
        hidden = decoder_hidden(decoder_in)
        decoder_out = reconstruct_pixels(hidden)
        decoder = Model(decoder_in, decoder_out)

        hidden = decoder_hidden(z)
        outputs = reconstruct_pixels(hidden)
        auto_encoder = Model(pixels, outputs)

        auto_encoder.compile(optimizer=Adam(lr=0.001),
                             loss=total_loss,
                             metrics=[KL_loss, reconstruction_loss])

        return auto_encoder, decoder

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
Epoch 1/100
    """
    auto_encoder, decoder = VariationalAutoEncoder(x_train.shape[1])
    auto_encoder.summary()

    ## FIXME
    # TypeError: You are passing KerasTensor(type_spec=TensorSpec(shape=(), dtype=tf.float32, name=None),
    # name='Placeholder:0', description="created by layer 'tf.cast_2'"), an intermediate Keras symbolic input/output, to
    # a TF API that does not allow registering custom dispatchers, such as `tf.cond`, `tf.function`, gradient tapes, or
    # `tf.map_fn`. Keras Functional model construction only supports TF API calls that *do* support dispatching, such as
    # `tf.math.add` or `tf.reshape`. Other APIs cannot be called directly on symbolic Kerasinputs/outputs. You can work
    # around this limitation by putting the operation in a custom Keras layer `call` and calling that layer on this
    # symbolic input/output.
    auto_encoder.fit(x_train, x_train, verbose=1,
                     batch_size=batch_size, epochs=100,
                     validation_data=(x_test, x_test))

    random_number = np.asarray([[np.random.normal()
                                 for _ in range(latent_space_depth)]])
    def decode_img(a):
        a = np.clip(a * 256, 0, 255).astype('uint8')
        return PIL.Image.fromarray(a)

    decode_img(decoder.predict(random_number).reshape(img_width, img_height)).resize((56, 56))

    num_cells = 10

    overview = PIL.Image.new('RGB',
                             (num_cells * (img_width + 4) + 8,
                              num_cells * (img_height + 4) + 8),
                             (128, 128, 128))

    vec = np.zeros((1, latent_space_depth))
    for x in range(num_cells):
        vec[:, 0] = (x * 3) / (num_cells - 1) - 1.5
        for y in range(num_cells):
            vec[:, 1] = (y * 3) / (num_cells - 1) - 1.5
            decoded = decoder.predict(vec)
            img = decode_img(decoded.reshape(img_width, img_height))
            overview.paste(img, (x * (img_width + 4) + 6, y * (img_height + 4) + 6))


    def ConditionalVariationalAutoEncoder(num_pixels, num_labels):
        pixels = Input(shape=(num_pixels,))
        label = Input(shape=(num_labels,), name='label')

        inputs = concat([pixels, label], name='inputs')

        encoder_hidden = Dense(512, activation='relu', name='encoder_hidden')(inputs)

        z_mean = Dense(latent_space_depth, activation='linear')(encoder_hidden)
        z_log_var = Dense(latent_space_depth, activation='linear')(encoder_hidden)

        def KL_loss(y_true, y_pred):
            return (0.5 * K.sum(K.exp(z_log_var) + K.square(z_mean) - 1 - z_log_var, axis=1))

        def reconstruction_loss(y_true, y_pred):
            return K.sum(K.binary_crossentropy(y_true, y_pred), axis=-1)

        def total_loss(y_true, y_pred):
            return KL_loss(y_true, y_pred) + reconstruction_loss(y_true, y_pred)

        z = Lambda(sample_z, output_shape=(latent_space_depth,))([z_mean, z_log_var])
        zc = concat([z, label])

        decoder_hidden = Dense(512, activation='relu')

        reconstruct_pixels = Dense(num_pixels, activation='sigmoid')

        decoder_in = Input(shape=(latent_space_depth + num_labels,))
        hidden = decoder_hidden(decoder_in)
        decoder_out = reconstruct_pixels(hidden)
        decoder = Model(decoder_in, decoder_out)

        hidden = decoder_hidden(zc)
        outputs = reconstruct_pixels(hidden)
        auto_encoder = Model([pixels, label], outputs)

        auto_encoder.compile(optimizer=Adam(lr=0.001),
                             loss=total_loss,
                             metrics=[KL_loss, reconstruction_loss])

        return auto_encoder, decoder

    cond_auto_encoder, cond_decoder = ConditionalVariationalAutoEncoder(x_train.shape[1], y_train.shape[1])
    cond_auto_encoder.summary()

    cond_auto_encoder.fit([x_train, y_train], x_train, verbose=1,
                          batch_size=batch_size, epochs=50,
                          validation_data = ([x_test, y_test], x_test))


if __name__ == '__main__':
    _main()
