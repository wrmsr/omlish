// @omdev-ext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

typedef struct _uuid_state {
    PyObject *uuid_cls;
    PyObject *safe_uuid_cls;
} _uuid_state;

static inline _uuid_state * get_uuid_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_uuid_state *)state;
}

//

static PyObject *_uuid_new(PyObject *self, PyObject *args)
{
    Py_RETURN_NONE;
}

//

PyDoc_STRVAR(_uuid_doc, "uuid");

static int _uuid_exec(PyObject *module)
{
    _uuid_state *state = get_uuid_state(module);

    PyObject *uuid_module = PyImport_ImportModule("uuid");
    if (uuid_module == NULL) {
        return -1;
    }
    if ((state->uuid_cls = PyObject_GetAttrString(uuid_module, "UUID")) == NULL) {
        Py_DECREF(uuid_module);
        return -1;
    }
    if ((state->safe_uuid_cls = PyObject_GetAttrString(uuid_module, "SafeUUID")) == NULL) {
        Py_DECREF(uuid_module);
        return -1;
    }
    Py_DECREF(uuid_module);

    return 0;
}

static int _uuid_traverse(PyObject *module, visitproc visit, void *arg)
{
    _uuid_state *state = get_uuid_state(module);
    Py_VISIT(state->uuid_cls);
    Py_VISIT(state->safe_uuid_cls);
    return 0;
}

static int _uuid_clear(PyObject *module)
{
    _uuid_state *state = get_uuid_state(module);
    Py_CLEAR(state->uuid_cls);
    Py_CLEAR(state->safe_uuid_cls);
    return 0;
}

static void _uuid_free(void *module)
{
    _uuid_clear((PyObject *)module);
}

static PyMethodDef _uuid_methods[] = {
    {"new", _uuid_new, METH_VARARGS, "new"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _uuid_slots[] = {
    {Py_mod_exec, (void *) _uuid_exec},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    // {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, NULL}
};

static struct PyModuleDef _uuid_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_uuid",
    .m_doc = _uuid_doc,
    .m_size = sizeof(_uuid_state),
    .m_methods = _uuid_methods,
    .m_slots = _uuid_slots,
    .m_traverse = _uuid_traverse,
    .m_clear = _uuid_clear,
    .m_free = _uuid_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__uuid(void)
{
    return PyModuleDef_Init(&_uuid_module);
}

}
