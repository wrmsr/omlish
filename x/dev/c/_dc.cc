// @omdev-ext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

typedef struct _dc_state {
} _dc_state;

static inline _dc_state * get_dc_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_dc_state *)state;
}

//

PyDoc_STRVAR(_dc_doc, "dc");

static int _dc_exec(PyObject *module)
{
    _dc_state *state = get_dc_state(module);
    return 0;
}

static int _dc_traverse(PyObject *module, visitproc visit, void *arg)
{
    _dc_state *state = get_dc_state(module);
    return 0;
}

static int _dc_clear(PyObject *module)
{
    _dc_state *state = get_dc_state(module);
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
