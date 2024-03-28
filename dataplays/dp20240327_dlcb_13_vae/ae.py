import io
import os.path
import struct

import PIL.Image
import PIL.ImageDraw
import keras.callbacks
import keras.layers as kl
import keras.models as km
import keras.preprocessing.image
import keras.utils
import numpy as np
import sklearn.model_selection
import torch
import torch.nn as nn
import torch.nn.functional as F

from omlish import lang


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

"""
 input_1 (InputLayer)        [(None, 32, 32, 1)]          0         []                            
 
n=0 f=4  ic=1  oc=4
 conv2d (Conv2D)             (None, 32, 32, 4)            40        ['input_1[0][0]']             
 conv2d_1 (Conv2D)           (None, 32, 32, 4)            20        ['input_1[0][0]']             
 concatenate (Concatenate)   (None, 32, 32, 8)            0         ['conv2d[0][0]','conv2d_1[0][0]']            
 max_pooling2d (MaxPooling2  (None, 16, 16, 8)            0         ['concatenate[0][0]']         
 
n=1 f=8  ic=8  oc=16
 conv2d_2 (Conv2D)           (None, 16, 16, 8)            584       ['max_pooling2d[0][0]']       
 conv2d_3 (Conv2D)           (None, 16, 16, 8)            264       ['max_pooling2d[0][0]']       
 concatenate_1 (Concatenate  (None, 16, 16, 16)           0         ['conv2d_2[0][0]','conv2d_3[0][0]']            
 max_pooling2d_1 (MaxPoolin  (None, 8, 8, 16)             0         ['concatenate_1[0][0]']       
 
n=2 f=16 ic=32
 conv2d_4 (Conv2D)           (None, 8, 8, 16)             2320      ['max_pooling2d_1[0][0]']     
 conv2d_5 (Conv2D)           (None, 8, 8, 16)             1040      ['max_pooling2d_1[0][0]']     
 concatenate_2 (Concatenate  (None, 8, 8, 32)             0         ['conv2d_4[0][0]','conv2d_5[0][0]']            
 max_pooling2d_2 (MaxPoolin  (None, 4, 4, 32)             0         ['concatenate_2[0][0]']       
 
n=3 f=32
 conv2d_6 (Conv2D)           (None, 4, 4, 32)             9248      ['max_pooling2d_2[0][0]']     
 conv2d_7 (Conv2D)           (None, 4, 4, 32)             4128      ['max_pooling2d_2[0][0]']     
 concatenate_3 (Concatenate  (None, 4, 4, 64)             0         ['conv2d_6[0][0]','conv2d_7[0][0]']            
 max_pooling2d_3 (MaxPoolin  (None, 2, 2, 64)             0         ['concatenate_3[0][0]']       
 
 dense (Dense)               (None, 2, 2, 32)             2080      ['max_pooling2d_3[0][0]']     
 
 conv2d_8 (Conv2D)           (None, 2, 2, 32)             9248      ['dense[0][0]']               
 up_sampling2d (UpSampling2  (None, 4, 4, 32)             0         ['conv2d_8[0][0]']            
 
 conv2d_9 (Conv2D)           (None, 4, 4, 16)             4624      ['up_sampling2d[0][0]']       
 up_sampling2d_1 (UpSamplin  (None, 8, 8, 16)             0         ['conv2d_9[0][0]']            
 
 conv2d_10 (Conv2D)          (None, 8, 8, 8)              1160      ['up_sampling2d_1[0][0]']     
 up_sampling2d_2 (UpSamplin  (None, 16, 16, 8)            0         ['conv2d_10[0][0]']           
 
 conv2d_11 (Conv2D)          (None, 16, 16, 4)            292       ['up_sampling2d_2[0][0]']     
 up_sampling2d_3 (UpSamplin  (None, 32, 32, 4)            0         ['conv2d_11[0][0]']           
 
 conv2d_12 (Conv2D)          (None, 32, 32, 1)            37        ['up_sampling2d_3[0][0]']     

n=0 f=4  ic=1  oc=4
n=1 f=8  ic=8  oc=16
n=2 f=16 ic=32
n=3 f=32

n=0 f=32
n=1 f=16
n=2 f=8
n=3 f=4
"""

class TorchAutoencoder(nn.Module):
    class InLayer(nn.Module):
        def __init__(self, ic: int, oc: int) -> None:
            super().__init__()
            self.left = nn.Conv2d(ic, oc, kernel_size=(3, 3), padding='same')
            self.right = nn.Conv2d(ic, oc, kernel_size=(2, 2), padding='same')

        def forward(self, x):
            left = F.relu(self.left(x))
            right = F.relu(self.right(x))
            conc = torch.concat([left, right], dim=1)
            x = F.max_pool2d(conc, (2, 2))
            return x

    class OutLayer(nn.Module):
        def __init__(self, ic: int, oc: int) -> None:
            super().__init__()
            self.conv = nn.Conv2d(ic, oc, kernel_size=(3, 3), padding='same')

        def forward(self, x):
            x = F.relu(self.conv(x))
            x = F.upsample(x, scale_factor=2)
            return x

    def __init__(self) -> None:
        super().__init__()
        self.ins = [
            TorchAutoencoder.InLayer(1, 4),
            TorchAutoencoder.InLayer(8, 8),
            TorchAutoencoder.InLayer(16, 16),
            TorchAutoencoder.InLayer(32, 32),
        ]
        self.dense = nn.Linear(64, 32)
        self.outs = [
            TorchAutoencoder.OutLayer(32, 32),
            TorchAutoencoder.OutLayer(32, 16),
            TorchAutoencoder.OutLayer(16, 8),
            TorchAutoencoder.OutLayer(8, 4),
        ]
        self.decode = nn.Conv2d(4, 1, kernel_size=(3, 3), padding='same')

    def forward(self, x):
        for l in self.ins:
            x = l(x)
        x = self.dense(x.permute(0, 2, 3, 1)).permute(0, 3, 1, 2)
        for l in self.outs:
            x = l(x)
        x = F.sigmoid(self.decode(x))
        return x


def create_autoencoder():
    input_img = kl.Input(shape=(32, 32, 1))

    filters = 2
    x = input_img
    for i in range(4):
        filters *= 2
        left = kl.Conv2D(filters, (3, 3), activation='relu', padding='same')(x)
        right = kl.Conv2D(filters, (2, 2), activation='relu', padding='same')(x)
        conc = kl.Concatenate()([left, right])
        x = kl.MaxPooling2D((2, 2), padding='same')(conc)

    x = kl.Dense(filters)(x)

    for i in range(4):
        x = kl.Conv2D(filters, (3, 3), activation='relu', padding='same')(x)
        x = kl.UpSampling2D((2, 2))(x)
        filters //= 2
    decoded = kl.Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)

    autoencoder = km.Model(input_img, decoded)
    autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')
    return autoencoder


def show_generates(autoencoder, x_test, cols=25, rand=True) -> None:
    if rand:
        idx = np.random.randint(x_test.shape[0], size=cols)
    else:
        idx = range(cols)
    sample = x_test[idx]
    decoded_imgs = autoencoder.predict(sample)

    def decode_img(tile, factor=1.0):
        tile = tile.reshape(tile.shape[:-1])
        tile = np.clip(tile * 255, 0, 255)
        return PIL.Image.fromarray(tile)

    overview = PIL.Image.new('RGB', (cols * 32, 64 + 20), (128, 128, 128))
    for idx in range(cols):
        overview.paste(decode_img(sample[idx]), (idx * 32, 5))
        overview.paste(decode_img(decoded_imgs[idx]), (idx * 32, 42))
    f = io.BytesIO()
    overview.save(f, 'png')
    img = PIL.Image.open(io.BytesIO(f.getvalue()))
    img.show()


def _main() -> None:
    autoencoder = create_autoencoder()
    autoencoder.summary()

    tn = TorchAutoencoder()

    x_train_fp = os.path.join(os.path.dirname(__file__), 'ae_x_train.npy')
    x_test_fp = os.path.join(os.path.dirname(__file__), 'ae_x_test.npy')
    if os.path.exists(x_train_fp):
        assert os.path.exists(x_test_fp)
        x_train = np.load(x_train_fp)
        x_test = np.load(x_test_fp)
    else:
        x_train, x_test = load_icons(get_data_path())
        np.save(x_train_fp, x_train)
        np.save(x_test_fp, x_test)
    print((x_train.shape, x_test.shape))

    print(tn(torch.tensor(x_train[0]).reshape(1, 1, 32, 32)).detach().numpy())

    class ShowGenerationsCallback(keras.callbacks.Callback):
        def __init__(self, n):
            super().__init__()
            self.n = n
        def on_epoch_end(self, epoch, logs=None):
            if epoch % self.n == 0:
                show_generates(autoencoder, x_test, rand=False)

    autoencoder.fit(
        x_train,
        x_train,
        epochs=1_000,
        batch_size=256,
        shuffle=True,
        validation_data=(x_test, x_test),
        callbacks=[
            keras.callbacks.TensorBoard(log_dir='/tmp/autoencoder'),
            ShowGenerationsCallback(5),
        ],
    )


if __name__ == '__main__':
    _main()
