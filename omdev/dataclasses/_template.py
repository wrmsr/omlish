# type: ignore
# ruff: noqa
# flake8: noqa
import dataclasses
import reprlib
import types


##


REGISTRY = {}


def _register(plan_repr):
    def inner(fn):
        REGISTRY[fn.__name__] = (plan_repr, fn)
        return fn
    return inner


##
