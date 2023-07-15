import functools
import sys
import types


NoneType = type(None)
NotImplementedType = type(NotImplemented)
EllipsisType = type(...)


def get_annotations(obj, *, globals=None, locals=None, eval_str=False):
    """Compute the annotations dict for an object.

    obj may be a callable, class, or module.
    Passing in an object of any other type raises TypeError.

    Returns a dict.  get_annotations() returns a new dict every time it's called; calling it twice on the same object
    will return two different but equivalent dicts.

    This function handles several details for you:

      * If eval_str is true, values of type str will be un-stringized using eval().  This is intended for use with
        stringized annotations ("from __future__ import annotations").
      * If obj doesn't have an annotations dict, returns an empty dict.  (Functions and methods always have an
        annotations dict; classes, modules, and other types of callables may not.)
      * Ignores inherited annotations on classes.  If a class doesn't have its own annotations dict, returns an empty
        dict.
      * All accesses to object members and dict values are done using getattr() and dict.get() for safety.
      * Always, always, always returns a freshly-created dict.

    eval_str controls whether or not values of type str are replaced with the result of calling eval() on those values:

      * If eval_str is true, eval() is called on values of type str.
      * If eval_str is false (the default), values of type str are unchanged.

    globals and locals are passed in to eval(); see the documentation for eval() for more information.  If either
    globals or locals is None, this function may replace that value with a context-specific default, contingent on
    type(obj):

      * If obj is a module, globals defaults to obj.__dict__.
      * If obj is a class, globals defaults to sys.modules[obj.__module__].__dict__ and locals defaults to the obj class
        namespace.
      * If obj is a callable, globals defaults to obj.__globals__, although if obj is a wrapped function (using
        functools.update_wrapper()) it is first unwrapped.
    """
    if isinstance(obj, type):
        # class
        obj_dict = getattr(obj, '__dict__', None)
        if obj_dict and hasattr(obj_dict, 'get'):
            ann = obj_dict.get('__annotations__', None)
            if isinstance(ann, types.GetSetDescriptorType):
                ann = None
        else:
            ann = None

        obj_globals = None
        module_name = getattr(obj, '__module__', None)
        if module_name:
            module = sys.modules.get(module_name, None)
            if module:
                obj_globals = getattr(module, '__dict__', None)
        obj_locals = dict(vars(obj))
        unwrap = obj
    elif isinstance(obj, types.ModuleType):
        # module
        ann = getattr(obj, '__annotations__', None)
        obj_globals = getattr(obj, '__dict__')
        obj_locals = None
        unwrap = None
    elif callable(obj):
        # this includes types.Function, types.BuiltinFunctionType, types.BuiltinMethodType, functools.partial,
        # functools.singledispatch, "class funclike" from Lib/test/test_inspect... on and on it goes.
        ann = getattr(obj, '__annotations__', None)
        obj_globals = getattr(obj, '__globals__', None)
        obj_locals = None
        unwrap = obj
    else:
        raise TypeError(f"{obj!r} is not a module, class, or callable.")

    if ann is None:
        return {}

    if not isinstance(ann, dict):
        raise ValueError(f"{obj!r}.__annotations__ is neither a dict nor None")

    if not ann:
        return {}

    if not eval_str:
        return dict(ann)

    if unwrap is not None:
        while True:
            if hasattr(unwrap, '__wrapped__'):
                unwrap = unwrap.__wrapped__
                continue
            if isinstance(unwrap, functools.partial):
                unwrap = unwrap.func
                continue
            break
        if hasattr(unwrap, "__globals__"):
            obj_globals = unwrap.__globals__

    if globals is None:
        globals = obj_globals
    if locals is None:
        locals = obj_locals

    return_value = {
        key: value if not isinstance(value, str) else eval(value, globals, locals)
        for key, value in ann.items()
    }
    return return_value


def update_abstractmethods(cls):
    """Recalculate the set of abstract methods of an abstract class.

    If a class has had one of its abstract methods implemented after the class was created, the method will not be
    considered implemented until this function is called. Alternatively, if a new abstract method has been added to the
    class, it will only be considered an abstract method of the class after this function is called.

    This function should be called before any use is made of the class, usually in class decorators that add methods to
    the subject class.

    Returns cls, to allow usage as a class decorator.

    If cls is not an instance of ABCMeta, does nothing.
    """
    if not hasattr(cls, '__abstractmethods__'):
        # We check for __abstractmethods__ here because cls might by a C implementation or a python implementation
        # (especially during testing), and we want to handle both cases.
        return cls

    abstracts = set()
    # Check the existing abstract methods of the parents, keep only the ones that are not implemented.
    for scls in cls.__bases__:
        for name in getattr(scls, '__abstractmethods__', ()):
            value = getattr(cls, name, None)
            if getattr(value, "__isabstractmethod__", False):
                abstracts.add(name)
    # Also add any other newly added abstract methods.
    for name, value in cls.__dict__.items():
        if getattr(value, "__isabstractmethod__", False):
            abstracts.add(name)
    cls.__abstractmethods__ = frozenset(abstracts)
    return cls