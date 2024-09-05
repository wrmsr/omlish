#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

typedef struct junk_state {
} junk_state;

// static inline junk_state * get_junk_state(PyObject *module)
// {
//     void *state = PyModule_GetState(module);
//     assert(state != NULL);
//     return (junk_state *)state;
// }

//

static PyObject * junk(PyObject *self, PyObject *args)
{
    return Py_BuildValue("k", 424);
}

//

PyDoc_STRVAR(junk_doc, "junk");

static int junk_exec(PyObject *module)
{
    // junk_state *state = get_junk_state(module);
    return 0;
}

static int junk_traverse(PyObject *module, visitproc visit, void *arg)
{
    // junk_state *state = get_junk_state(module);
    return 0;
}

static int junk_clear(PyObject *module)
{
    // junk_state *state = get_junk_state(module);
    return 0;
}

static void junk_free(void *module)
{
    junk_clear((PyObject *)module);
}

static PyMethodDef junk_methods[] = {
    {"junk", junk, METH_NOARGS, "junk"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot junk_slots[] = {
    {Py_mod_exec, (void *) junk_exec},
    {0, NULL}
};

static struct PyModuleDef junk_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "junk",
    .m_doc = junk_doc,
    .m_size = sizeof(junk_state),
    .m_methods = junk_methods,
    .m_slots = junk_slots,
    .m_traverse = junk_traverse,
    .m_clear = junk_clear,
    .m_free = junk_free,
};

extern "C" {

PyMODINIT_FUNC PyInit_junk(void)
{
    return PyModuleDef_Init(&junk_module);
}

}
