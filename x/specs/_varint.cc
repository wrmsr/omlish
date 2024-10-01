/*
#include <Python.h>

// C implementation of the read_varint function
static PyObject* read_varint(PyObject* self, PyObject* args) {
    PyObject *iterator, *item;
    unsigned long long result = 0;
    int shift = 0;

    // Parse the input arguments: a Python iterator
    if (!PyArg_ParseTuple(args, "O", &iterator)) {
        return NULL;
    }

    // Check if the input object is iterable
    iterator = PyObject_GetIter(iterator);
    if (!iterator) {
        PyErr_SetString(PyExc_TypeError, "Argument must be an iterator");
        return NULL;
    }

    // Iterate over the provided data
    while ((item = PyIter_Next(iterator))) {
        if (!PyLong_Check(item)) {
            Py_DECREF(item);
            Py_DECREF(iterator);
            PyErr_SetString(PyExc_TypeError, "Iterator must yield integers");
            return NULL;
        }

        int byte = (int)PyLong_AsLong(item);
        Py_DECREF(item);

        result |= (byte & 0x7F) << shift;
        shift += 7;

        if (!(byte & 0x80)) {
            break;
        }
    }

    Py_DECREF(iterator);

    if (PyErr_Occurred()) {
        return NULL;  // Return NULL if there was an error during iteration
    }

    // Return the result as a Python integer
    return PyLong_FromUnsignedLongLong(result);
}

// Define the methods of the module
static PyMethodDef VarintMethods[] = {
    {"read_varint", read_varint, METH_VARARGS, "Read a variable-length integer from an iterator of bytes."},
    {NULL, NULL, 0, NULL}  // Sentinel value to signal end of the array
};

// Define the module
static struct PyModuleDef varintmodule = {
    PyModuleDef_HEAD_INIT,
    "varint",  // Module name
    NULL,      // Module documentation (optional)
    -1,        // Size of per-interpreter state or -1 if module keeps state in global variables
    VarintMethods
};

// Initialize the module
PyMODINIT_FUNC PyInit_varint(void) {
    return PyModule_Create(&varintmodule);
}
*/
