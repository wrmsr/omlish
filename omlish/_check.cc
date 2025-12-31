// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <vector>

//

#define _MODULE_NAME "_check"
#define _PACKAGE_NAME "omlish"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

typedef struct check_state {
    PyObject *typing_any;
    PyTypeObject *nonetype;
} check_state;

static inline check_state * get_check_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (check_state *)state;
}

//

PyDoc_STRVAR(unpack_isinstance_spec_doc, "unpack_isinstance_spec(spec)");

static PyObject * unpack_isinstance_spec(PyObject *module, PyObject *spec)
{
    check_state *state = get_check_state(module);

    // If spec is a type, return (spec,)
    if (PyType_Check(spec)) {
        return PyTuple_Pack(1, spec);
    }

    PyObject *tuple_spec = nullptr;

    // If not a tuple, wrap it in a tuple
    if (!PyTuple_Check(spec)) {
        tuple_spec = PyTuple_Pack(1, spec);
        if (tuple_spec == nullptr) {
            return nullptr;
        }
    } else {
        // It's already a tuple, so we'll work with it
        tuple_spec = spec;
        Py_INCREF(tuple_spec);
    }

    // Check if None is in spec
    Py_ssize_t size = PyTuple_Size(tuple_spec);
    if (size < 0) {
        Py_DECREF(tuple_spec);
        return nullptr;
    }

    bool has_none = false;
    bool has_any = false;

    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject *item = PyTuple_GetItem(tuple_spec, i);  // borrowed reference
        if (item == nullptr) {
            Py_DECREF(tuple_spec);
            return nullptr;
        }

        if (item == Py_None) {
            has_none = true;
        }

        // Check if item is typing.Any
        if (state->typing_any != nullptr) {
            int cmp = PyObject_RichCompareBool(item, state->typing_any, Py_EQ);
            if (cmp < 0) {
                Py_DECREF(tuple_spec);
                return nullptr;
            }
            if (cmp) {
                has_any = true;
            }
        }
    }

    // If typing.Any is in spec, return (object,)
    if (has_any) {
        Py_DECREF(tuple_spec);
        return PyTuple_Pack(1, &PyBaseObject_Type);
    }

    // If None is in spec, filter it out and add NoneType
    if (has_none) {
        std::vector<PyObject*> filtered;
        filtered.reserve(size);

        for (Py_ssize_t i = 0; i < size; i++) {
            PyObject *item = PyTuple_GetItem(tuple_spec, i);  // borrowed reference
            if (item != Py_None) {
                filtered.push_back(item);
            }
        }

        // Add NoneType
        filtered.push_back((PyObject *)state->nonetype);

        // Create new tuple
        PyObject *result = PyTuple_New(filtered.size());
        if (result == nullptr) {
            Py_DECREF(tuple_spec);
            return nullptr;
        }

        for (size_t i = 0; i < filtered.size(); i++) {
            Py_INCREF(filtered[i]);
            PyTuple_SET_ITEM(result, i, filtered[i]);
        }

        Py_DECREF(tuple_spec);
        return result;
    }

    // Return the tuple as-is
    return tuple_spec;
}

//

PyDoc_STRVAR(check_doc, "Native C++ implementations for omlish.lite.check");

static int check_exec(PyObject *module)
{
    check_state *state = get_check_state(module);

    // Get typing.Any
    PyObject *typing_module = PyImport_ImportModule("typing");
    if (typing_module == nullptr) {
        // If typing module is not available, just set to nullptr
        PyErr_Clear();
        state->typing_any = nullptr;
    } else {
        state->typing_any = PyObject_GetAttrString(typing_module, "Any");
        Py_DECREF(typing_module);
        if (state->typing_any == nullptr) {
            PyErr_Clear();
        }
    }

    // Get NoneType (type(None))
    state->nonetype = Py_TYPE(Py_None);
    Py_INCREF(state->nonetype);

    return 0;
}

static int check_traverse(PyObject *module, visitproc visit, void *arg)
{
    check_state *state = get_check_state(module);
    Py_VISIT(state->typing_any);
    Py_VISIT(state->nonetype);
    return 0;
}

static int check_clear(PyObject *module)
{
    check_state *state = get_check_state(module);
    Py_CLEAR(state->typing_any);
    Py_CLEAR(state->nonetype);
    return 0;
}

static void check_free(void *module)
{
    check_clear((PyObject *)module);
}

static PyMethodDef check_methods[] = {
    {"unpack_isinstance_spec", (PyCFunction)unpack_isinstance_spec, METH_O, unpack_isinstance_spec_doc},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot check_slots[] = {
    {Py_mod_exec, (void *) check_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, NULL}
};

static struct PyModuleDef check_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = check_doc,
    .m_size = sizeof(check_state),
    .m_methods = check_methods,
    .m_slots = check_slots,
    .m_traverse = check_traverse,
    .m_clear = check_clear,
    .m_free = check_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__check(void)
{
    return PyModuleDef_Init(&check_module);
}

}
