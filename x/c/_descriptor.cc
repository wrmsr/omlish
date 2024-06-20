#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

#define _MODULE_NAME "x.c._descriptor"

//static struct PyModuleDef _descriptor_module;

//

typedef struct _descriptor_module_state {
    PyObject *dataclasses_missing;
    PyTypeObject *field_descriptor_type;
} _descriptor_module_state;

static inline _descriptor_module_state * get_descriptor_module_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_descriptor_module_state *)state;
}

//static inline _descriptor_module_state * get_descriptor_module_state_by_type(PyTypeObject *type)
//{
//    PyObject *module = PyType_GetModuleByDef(type, &_descriptor_module_module);
//    if (module == NULL) {
//        return NULL;
//    }
//    return get_descriptor_module_state(module);
//}

//

/*
class FieldDescriptor:

    def __init__(
            self,
            attr: str,
            *,
            default: ta.Any = dc.MISSING,
            frozen: bool = False,
            name: str | None = None,
            pre_set: ta.Callable[[ta.Any, ta.Any], ta.Any] | None = None,
            post_set: ta.Callable[[ta.Any, ta.Any], None] | None = None,
    ) -> None:
        super().__init__()

        self._attr = attr
        self._default = default
        self._frozen = frozen
        self._name = name
        self._pre_set = pre_set
        self._post_set = post_set

    def __set_name__(self, owner, name):
        if self._name is None:
            self._name = name

    def __get__(self, instance, owner=None):
        if instance is not None:
            try:
                return getattr(instance, self._attr)
            except AttributeError:
                pass
        if self._default is not dc.MISSING:
            return self._default
        raise AttributeError(self._name)

    def __set__(self, instance, value):
        if self._frozen:
            raise dc.FrozenInstanceError(f'cannot assign to field {self._name!r}')
        if self._pre_set is not None:
            value = self._pre_set(instance, value)
        setattr(instance, self._attr, value)
        if self._post_set is not None:
            self._post_set(instance, value)

    def __delete__(self, instance):
        if self._frozen:
            raise dc.FrozenInstanceError(f'cannot delete field {self._name!r}')
        delattr(instance, self._attr)
 */

typedef struct {
    PyObject_HEAD
    PyObject *attr;
    PyObject *default_;
    PyObject *frozen;
    PyObject *name;
    PyObject *pre_set;
    PyObject *post_set;
    PyObject *dict;
} field_descriptor_object;

static int field_descriptor_traverse(field_descriptor_object *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    Py_VISIT(self->attr);
    Py_VISIT(self->default_);
    Py_VISIT(self->frozen);
    Py_VISIT(self->name);
    Py_VISIT(self->pre_set);
    Py_VISIT(self->post_set);
    Py_VISIT(self->dict);
    return 0;
}

static int field_descriptor_clear(field_descriptor_object *self)
{
    Py_CLEAR(self->attr);
    Py_CLEAR(self->default_);
    Py_CLEAR(self->frozen);
    Py_CLEAR(self->name);
    Py_CLEAR(self->pre_set);
    Py_CLEAR(self->post_set);
    Py_CLEAR(self->dict);
    return 0;
}

static void field_descriptor_dealloc(field_descriptor_object *self)
{
    PyTypeObject *tp = Py_TYPE(self);
    PyObject_GC_UnTrack(self);
    field_descriptor_clear(self);
    tp->tp_free((PyObject *) self);
    Py_DECREF(tp);
}

static PyObject * field_descriptor_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (PyTuple_GET_SIZE(args) != 1) {
        PyErr_SetString(PyExc_TypeError, "type 'field_descriptor' takes exactly one positional argument");
        return NULL;
    }

    PyObject *dispatch = PyTuple_GET_ITEM(args, 0);
    if (!PyCallable_Check(dispatch)) {
        PyErr_SetString(PyExc_TypeError, "the argument must be callable");
        return NULL;
    }

    field_descriptor_object *self;
    self = (field_descriptor_object *) type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }

    self->dispatch = Py_NewRef(dispatch);
    self->vectorcall = (vectorcallfunc) field_descriptor_vectorcall;

    if (kwds != NULL) {
        self->dict = PyDict_Copy(kwds);
    }

    return (PyObject *) self;
}

static PyObject * field_descriptor_do_dispatch(field_descriptor_object *self, PyObject *arg) {
    PyTypeObject *arg_ty = Py_TYPE(arg);

    PyObject *args[2] = {NULL, (PyObject *) arg_ty};
    PyObject *disp_res = PyObject_Vectorcall(self->dispatch, &args[1], 1 | PY_VECTORCALL_ARGUMENTS_OFFSET, NULL);

    return disp_res;
}

static PyObject * field_descriptor_call(field_descriptor_object *self, PyObject *args, PyObject *kwargs) {
    assert(PyCallable_Check(self->dispatch));

    if (PyTuple_GET_SIZE(args) < 1) {
        PyErr_SetString(PyExc_TypeError, "field_descriptor takes at least one positional argument");
        return NULL;
    }

    PyObject *arg = PyTuple_GET_ITEM(args, 0);
    PyObject *disp_res = field_descriptor_do_dispatch(self, arg);
    if (disp_res == NULL) {
        return NULL;
    }

    PyObject *res = PyObject_Call(disp_res, args, kwargs);

    Py_DECREF(disp_res);

    return res;
}

static PyMemberDef field_descriptor_members[] = {
    {"__dictoffset__", T_PYSSIZET, offsetof(field_descriptor_object, dict), READONLY},
    {NULL}
};

static PyGetSetDef field_descriptor_getsetters[] = {
    {"__dict__", PyObject_GenericGetDict, PyObject_GenericSetDict},
    {NULL}
};

static PyMethodDef field_descriptor_methods[] = {
    {NULL}
};

static PyType_Slot field_descriptor_type_slots[] = {
        {Py_tp_traverse, (void *) field_descriptor_traverse},
        {Py_tp_clear, (void *) field_descriptor_clear},
        {Py_tp_methods, field_descriptor_methods},
        {Py_tp_members, field_descriptor_members},
        {Py_tp_getset, field_descriptor_getsetters},
        {Py_tp_new, (void *) field_descriptor_new},
        {Py_tp_dealloc, (void *) field_descriptor_dealloc},
        {Py_tp_call, (void *) field_descriptor_call},
        {0, 0}
};

static PyType_Spec field_descriptor_type_spec = {
        .name = _MODULE_NAME ".field_descriptor",
        .basicsize = sizeof(field_descriptor_object),
        .itemsize = 0,
        .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
                 Py_TPFLAGS_BASETYPE | Py_TPFLAGS_IMMUTABLETYPE,
        .slots = field_descriptor_type_slots
};

//

static int _descriptor_module_exec(PyObject *module)
{
    _descriptor_module_state *state = get_descriptor_module_state(module);

    PyObject *dataclasses_module = PyImport_ImportModule("dataclasses");
    if (dataclasses_module == NULL) {
        return -1;
    }
    if ((state->dataclasses_missing = PyObject_GetAttrString(dataclasses_module, "MISSING")) == NULL) {
        Py_DECREF(dataclasses_module);
        return -1;
    }
    Py_DECREF(dataclasses_module);

    state->field_descriptor_type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &field_descriptor_type_spec, NULL);
    if (state->field_descriptor_type == NULL) {
        return -1;
    }
    if (PyModule_AddType(module, state->field_descriptor_type) < 0) {
        return -1;
    }

    return 0;
}

static int _descriptor_module_traverse(PyObject *module, visitproc visit, void *arg)
{
    _descriptor_module_state *state = get_descriptor_module_state(module);
    Py_VISIT(state->dataclasses_missing);
    Py_VISIT(state->field_descriptor_type);
    return 0;
}

static int _descriptor_module_clear(PyObject *module)
{
    _descriptor_module_state *state = get_descriptor_module_state(module);
    Py_CLEAR(state->dataclasses_missing);
    Py_CLEAR(state->field_descriptor_type);
    return 0;
}

static void _descriptor_module_free(void *module)
{
    _descriptor_module_clear((PyObject *)module);
}

static PyMethodDef _descriptor_module_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _descriptor_module_slots[] = {
        {Py_mod_exec, (void *) _descriptor_module_exec},
        {0, NULL}
};

static struct PyModuleDef _descriptor_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_size = sizeof(_descriptor_module_state),
    .m_methods = _descriptor_module_methods,
    .m_slots = _descriptor_module_slots,
    .m_traverse = _descriptor_module_traverse,
    .m_clear = _descriptor_module_clear,
    .m_free = _descriptor_module_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__descriptor(void)
{
    return PyModuleDef_Init(&_descriptor_module);
}

}
