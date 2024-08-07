import os.path
cachedir = os.path.join(os.path.dirname(__file__), './cachedir/2')

from .. import Memory
memory = Memory(cachedir, verbose=0)

@memory.cache
def f(x):
    print('Running f(%s)' % x)
    return x

print(f(1))
print(f(1))
print(f(2))

##

import numpy as np

@memory.cache
def g(x):
    print('A long-running calculation, with parameter %s' % x)
    return np.hamming(x)

@memory.cache
def h(x):
    print('A second long-running calculation, using g(x)')
    return np.vander(x)

a = g(3)
print(a)
print(g(3))
b = h(a)
b2 = h(a)
print(b2)
print(np.allclose(b, b2))

##

cachedir2 = os.path.join(os.path.dirname(__file__), './cachedir/3')
memory2 = Memory(cachedir2, mmap_mode='r')
square = memory2.cache(np.square)
a = np.vander(np.arange(3)).astype(float)
print(square(a))

res = square(a)
print(repr(res))

##

result = g.call_and_shelve(4)
print(result)

print(result.get())

result.clear()
result.get()
