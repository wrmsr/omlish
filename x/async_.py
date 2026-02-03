# ruff: noqa: UP006 UP045
#
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
#
# https://github.com/jab/cpython/blob/ce35092a898be5da4fd6ff2d1c92b4e020ccf934/Lib/operator.py
import collections.abc


##


_AITER_NOT_PROVIDED = object()  # sentinel object to detect when a kwarg was not given


def aiter_(obj, sentinel=_AITER_NOT_PROVIDED):
    """
    aiter_(async_iterable) -> async_iterator
    aiter_(async_callable, sentinel) -> async_iterator

    Like the iter() builtin but for async iterables and callables.
    """

    if sentinel is _AITER_NOT_PROVIDED:
        if not isinstance(obj, collections.abc.AsyncIterable):
            raise TypeError(f'aiter_ expected an AsyncIterable, got {type(obj)}')

        ait = type(obj).__aiter__(obj)
        if not isinstance(ait, collections.abc.AsyncIterator):
            raise TypeError(f'obj.__aiter__() returned non-AsyncIterator: {type(ait)}')

        return ait

    if not callable(obj):
        raise TypeError(f'aiter_ expected an async callable, got {type(obj)}')

    return _aiter_callable(obj, sentinel)


class _aiter_callable:  # noqa
    __slots__ = ('acallable', 'sentinel')

    def __init__(self, acallable, sentinel):
        self.acallable = acallable
        self.sentinel = sentinel

    def __aiter__(self):
        return self

    def __anext__(self):
        return _aiter_anext(self.acallable().__await__(), self.sentinel)


class _aiter_anext:  # noqa
    __slots__ = ('iterator', 'sentinel')

    def __init__(self, iterator, sentinel):
        self.iterator = iterator
        self.sentinel = sentinel

    def __await__(self):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.iterator)
        except StopIteration as end:
            if end.value == self.sentinel:
                raise StopAsyncIteration(end.value) from None
            raise


def anext_(async_iterator, default=_AITER_NOT_PROVIDED):
    """
    anext_(async_iterator[, default])

    Return the next item from the async iterator. If default is given and the iterator is exhausted, it is returned
    instead of raising StopAsyncIteration.
    """

    if not isinstance(async_iterator, collections.abc.AsyncIterator):
        raise TypeError(f'anext_ expected an AsyncIterator, got {type(async_iterator)}')

    anxt = type(async_iterator).__anext__(async_iterator)

    if default is _AITER_NOT_PROVIDED:
        return anxt

    return _anext_default(anxt, default)


class _anext_default:  # noqa
    __slots__ = ('iterator', 'default')

    def __init__(self, iterator, default):
        self.iterator = iterator
        self.default = default

    def __await__(self):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.iterator)
        except StopAsyncIteration:
            raise StopIteration(self.default) from None
