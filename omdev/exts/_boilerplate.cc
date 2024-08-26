// @omdev-ext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

typedef struct _boilerplate_state {
} _boilerplate_state;

static inline _boilerplate_state * get_boilerplate_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_boilerplate_state *)state;
}

//

PyDoc_STRVAR(_boilerplate_doc, "boilerplate");

static int _boilerplate_exec(PyObject *module)
{
    get_boilerplate_state(module);
    return 0;
}

static int _boilerplate_traverse(PyObject *module, visitproc visit, void *arg)
{
    get_boilerplate_state(module);
    return 0;
}

static int _boilerplate_clear(PyObject *module)
{
    get_boilerplate_state(module);
    return 0;
}

static void _boilerplate_free(void *module)
{
    _boilerplate_clear((PyObject *)module);
}

static PyMethodDef _boilerplate_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _boilerplate_slots[] = {
    {Py_mod_exec, (void *) _boilerplate_exec},
    {0, NULL}
};

static struct PyModuleDef _boilerplate_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_boilerplate",
    .m_doc = _boilerplate_doc,
    .m_size = sizeof(_boilerplate_state),
    .m_methods = _boilerplate_methods,
    .m_slots = _boilerplate_slots,
    .m_traverse = _boilerplate_traverse,
    .m_clear = _boilerplate_clear,
    .m_free = _boilerplate_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__boilerplate(void)
{
    return PyModuleDef_Init(&_boilerplate_module);
}

}
