# type: ignore
# ruff: noqa
# flake8: noqa
import dataclasses
import reprlib
import types


##


REGISTRY = {}


def _register(*args):
    def inner(fn):
        REGISTRY[fn.__name__] = (args, fn)
        return fn
    return inner


##
