import dataclasses as dc
import inspect
import itertools
import types


MISSING = dc.MISSING


def _dataclass_getstate(self):
    return [getattr(self, f.name) for f in dc.fields(self)]


def _dataclass_setstate(self, state):
    for field, value in zip(dc.fields(self), state):
        object.__setattr__(self, field.name, value)


def _get_slots(cls):
    match cls.__dict__.get('__slots__'):
        # A class which does not define __slots__ at all is equivalent to a class defining
        #   __slots__ = ('__dict__', '__weakref__')
        # `__dictoffset__` and `__weakrefoffset__` can tell us whether the base type has dict/weakref slots, in a way
        # that works correctly for both Python classes and C extension types. Extension types don't use `__slots__` for
        # slot creation
        case None:
            slots = []
            if getattr(cls, '__weakrefoffset__', -1) != 0:
                slots.append('__weakref__')
            if getattr(cls, '__dictoffset__', -1) != 0:
                slots.append('__dict__')
            yield from slots
        case str(slot):
            yield slot
        # Slots may be any iterable, but we cannot handle an iterator because it will already be (partially) consumed.
        case iterable if not hasattr(iterable, '__next__'):
            yield from iterable
        case _:
            raise TypeError(f"Slots of '{cls.__name__}' cannot be determined")


def _update_func_cell_for__class__(f, oldcls, newcls):
    # Returns True if we update a cell, else False.
    if f is None:
        # f will be None in the case of a property where not all of fget, fset, and fdel are used.  Nothing to do in
        # that case.
        return False
    try:
        idx = f.__code__.co_freevars.index('__class__')
    except ValueError:
        # This function doesn't reference __class__, so nothing to do.
        return False
    # Fix the cell to point to the new class, if it's already pointing at the old class.  I'm not convinced that the "is
    # oldcls" test is needed, but other than performance can't hurt.
    closure = f.__closure__[idx]
    if closure.cell_contents is oldcls:
        closure.cell_contents = newcls
        return True
    return False


def add_slots(
        cls: type,
        is_frozen: bool,
        weakref_slot: bool,
) -> type:
    # Need to create a new class, since we can't set __slots__ after a class has been created, and the @dataclass
    # decorator is called after the class is created.

    # Make sure __slots__ isn't already set.
    if '__slots__' in cls.__dict__:
        raise TypeError(f'{cls.__name__} already specifies __slots__')

    # Create a new dict for our new class.
    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in dc.fields(cls))  # noqa

    # Make sure slots don't overlap with those in base classes.
    inherited_slots = set(itertools.chain.from_iterable(map(_get_slots, cls.__mro__[1:-1])))

    # The slots for our class.  Remove slots from our base classes.  Add '__weakref__' if weakref_slot was given, unless
    # it is already present.
    cls_dict['__slots__'] = tuple(
        itertools.filterfalse(
            inherited_slots.__contains__,
            itertools.chain(
                field_names,
                # gh-93521: '__weakref__' also needs to be filtered out if already present in inherited_slots
                ('__weakref__',) if weakref_slot else (),
            ),
        ),
    )

    for field_name in field_names:
        # Remove our attributes, if present. They'll still be available in _MARKER.
        cls_dict.pop(field_name, None)

    # Remove __dict__ itself.
    cls_dict.pop('__dict__', None)

    # Clear existing `__weakref__` descriptor, it belongs to a previous type:
    cls_dict.pop('__weakref__', None)

    qualname = getattr(cls, '__qualname__', None)
    newcls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
    if qualname is not None:
        newcls.__qualname__ = qualname

    if is_frozen:
        # Need this for pickling frozen classes with slots.
        if '__getstate__' not in cls_dict:
            newcls.__getstate__ = _dataclass_getstate  # type: ignore
        if '__setstate__' not in cls_dict:
            newcls.__setstate__ = _dataclass_setstate  # type: ignore

    # Fix up any closures which reference __class__.  This is used to fix zero argument super so that it points to the
    # correct class (the newly created one, which we're returning) and not the original class.  We can break out of this
    # loop as soon as we make an update, since all closures for a class will share a given cell.
    for member in newcls.__dict__.values():
        # If this is a wrapped function, unwrap it.
        member = inspect.unwrap(member)
        if isinstance(member, types.FunctionType):
            if _update_func_cell_for__class__(member, cls, newcls):
                break

        elif isinstance(member, property):
            if (
                    _update_func_cell_for__class__(member.fget, cls, newcls) or
                    _update_func_cell_for__class__(member.fset, cls, newcls) or
                    _update_func_cell_for__class__(member.fdel, cls, newcls)
            ):
                break

    return newcls
