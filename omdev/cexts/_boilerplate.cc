// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

#define _MODULE_NAME "_boilerplate"
#define _PACKAGE_NAME "omdev.cexts"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

typedef struct boilerplate_state {
} boilerplate_state;

static inline boilerplate_state * get_boilerplate_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (boilerplate_state *)state;
}

//

PyDoc_STRVAR(boilerplate_doc, "boilerplate");

static int boilerplate_exec(PyObject *module)
{
    get_boilerplate_state(module);
    return 0;
}

static int boilerplate_traverse(PyObject *module, visitproc visit, void *arg)
{
    get_boilerplate_state(module);
    return 0;
}

static int boilerplate_clear(PyObject *module)
{
    get_boilerplate_state(module);
    return 0;
}

static void boilerplate_free(void *module)
{
    boilerplate_clear((PyObject *)module);
}

static PyMethodDef boilerplate_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot boilerplate_slots[] = {
    {Py_mod_exec, (void *) boilerplate_exec},
// #if PY_VERSION_HEX >= 0x030D0000
//     {Py_mod_gil, Py_MOD_GIL_NOT_USED},
// #endif
    {0, NULL}
};

static struct PyModuleDef boilerplate_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = boilerplate_doc,
    .m_size = sizeof(boilerplate_state),
    .m_methods = boilerplate_methods,
    .m_slots = boilerplate_slots,
    .m_traverse = boilerplate_traverse,
    .m_clear = boilerplate_clear,
    .m_free = boilerplate_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__boilerplate(void)
{
    return PyModuleDef_Init(&boilerplate_module);
}

}
