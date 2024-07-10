#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

typedef struct _junk_state {
} _junk_state;

// static inline _junk_state * get_junk_state(PyObject *module)
// {
//     void *state = PyModule_GetState(module);
//     assert(state != NULL);
//     return (_junk_state *)state;
// }

//

static PyObject * junk(PyObject *self, PyObject *args)
{
    return Py_BuildValue("k", 424);
}


//

PyDoc_STRVAR(_junk_doc, "junk");

static int _junk_exec(PyObject *module)
{
    // _junk_state *state = get_junk_state(module);
    return 0;
}

static int _junk_traverse(PyObject *module, visitproc visit, void *arg)
{
    // _junk_state *state = get_junk_state(module);
    return 0;
}

static int _junk_clear(PyObject *module)
{
    // _junk_state *state = get_junk_state(module);
    return 0;
}

static void _junk_free(void *module)
{
    _junk_clear((PyObject *)module);
}

static PyMethodDef module_methods[] = {
    {"junk", junk, METH_NOARGS, "junk"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _junk_slots[] = {
        {Py_mod_exec, (void *) _junk_exec},
        {0, NULL}
};

static struct PyModuleDef _junk_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_junk",
    .m_doc = _junk_doc,
    .m_size = sizeof(_junk_state),
    .m_methods = module_methods,
    .m_slots = _junk_slots,
    .m_traverse = _junk_traverse,
    .m_clear = _junk_clear,
    .m_free = _junk_free,
};


extern "C" {

PyMODINIT_FUNC PyInit_junk(void)
{
    return PyModuleDef_Init(&_junk_module);
}

}
