from dataclasses import FrozenInstanceError
from dataclasses import MISSING
from libcpp cimport bool


cdef class FieldDescriptor:

    cdef public str attr
    cdef public object default_
    cdef public bool frozen
    cdef public str name
    cdef public object pre_set
    cdef public object post_set

    def __init__(
            self,
            str attr,
            *,
            object default_ = MISSING,
            bool frozen = False,
            str name = None,
            object pre_set = None,
            object post_set = None,
            **kwargs
    ):
        super().__init__(**kwargs)

        self.attr = attr
        self.default_ = default_
        self.frozen = frozen
        self.name = name
        self.pre_set = pre_set
        self.post_set = post_set

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name

    def __get__(self, instance, owner):
        if instance is not None:
            try:
                return getattr(instance, self.attr)
            except AttributeError:
                pass
        if self.default_ is not MISSING:
            return self.default_
        raise AttributeError(self.name)

    def __set__(self, instance, value):
        if self.frozen:
            raise FrozenInstanceError(f'cannot assign to field {self.name!r}')
        if self.pre_set is not None:
            value = self.pre_set(instance, value)
        setattr(instance, self.attr, value)
        if self.post_set is not None:
            self.post_set(instance, value)

    def __delete__(self, instance):
        if self.frozen:
            raise FrozenInstanceError(f'cannot delete field {self.name!r}')
        delattr(instance, self.attr)
