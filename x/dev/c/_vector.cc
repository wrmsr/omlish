// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

///

#define _MODULE_NAME "_vector"
#define _PACKAGE_NAME "omdev.cexts"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

typedef struct vector_module_state {
    PyTypeObject *vector_type;
} vector_module_state;

static inline vector_module_state * get_vector_module_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (vector_module_state *)state;
}

///

typedef struct {
    PyObject_HEAD
    PyObject *dict;
    PyObject *weakreflist;
} vector_object;

static int vector_traverse(vector_object *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    Py_VISIT(self->dict);
    return 0;
}

static int vector_clear(vector_object *self)
{
    Py_CLEAR(self->dict);
    return 0;
}

static void vector_dealloc(vector_object *self)
{
    PyTypeObject *tp = Py_TYPE(self);
    PyObject_GC_UnTrack(self);
    if (self->weakreflist != NULL) {
        PyObject_ClearWeakRefs((PyObject *) self);
    }
    vector_clear(self);
    tp->tp_free((PyObject *) self);
    Py_DECREF(tp);
}

static PyObject * vector_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (PyTuple_GET_SIZE(args) != 0) {
        PyErr_SetString(PyExc_TypeError, "type 'vector' no arguments");
        return NULL;
    }

    vector_object *self;
    self = (vector_object *) type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }

    return (PyObject *) self;
}

static PyMemberDef vector_members[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(vector_object, weakreflist), READONLY},
    {"__dictoffset__", T_PYSSIZET, offsetof(vector_object, dict), READONLY},
    {NULL}
};

static PyGetSetDef vector_getsetters[] = {
    {"__dict__", PyObject_GenericGetDict, PyObject_GenericSetDict},
    {NULL}
};

static PyMethodDef vector_methods[] = {
    {NULL}
};

static PyType_Slot vector_type_slots[] = {
    {Py_tp_traverse, (void *) vector_traverse},
    {Py_tp_clear, (void *) vector_clear},
    {Py_tp_methods, vector_methods},
    {Py_tp_members, vector_members},
    {Py_tp_getset, vector_getsetters},
    {Py_tp_new, (void *) vector_new},
    {Py_tp_dealloc, (void *) vector_dealloc},
    {0, 0}
};

static PyType_Spec vector_type_spec = {
    .name = _MODULE_FULL_NAME ".vector",
    .basicsize = sizeof(vector_object),
    .itemsize = 0,
    .flags =
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
        Py_TPFLAGS_BASETYPE,
    .slots = vector_type_slots
};

///

PyDoc_STRVAR(vector_module_doc, "vector");

static int vector_module_exec(PyObject *module)
{
    vector_module_state *state = get_vector_module_state(module);

    state->vector_type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &vector_type_spec, NULL);
    if (state->vector_type == NULL) {
        return -1;
    }
    if (PyModule_AddType(module, state->vector_type) < 0) {
        return -1;
    }

    return 0;
}

static int vector_module_traverse(PyObject *module, visitproc visit, void *arg)
{
    vector_module_state *state = get_vector_module_state(module);
    Py_VISIT(state->vector_type);
    return 0;
}

static int vector_module_clear(PyObject *module)
{
    vector_module_state *state = get_vector_module_state(module);
    Py_CLEAR(state->vector_type);
    return 0;
}

static void vector_module_free(void *module)
{
    vector_module_clear((PyObject *)module);
}

static PyMethodDef vector_module_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot vector_module_slots[] = {
    {Py_mod_exec, (void *) vector_module_exec},
// #if PY_VERSION_HEX >= 0x030D0000
//     {Py_mod_gil, Py_MOD_GIL_NOT_USED},
// #endif
    {0, NULL}
};

static struct PyModuleDef vector_module_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = vector_module_doc,
    .m_size = sizeof(vector_module_state),
    .m_methods = vector_module_methods,
    .m_slots = vector_module_slots,
    .m_traverse = vector_module_traverse,
    .m_clear = vector_module_clear,
    .m_free = vector_module_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__vector(void)
{
    return PyModuleDef_Init(&vector_module_module);
}

}
