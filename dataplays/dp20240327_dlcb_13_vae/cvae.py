import functools
import os.path  # noqa

from keras import backend as K
from keras.callbacks import EarlyStopping
from keras.datasets import mnist
from keras.layers import Input, Dense, Lambda
from keras.layers import concatenate as concat
from keras.models import Model
from keras.optimizers.legacy import Adam  # https://stackoverflow.com/a/75596562
from keras.utils import to_categorical
import PIL
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


"""
__________________________________________________________________________________________________
 Layer (type)                Output Shape                 Param #   Connected to                  
==================================================================================================
 input_3 (InputLayer)        [(None, 784)]                0         []                            
                                                                                                  
 label (InputLayer)          [(None, 10)]                 0         []                            
                                                                                                  
 inputs (Concatenate)        (None, 794)                  0         ['input_3[0][0]',             
                                                                     'label[0][0]']               
                                                                                                  
 encoder_hidden (Dense)      (None, 512)                  407040    ['inputs[0][0]']              
                                                                                                  
 dense_5 (Dense)             (None, 2)                    1026      ['encoder_hidden[0][0]']      
                                                                                                  
 dense_6 (Dense)             (None, 2)                    1026      ['encoder_hidden[0][0]']      
                                                                                                  
 lambda_1 (Lambda)           (250, 2)                     0         ['dense_5[0][0]',             
                                                                     'dense_6[0][0]']             
                                                                                                  
 concatenate (Concatenate)   (250, 12)                    0         ['lambda_1[0][0]',            
                                                                     'label[0][0]']               
                                                                                                  
 dense_7 (Dense)             multiple                     6656      ['concatenate[0][0]']         
                                                                                                  
 dense_8 (Dense)             multiple                     402192    ['dense_7[1][0]']             
                                                                                                  
==================================================================================================
Total params: 817940 (3.12 MB)
Trainable params: 817940 (3.12 MB)
Non-trainable params: 0 (0.00 Byte)
__________________________________________________________________________________________________
"""
def ConditionalVariationalAutoEncoder(batch_size, latent_space_depth, num_pixels, num_labels):
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

    z = Lambda(
        functools.partial(sample_z, batch_size, latent_space_depth),
        output_shape=(latent_space_depth,),
    )([z_mean, z_log_var])
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


def _main() -> None:
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

    cond_auto_encoder, cond_decoder = ConditionalVariationalAutoEncoder(
        batch_size,
        latent_space_depth,
        x_train.shape[1],
        y_train.shape[1],
    )
    cond_auto_encoder.summary()

    ##

    cond_auto_encoder.fit(
        [x_train, y_train],
        x_train,
        verbose=1,
        batch_size=batch_size,
        epochs=50,
        validation_data=([x_test, y_test], x_test),
    )

    ##

    number_4 = np.zeros((1, latent_space_depth + y_train.shape[1]))
    number_4[:, 4 + latent_space_depth] = 1
    decode_img(cond_decoder.predict(number_4).reshape(
        img_width, img_height)).resize((56, 56)).show()

    ##

    number_8_3 = np.zeros((1, latent_space_depth + y_train.shape[1]))
    number_8_3[:, 8 + latent_space_depth] = 0.5
    number_8_3[:, 3 + latent_space_depth] = 0.5
    decode_img(cond_decoder.predict(number_8_3).reshape(
        img_width, img_height)).resize((56, 56)).show()

    ##

    digits = [3, 0, 8, 9]
    num_cells = 10

    overview = PIL.Image.new(
        'RGB',
        (
            num_cells * (img_width + 4) + 8,
            num_cells * (img_height + 4) + 8,
        ),
        (128, 128, 128),
    )

    vec = np.zeros((1, latent_space_depth + y_train.shape[1]))
    for x in range(num_cells):
        x1 = [x / (num_cells - 1), 1 - x / (num_cells - 1)]
        for y in range(num_cells):
            y1 = [y / (num_cells - 1), 1 - y / (num_cells - 1)]
            for idx, dig in enumerate(digits):
                vec[:, dig + latent_space_depth] = x1[idx % 2] * y1[idx // 2]
            decoded = cond_decoder.predict(vec)
            img = decode_img(decoded.reshape(img_width, img_height))
            overview.paste(img, (x * (img_width + 4) + 6, y * (img_height + 4) + 6))

    overview.show()

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

    for x in range(num_cells):
        vec = np.zeros((1, latent_space_depth + y_train.shape[1]))
        vec[:, x + latent_space_depth] = 1
        for y in range(num_cells):
            vec[:, 1] = 3 * y / (num_cells - 1) - 1.5
            decoded = cond_decoder.predict(vec)
            img = decode_img(decoded.reshape(img_width, img_height))
            overview.paste(img, (x * (img_width + 4) + 6, y * (img_height + 4) + 6))
    overview.show()


if __name__ == '__main__':
    _main()
