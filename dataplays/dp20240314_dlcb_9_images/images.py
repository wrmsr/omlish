from keras.applications.vgg16 import VGG16
from keras.applications.inception_v3 import InceptionV3
from keras import applications
from keras.preprocessing import image
from keras.applications.vgg19 import preprocess_input

from scipy import ndimage
import matplotlib.pyplot as plt
from PIL import Image
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.imagenet_utils import preprocess_input
import numpy as np


def _main():
    model = VGG16(weights='imagenet', include_top=True)
    print(model.summary())

    img = Image.open('cat.jpg')
    w, h = img.size
    s = min(w, h)
    y = (h - s) // 2
    x = (w - s) // 2
    img = img.crop((x, y, s, s))
    plt.imshow(np.asarray(img))

    target_size = max(x for x in model.layers[0].input_shape[0] if x)
    img = img.resize((target_size, target_size), Image.Resampling.BILINEAR)
    plt.imshow(np.asarray(img))

    np_img = image.img_to_array(img)
    img_batch = np.expand_dims(np_img, axis=0)
    pre_processed = preprocess_input(img_batch)
    print(pre_processed.shape)

    features = model.predict(pre_processed)
    print(features.shape)

    print(decode_predictions(features, top=5))


if __name__ == '__main__':
    _main()
