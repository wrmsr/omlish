// @omdev-ext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

#define _MODULE_NAME "_dc"
#define _PACKAGE_NAME "x.dev.c"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

typedef struct _dc_state {
    PyTypeObject *point_type;
} _dc_state;

static inline _dc_state * get_dc_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_dc_state *)state;
}

//

typedef struct {
    PyObject_HEAD
    PyObject *dict;
    PyObject *weakreflist;
    int x;
    int y;
} point_object;

static int point_traverse(point_object *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    Py_VISIT(self->dict);
    return 0;
}

static int point_clear(point_object *self)
{
    Py_CLEAR(self->dict);
    return 0;
}

static void point_dealloc(point_object *self)
{
    PyTypeObject *tp = Py_TYPE(self);
    PyObject_GC_UnTrack(self);
    if (self->weakreflist != NULL) {
        PyObject_ClearWeakRefs((PyObject *) self);
    }
    point_clear(self);
    tp->tp_free((PyObject *) self);
    Py_DECREF(tp);
}

static PyObject * point_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    int x, y;

    static const char *kwlist[] = {
        "x",
        "y",
        NULL,
    };
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii", (char **) kwlist, &x, &y)) {
        PyErr_SetString(PyExc_TypeError, "type 'point' takes two arguments 'x' and 'y'");
        return NULL;
    }

    point_object *self;
    self = (point_object *) type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }

    self->x = x;
    self->y = y;

    return (PyObject *) self;
}

static PyObject *
point_repr(point_object *self)
{
    int i = Py_ReprEnter((PyObject *) self);
    if (i != 0) {
        if (i < 0) {
            return NULL;
        }
        return PyUnicode_FromString("...");
    }

    PyObject *result = PyUnicode_FromFormat(
        "%s(x=%d, y=%d)",
        _PyType_Name(Py_TYPE(self)),
        self->x,
        self->y);

    Py_ReprLeave((PyObject *) self);
    return result;
}

static PyObject *
point_reduce(point_object *self, PyObject *unused)
{
    return Py_BuildValue(
        "O(ii)(O)",
        Py_TYPE(self),
        self->x,
        self->y,
        self->dict ? self->dict : Py_None);
}

static PyObject *
point_setstate(point_object *self, PyObject *state)
{
    PyObject *dict;

    if (!PyTuple_Check(state) ||
        !PyArg_ParseTuple(state, "O", &dict))
    {
        PyErr_SetString(PyExc_TypeError, "invalid point state");
        return NULL;
    }

    if (dict == Py_None) {
        dict = NULL;
    } else {
        Py_INCREF(dict);
    }

    Py_XSETREF(self->dict, dict);
    Py_RETURN_NONE;
}

static PyMemberDef point_members[] = {
    {"x", Py_T_INT, offsetof(point_object, x), READONLY},
    {"y", Py_T_INT, offsetof(point_object, y), READONLY},
    {"__weaklistoffset__", T_PYSSIZET, offsetof(point_object, weakreflist), READONLY},
    {"__dictoffset__", T_PYSSIZET, offsetof(point_object, dict), READONLY},
    {NULL}
};

static PyGetSetDef point_getsetters[] = {
    {"__dict__", PyObject_GenericGetDict, PyObject_GenericSetDict},
    {NULL}
};

static PyMethodDef point_methods[] = {
    {"__reduce__", (PyCFunction) point_reduce, METH_NOARGS},
    {"__setstate__", (PyCFunction) point_setstate, METH_O},
    {NULL}
};

static PyType_Slot point_type_slots[] = {
    {Py_tp_traverse, (void *) point_traverse},
    {Py_tp_clear, (void *) point_clear},
    {Py_tp_methods, point_methods},
    {Py_tp_members, point_members},
    {Py_tp_getset, point_getsetters},
    {Py_tp_new, (void *) point_new},
    {Py_tp_repr, (void *) point_repr},
    {Py_tp_dealloc, (void *) point_dealloc},
    {0, 0}
};

static PyType_Spec point_type_spec = {
    .name = _MODULE_FULL_NAME ".point",
    .basicsize = sizeof(point_object),
    .itemsize = 0,
    .flags =
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
        Py_TPFLAGS_BASETYPE,  // | Py_TPFLAGS_IMMUTABLETYPE,
    .slots = point_type_slots
};

//

PyDoc_STRVAR(_dc_doc, "dc");

static int _dc_exec(PyObject *module)
{
    _dc_state *state = get_dc_state(module);

    state->point_type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &point_type_spec, NULL);
    if (state->point_type == NULL) {
        return -1;
    }
    if (PyModule_AddType(module, state->point_type) < 0) {
        return -1;
    }

    return 0;
}

static int _dc_traverse(PyObject *module, visitproc visit, void *arg)
{
    _dc_state *state = get_dc_state(module);
    Py_VISIT(state->point_type);
    return 0;
}

static int _dc_clear(PyObject *module)
{
    _dc_state *state = get_dc_state(module);
    Py_CLEAR(state->point_type);
    return 0;
}

static void _dc_free(void *module)
{
    _dc_clear((PyObject *)module);
}

static PyMethodDef _dc_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _dc_slots[] = {
    {Py_mod_exec, (void *) _dc_exec},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {0, NULL}
};

static struct PyModuleDef _dc_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_dc",
    .m_doc = _dc_doc,
    .m_size = sizeof(_dc_state),
    .m_methods = _dc_methods,
    .m_slots = _dc_slots,
    .m_traverse = _dc_traverse,
    .m_clear = _dc_clear,
    .m_free = _dc_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__dc(void)
{
    return PyModuleDef_Init(&_dc_module);
}

}
