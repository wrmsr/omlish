#include <Python.h>

#include <unistd.h>


static PyObject *
junk(PyObject *self, PyObject *args)
{
    return Py_BuildValue("k", 420);
}


static PyMethodDef module_methods[] = {
    {"junk", junk, METH_NOARGS, "junk"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "junk",
    "junk extension",
    -1,
    module_methods
};


extern "C" {

PyMODINIT_FUNC
PyInit_junk(void)
{
    PyObject *m;

    m = PyModule_Create(&module_def);

    if (m == NULL) {
        return NULL;
    }
    return m;
}

}
