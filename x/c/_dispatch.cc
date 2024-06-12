#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

typedef struct _dispatch_state {
    PyTypeObject *Custom_type;
} _dispatch_state;

static inline _dispatch_state * get_dispatch_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_dispatch_state *)state;
}

//

typedef struct {
    PyObject_HEAD
    PyObject *first;
    PyObject *last;
    int number;
} CustomObject;

static int Custom_traverse(CustomObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->first);
    Py_VISIT(self->last);
    return 0;
}

static int Custom_clear(CustomObject *self)
{
    Py_CLEAR(self->first);
    Py_CLEAR(self->last);
    return 0;
}

static void Custom_dealloc(CustomObject *self)
{
    PyObject_GC_UnTrack(self);
    Custom_clear(self);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject * Custom_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    CustomObject *self;
    self = (CustomObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->first = PyUnicode_FromString("");
        if (self->first == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->last = PyUnicode_FromString("");
        if (self->last == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->number = 0;
    }
    return (PyObject *) self;
}

static int Custom_init(CustomObject *self, PyObject *args, PyObject *kwds)
{
    static const char *kwlist[] = {"first", "last", "number", NULL};
    PyObject *first = NULL, *last = NULL, *tmp;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|UUi", (char **)kwlist, &first, &last, &self->number)) {
        return -1;
    }

    if (first) {
        tmp = self->first;
        Py_INCREF(first);
        self->first = first;
        Py_DECREF(tmp);
    }
    if (last) {
        tmp = self->last;
        Py_INCREF(last);
        self->last = last;
        Py_DECREF(tmp);
    }
    return 0;
}

static PyMemberDef Custom_members[] = {
    {"number", T_INT, offsetof(CustomObject, number), 0, "custom number"},
    {NULL}
};

static PyObject * Custom_getfirst(CustomObject *self, void *closure)
{
    Py_INCREF(self->first);
    return self->first;
}

static int Custom_setfirst(CustomObject *self, PyObject *value, void *closure)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete the first attribute");
        return -1;
    }
    if (!PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "The first attribute value must be a string");
        return -1;
    }
    Py_INCREF(value);
    Py_CLEAR(self->first);
    self->first = value;
    return 0;
}

static PyObject * Custom_getlast(CustomObject *self, void *closure)
{
    Py_INCREF(self->last);
    return self->last;
}

static int Custom_setlast(CustomObject *self, PyObject *value, void *closure)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete the last attribute");
        return -1;
    }
    if (!PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "The last attribute value must be a string");
        return -1;
    }
    Py_INCREF(value);
    Py_CLEAR(self->last);
    self->last = value;
    return 0;
}

static PyGetSetDef Custom_getsetters[] = {
    {"first", (getter) Custom_getfirst, (setter) Custom_setfirst, "first name", NULL},
    {"last", (getter) Custom_getlast, (setter) Custom_setlast, "last name", NULL},
    {NULL}
};

static PyObject * Custom_name(CustomObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyUnicode_FromFormat("%S %S", self->first, self->last);
}

static PyMethodDef Custom_methods[] = {
    {"name", (PyCFunction) Custom_name, METH_NOARGS, "Return the name, combining the first and last name"},
    {NULL}
};

static PyType_Slot Custom_type_slots[] = {
        {Py_tp_traverse, (void *) Custom_traverse},
        {Py_tp_clear, (void *) Custom_clear},
        {Py_tp_methods, Custom_methods},
        {Py_tp_members, Custom_members},
        {Py_tp_getset, Custom_getsetters},
        {Py_tp_init, (void *) Custom_init},
        {Py_tp_new, (void *) Custom_new},
        {Py_tp_dealloc, (void *) Custom_dealloc},

        {0, 0}
};

static PyType_Spec Custom_type_spec = {
        .name = "functools.Custom",
        .basicsize = sizeof(CustomObject),
        .itemsize = 0,
        .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
                 Py_TPFLAGS_BASETYPE | Py_TPFLAGS_IMMUTABLETYPE,
        .slots = Custom_type_slots
};

//

static int _dispatch_exec(PyObject *module)
{
    _dispatch_state *state = get_dispatch_state(module);

    state->Custom_type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &Custom_type_spec, NULL);
    if (state->Custom_type == NULL) {
        return -1;
    }
    if (PyModule_AddType(module, state->Custom_type) < 0) {
        return -1;
    }

    return 0;
}

static int _dispatch_traverse(PyObject *module, visitproc visit, void *arg)
{
    _dispatch_state *state = get_dispatch_state(module);
    Py_VISIT(state->Custom_type);
    return 0;
}

static int _dispatch_clear(PyObject *module)
{
    _dispatch_state *state = get_dispatch_state(module);
    Py_CLEAR(state->Custom_type);
    return 0;
}

static void _dispatch_free(void *module)
{
    _dispatch_clear((PyObject *)module);
}

static PyMethodDef _dispatch_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _dispatch_slots[] = {
        {Py_mod_exec, (void *) _dispatch_exec},
        {0, NULL}
};

static struct PyModuleDef _dispatch_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_dispatch",
    .m_size = sizeof(_dispatch_state),
    .m_methods = _dispatch_methods,
    .m_slots = _dispatch_slots,
    .m_traverse = _dispatch_traverse,
    .m_clear = _dispatch_clear,
    .m_free = _dispatch_free,
};


extern "C" {

PyMODINIT_FUNC PyInit__dispatch(void)
{
    return PyModuleDef_Init(&_dispatch_module);
}

}
