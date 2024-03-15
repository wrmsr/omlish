
from pathlib import Path
import requests

DATA_PATH = Path("data")
PATH = DATA_PATH / "mnist"

PATH.mkdir(parents=True, exist_ok=True)

URL = "https://github.com/pytorch/tutorials/raw/main/_static/"
FILENAME = "mnist.pkl.gz"

if not (PATH / FILENAME).exists():
    content = requests.get(URL + FILENAME).content
    (PATH / FILENAME).open("wb").write(content)

###############################################################################
# This dataset is in numpy array format, and has been stored using pickle,
# a python-specific format for serializing data.

import pickle
import gzip

with gzip.open((PATH / FILENAME).as_posix(), "rb") as f:
    (x_train, y_train), (x_valid, y_valid), _ = pickle.load(f, encoding="latin-1")

###############################################################################
# Each image is 28 x 28, and is being stored as a flattened row of length
# 784 (=28x28). Let's take a look at one; we need to reshape it to 2d
# first.

from matplotlib import pyplot
import numpy as np

# pyplot.imshow(x_train[0].reshape((28, 28)), cmap="gray")
# # ``pyplot.show()`` only if not on Colab
# try:
#     import google.colab
# except ImportError:
#     pyplot.show()
# print(x_train.shape)

###############################################################################
# PyTorch uses ``torch.tensor``, rather than numpy arrays, so we need to
# convert our data.

import torch

x_train, y_train, x_valid, y_valid = map(torch.tensor, (x_train, y_train, x_valid, y_valid))
n, c = x_train.shape
# print(x_train, y_train)
# print(x_train.shape)
# print(y_train.min(), y_train.max())

###############################################################################
# Neural net from scratch (without ``torch.nn``)
# -----------------------------------------------
#
# Let's first create a model using nothing but PyTorch tensor operations. We're assuming
# you're already familiar with the basics of neural networks. (If you're not, you can
# learn them at `course.fast.ai <https://course.fast.ai>`_).
#
# PyTorch provides methods to create random or zero-filled tensors, which we will
# use to create our weights and bias for a simple linear model. These are just regular
# tensors, with one very special addition: we tell PyTorch that they require a
# gradient. This causes PyTorch to record all of the operations done on the tensor,
# so that it can calculate the gradient during back-propagation *automatically*!
#
# For the weights, we set ``requires_grad`` **after** the initialization, since we
# don't want that step included in the gradient. (Note that a trailing ``_`` in
# PyTorch signifies that the operation is performed in-place.)
#
# .. note:: We are initializing the weights here with
#    `Xavier initialisation <http://proceedings.mlr.press/v9/glorot10a/glorot10a.pdf>`_
#    (by multiplying with ``1/sqrt(n)``).

import math

weights = torch.randn(784, 10) / math.sqrt(784)
weights.requires_grad_()
bias = torch.zeros(10, requires_grad=True)

###############################################################################
# Thanks to PyTorch's ability to calculate gradients automatically, we can
# use any standard Python function (or callable object) as a model! So
# let's just write a plain matrix multiplication and broadcasted addition
# to create a simple linear model. We also need an activation function, so
# we'll write `log_softmax` and use it. Remember: although PyTorch
# provides lots of prewritten loss functions, activation functions, and
# so forth, you can easily write your own using plain python. PyTorch will
# even create fast GPU or vectorized CPU code for your function
# automatically.

def log_softmax(x):
    return x - x.exp().sum(-1).log().unsqueeze(-1)

def model(xb):
    return log_softmax(xb @ weights + bias)

######################################################################################
# In the above, the ``@`` stands for the matrix multiplication operation. We will call
# our function on one batch of data (in this case, 64 images).  This is
# one *forward pass*.  Note that our predictions won't be any better than
# random at this stage, since we start with random weights.

bs = 64  # batch size

xb = x_train[0:bs]  # a mini-batch from x
preds = model(xb)  # predictions
print(preds[0])
print(preds.shape)

###############################################################################
# As you see, the ``preds`` tensor contains not only the tensor values, but also a
# gradient function. We'll use this later to do backprop.
#
# Let's implement negative log-likelihood to use as the loss function
# (again, we can just use standard Python):

def nll(input, target):
    return -input[range(target.shape[0]), target].mean()

loss_func = nll

###############################################################################
# Let's check our loss with our random model, so we can see if we improve
# after a backprop pass later.

yb = y_train[0:bs]
print(loss_func(preds, yb))

# Let's also implement a function to calculate the accuracy of our model.
# For each prediction, if the index with the largest value matches the
# target value, then the prediction was correct.

def accuracy(out, yb):
    preds = torch.argmax(out, dim=1)
    return (preds == yb).float().mean()

###############################################################################
# Let's check the accuracy of our random model, so we can see if our
# accuracy improves as our loss improves.

print(accuracy(preds, yb))

###############################################################################
# We can now run a training loop.  For each iteration, we will:
#
# - select a mini-batch of data (of size ``bs``)
# - use the model to make predictions
# - calculate the loss
# - ``loss.backward()`` updates the gradients of the model, in this case, ``weights``
#   and ``bias``.
#
# We now use these gradients to update the weights and bias.  We do this
# within the ``torch.no_grad()`` context manager, because we do not want these
# actions to be recorded for our next calculation of the gradient.  You can read
# more about how PyTorch's Autograd records operations
# `here <https://pytorch.org/docs/stable/notes/autograd.html>`_.
#
# We then set the
# gradients to zero, so that we are ready for the next loop.
# Otherwise, our gradients would record a running tally of all the operations
# that had happened (i.e. ``loss.backward()`` *adds* the gradients to whatever is
# already stored, rather than replacing them).
#
# .. tip:: You can use the standard python debugger to step through PyTorch
#    code, allowing you to check the various variable values at each step.
#    Uncomment ``set_trace()`` below to try it out.
#

lr = 0.5  # learning rate
epochs = 2  # how many epochs to train for

for epoch in range(epochs):
    for i in range((n - 1) // bs + 1):
        #         set_trace()
        start_i = i * bs
        end_i = start_i + bs
        xb = x_train[start_i:end_i]
        yb = y_train[start_i:end_i]
        pred = model(xb)
        loss = loss_func(pred, yb)

        loss.backward()
        with torch.no_grad():
            weights -= weights.grad * lr
            bias -= bias.grad * lr
            weights.grad.zero_()
            bias.grad.zero_()

    print(loss)

###############################################################################
# That's it: we've created and trained a minimal neural network (in this case, a
# logistic regression, since we have no hidden layers) entirely from scratch!
#
# Let's check the loss and accuracy and compare those to what we got
# earlier. We expect that the loss will have decreased and accuracy to
# have increased, and they have.

print(loss_func(model(xb), yb))
print(accuracy(model(xb), yb))
