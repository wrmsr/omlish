"""
[build-system]
requires = [
    'setuptools',
]
build-backend = 'setuptools.build_meta'


##

[project]
name = 'omlish'
authors = [{name = 'wrmsr'}]
urls = {source = 'https://github.com/wrmsr/omlish'}
license = {text = 'BSD-3-Clause'}
requires-python = '>=3.12'

dynamic = ['version']

description = 'omlish'
classifiers = [
    'License :: OSI Approved :: BSD License',
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',

    'Operating System :: OS Independent',
    'Operating System :: POSIX',
]

[project.optional-dependencies]
async = [
    'anyio',
]

compression=[
    'lz4',
]


##

[tool.setuptools]
include-package-data = false

[tool.setuptools.dynamic]
version = {attr = 'omlish.__about__.__version__'}

[tool.setuptools.packages.find]
include = ['omlish', 'omlish.*']
exclude = ['*.tests', '*.tests.*']

"""

"""
__author__ = 'wrmsr'
__url__ = 'https://github.com/wrmsr/omlish'
__license__ = 'BSD-3-Clause'
__requires_python__ = '>=3.12'

__version__ = '0.0.0.dev7'
"""
