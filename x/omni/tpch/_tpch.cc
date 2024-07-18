#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

typedef struct _tpch_state {
} _tpch_state;

static inline _tpch_state * get_tpch_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_tpch_state *)state;
}

//

PyDoc_STRVAR(_tpch_doc, "tpch");

static int _tpch_exec(PyObject *module)
{
    get_tpch_state(module);
    return 0;
}

static int _tpch_traverse(PyObject *module, visitproc visit, void *arg)
{
    get_tpch_state(module);
    return 0;
}

static int _tpch_clear(PyObject *module)
{
    get_tpch_state(module);
    return 0;
}

static void _tpch_free(void *module)
{
    _tpch_clear((PyObject *)module);
}

static PyMethodDef _tpch_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _tpch_slots[] = {
    {Py_mod_exec, (void *) _tpch_exec},
    {0, NULL}
};

static struct PyModuleDef _tpch_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_tpch",
    .m_doc = _tpch_doc,
    .m_size = sizeof(_tpch_state),
    .m_methods = _tpch_methods,
    .m_slots = _tpch_slots,
    .m_traverse = _tpch_traverse,
    .m_clear = _tpch_clear,
    .m_free = _tpch_free,
};


extern "C" {

PyMODINIT_FUNC PyInit__tpch(void)
{
    return PyModuleDef_Init(&_tpch_module);
}

}
