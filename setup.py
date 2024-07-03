"""
TODO:
 - https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
"""
import os.path
import sys
import typing as ta

import setuptools as st


PROJECT = 'omlish'


def _read_about(fp: ta.Optional[str] = None) -> ta.Mapping[str, ta.Any]:
    if not fp:
        fp = os.path.join(PROJECT, '__about__.py')
    dct = {}
    with open(fp, 'rb') as f:
        src = f.read()
        if sys.version_info[0] > 2:
            src = src.decode('UTF-8')
        exec(src, ta.cast(ta.Dict, dct))
    return dct


DIR = os.path.realpath(os.path.dirname(__file__))

ABOUT = _read_about(os.path.join(DIR, PROJECT, '__about__.py'))

if __name__ == '__main__':
    st.setup(
        name=PROJECT,
        version=ABOUT['__version__'],
        description=ABOUT['__description__'],
        author=ABOUT['__author__'],
        url=ABOUT['__url__'],
        license=ABOUT['__license__'],

        python_requires=ABOUT['__python_requires__'],
        classifiers=ABOUT['__classifiers__'],

        setup_requires=['setuptools'],

        packages=st.find_packages(
            include=[PROJECT, PROJECT + '.*'],
            exclude=['tests', '*.tests', '*.tests.*'],
        )
    )
