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
    PyTypeObject *BoundUnaryCheckType;
    PyTypeObject *BoundBinaryCheckType;
} check_state;

static inline check_state * get_check_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != nullptr);
    return (check_state *)state;
}

//

PyDoc_STRVAR(unpack_isinstance_spec_doc, "unpack_isinstance_spec(spec)");

static PyObject * unpack_isinstance_spec(PyObject *module, PyObject *spec)
{
    check_state *state = get_check_state(module);

    // If spec is typing.Any return object
    if (state->typing_any != nullptr) {
        int cmp = PyObject_RichCompareBool(spec, state->typing_any, Py_EQ);
        if (cmp < 0) {
            return nullptr;
        }
        if (cmp) {
            return Py_NewRef((PyObject *)&PyBaseObject_Type);
        }
    }

    // Handle 'is None' -> return NoneType
    if (spec == Py_None) {
        return Py_NewRef((PyObject *)state->nonetype);
    }

    // If not a tuple, return it directly
    if (!PyTuple_Check(spec)) {
        Py_INCREF(spec);
        return spec;
    }

    Py_ssize_t size = PyTuple_Size(spec);
    bool has_none = false;

    // Check for typing.Any and None
    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject *item = PyTuple_GetItem(spec, i);
        if (item == nullptr) {
            return nullptr;
        }

        // If typing.Any is in spec, return object
        if (state->typing_any != nullptr) {
            int cmp = PyObject_RichCompareBool(item, state->typing_any, Py_EQ);
            if (cmp < 0) {
                return nullptr;
            }
            if (cmp) {
                return Py_NewRef((PyObject *)&PyBaseObject_Type);
            }
        }

        if (item == Py_None) {
            has_none = true;
        }
    }

    // If None is in spec, filter it out and add NoneType
    if (has_none) {
        std::vector<PyObject*> filtered;
        filtered.reserve(size);

        for (Py_ssize_t i = 0; i < size; i++) {
            PyObject *item = PyTuple_GetItem(spec, i);
            if (item != Py_None) {
                filtered.push_back(item);
            }
        }

        filtered.push_back((PyObject *)state->nonetype);

        PyObject *result = PyTuple_New(filtered.size());
        if (result == nullptr) {
            return nullptr;
        }

        for (size_t i = 0; i < filtered.size(); i++) {
            Py_INCREF(filtered[i]);
            PyTuple_SET_ITEM(result, i, filtered[i]);
        }
        return result;
    }

    // Return the tuple as-is
    Py_INCREF(spec);
    return spec;
}

//

typedef enum {
    UNARY_CHECK_MODE_UNKNOWN,
    UNARY_CHECK_MODE_NONE,
    UNARY_CHECK_MODE_NOT_NONE,
    UNARY_CHECK_MODE_ARG,
    UNARY_CHECK_MODE_STATE,
} bound_unary_check_mode;

typedef struct {
    PyObject_HEAD
    PyObject *fn;
    PyObject *module;
    vectorcallfunc vectorcall;
    bound_unary_check_mode mode;
} BoundUnaryCheck;

static int BoundUnaryCheck_traverse(BoundUnaryCheck *self, visitproc visit, void *arg)
{
    Py_VISIT(self->fn);
    Py_VISIT(self->module);
    return 0;
}

static int BoundUnaryCheck_clear(BoundUnaryCheck *self)
{
    Py_CLEAR(self->fn);
    Py_CLEAR(self->module);
    return 0;
}

static void BoundUnaryCheck_dealloc(BoundUnaryCheck *self)
{
    PyObject_GC_UnTrack(self);
    BoundUnaryCheck_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject * BoundUnaryCheck_execute(BoundUnaryCheck *self, PyObject *v, PyObject *msg)
{
    int res;
    switch (self->mode) {
        case UNARY_CHECK_MODE_NONE:
            if (v == Py_None) {
                return Py_NewRef(v);
            }
            break;

        case UNARY_CHECK_MODE_NOT_NONE:
            if (v != Py_None) {
                return Py_NewRef(v);
            }
            break;

        case UNARY_CHECK_MODE_ARG:
        case UNARY_CHECK_MODE_STATE:
            res = PyObject_IsTrue(v);
            if (res > 0) {
                return Py_NewRef(v);
            } else if (res < 0) {
                // An exception occurred during truth evaluation (e.g., __bool__ failed)
                return nullptr;
            }
            // res == 0, fall through to Python fallback
            break;

        default:
            break;
    }

    return PyObject_CallFunctionObjArgs(self->fn, v, msg, nullptr);
}

static PyObject * BoundUnaryCheck_call(BoundUnaryCheck *self, PyObject *args, PyObject *kwargs)
{
    PyObject *v;
    PyObject *msg = Py_None;

    if (kwargs != nullptr && PyDict_GET_SIZE(kwargs) != 0) {
        PyErr_SetString(PyExc_TypeError, "unary_check() takes no keyword arguments");
        return nullptr;
    }

    if (!PyArg_ParseTuple(args, "O|O:unary_check", &v, &msg)) {
        return nullptr;
    }

    return BoundUnaryCheck_execute(self, v, msg);
}

static PyObject * BoundUnaryCheck_vectorcall(PyObject *callable, PyObject *const *args, size_t nargsf, PyObject *kwnames)
{
    BoundUnaryCheck *self = (BoundUnaryCheck *)callable;
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);

    if (kwnames != nullptr && PyTuple_GET_SIZE(kwnames) != 0) {
        PyErr_SetString(PyExc_TypeError, "unary_check() takes no keyword arguments");
        return nullptr;
    }

    if (nargs < 1 || nargs > 2) {
        PyErr_Format(PyExc_TypeError, "unary_check() takes from 1 to 2 positional arguments but %zd were given", nargs);
        return nullptr;
    }

    PyObject *v = args[0];
    PyObject *msg = (nargs == 2) ? args[1] : Py_None;

    return BoundUnaryCheck_execute(self, v, msg);
}

static PyType_Slot BoundUnaryCheck_slots[] = {
    {Py_tp_dealloc, (void *)BoundUnaryCheck_dealloc},
    {Py_tp_traverse, (void *)BoundUnaryCheck_traverse},
    {Py_tp_clear, (void *)BoundUnaryCheck_clear},
    {Py_tp_call, (void *)BoundUnaryCheck_call},
    {Py_tp_doc, (void *)"Bound unary check callable with C acceleration"},
    {0, nullptr}
};

static PyType_Spec BoundUnaryCheck_spec = {
    .name = _MODULE_FULL_NAME ".BoundUnaryCheck",
    .basicsize = sizeof(BoundUnaryCheck),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_HAVE_VECTORCALL,
    .slots = BoundUnaryCheck_slots,
};

PyDoc_STRVAR(bind_unary_check_doc, "bind_unary_check(fn)\n\nBind a unary check callable with C acceleration.");

static PyObject * bind_unary_check(PyObject *module, PyObject *fn)
{
    if (!PyCallable_Check(fn)) {
        PyErr_SetString(PyExc_TypeError, "fn must be callable");
        return nullptr;
    }

    // Determine mode from __name__
    PyObject *name_obj = PyObject_GetAttrString(fn, "__name__");
    if (name_obj == nullptr) {
        return nullptr;
    }

    bound_unary_check_mode mode = UNARY_CHECK_MODE_UNKNOWN;
    if (PyUnicode_Check(name_obj)) {
        if (PyUnicode_CompareWithASCIIString(name_obj, "none") == 0) {
            mode = UNARY_CHECK_MODE_NONE;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "not_none") == 0) {
            mode = UNARY_CHECK_MODE_NOT_NONE;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "arg") == 0) {
            mode = UNARY_CHECK_MODE_ARG;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "state") == 0) {
            mode = UNARY_CHECK_MODE_STATE;
        }
    }

    if (mode == UNARY_CHECK_MODE_UNKNOWN) {
        PyErr_Format(PyExc_TypeError, "Unsupported unary check function: %S", name_obj);
        Py_DECREF(name_obj);
        return nullptr;
    }
    Py_DECREF(name_obj);

    check_state *state = get_check_state(module);
    BoundUnaryCheck *self = PyObject_GC_New(BoundUnaryCheck, state->BoundUnaryCheckType);
    if (self == nullptr) {
        return nullptr;
    }

    self->fn = Py_NewRef(fn);
    self->module = Py_NewRef(module);
    self->vectorcall = BoundUnaryCheck_vectorcall;
    self->mode = mode;

    PyObject_GC_Track(self);
    return (PyObject *)self;
}

//

typedef enum {
    BINARY_CHECK_MODE_UNKNOWN,
    BINARY_CHECK_MODE_EQUAL,
    BINARY_CHECK_MODE_NOT_EQUAL,
    BINARY_CHECK_MODE_IS,
    BINARY_CHECK_MODE_IS_NOT,
    BINARY_CHECK_MODE_IN,
    BINARY_CHECK_MODE_NOT_IN,
    BINARY_CHECK_MODE_ISINSTANCE,
    BINARY_CHECK_MODE_NOT_ISINSTANCE,
    BINARY_CHECK_MODE_ISSUBCLASS,
    BINARY_CHECK_MODE_NOT_ISSUBCLASS,
} bound_binary_check_mode;

typedef struct {
    PyObject_HEAD
    PyObject *fn;
    PyObject *module;
    vectorcallfunc vectorcall;
    bound_binary_check_mode mode;
} BoundBinaryCheck;

static int BoundBinaryCheck_traverse(BoundBinaryCheck *self, visitproc visit, void *arg)
{
    Py_VISIT(self->fn);
    Py_VISIT(self->module);
    return 0;
}

static int BoundBinaryCheck_clear(BoundBinaryCheck *self)
{
    Py_CLEAR(self->fn);
    Py_CLEAR(self->module);
    return 0;
}

static void BoundBinaryCheck_dealloc(BoundBinaryCheck *self)
{
    PyObject_GC_UnTrack(self);
    BoundBinaryCheck_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject * BoundBinaryCheck_execute(BoundBinaryCheck *self, PyObject *l, PyObject *r, PyObject *msg)
{
    int cmp;
    switch (self->mode) {
        case BINARY_CHECK_MODE_EQUAL:
            cmp = PyObject_RichCompareBool(l, r, Py_EQ);
            if (cmp < 0) {
                return nullptr;
            }

            if (cmp > 0) {
                return Py_NewRef(l);
            }
            break;

        case BINARY_CHECK_MODE_NOT_EQUAL:
            cmp = PyObject_RichCompareBool(l, r, Py_NE);
            if (cmp < 0) {
                return nullptr;
            }

            if (cmp > 0) {
                return Py_NewRef(l);
            }
            break;

        case BINARY_CHECK_MODE_IS:
            if (l == r) {
                return Py_NewRef(l);
            }
            break;

        case BINARY_CHECK_MODE_IS_NOT:
            if (l != r) {
                return Py_NewRef(l);
            }
            break;

        case BINARY_CHECK_MODE_IN:
        case BINARY_CHECK_MODE_NOT_IN: {
            // PySequence_Contains(container, item) -> equivalent to 'l in r'
            // Note: CPython arguments are (r, l) for 'l in r'
            int res = PySequence_Contains(r, l);
            if (res < 0) {
                return nullptr; // e.g., TypeError: argument of type 'int' is not iterable
            }

            if (
                (self->mode == BINARY_CHECK_MODE_IN && res > 0) ||
                (self->mode == BINARY_CHECK_MODE_NOT_IN && res == 0)
            ) {
                return Py_NewRef(l);
            }
            break;
        }

        case BINARY_CHECK_MODE_ISINSTANCE:
        case BINARY_CHECK_MODE_NOT_ISINSTANCE: {
            // 1. Unpack the spec (r) using our accelerated logic
            // Note: This returns a new reference
            PyObject *unpacked = unpack_isinstance_spec(self->module, r);
            if (unpacked == nullptr) {
                return nullptr;
            }

            // 2. Perform the actual isinstance check
            // PyObject_IsInstance handles both single types and tuples of types
            int is_inst = PyObject_IsInstance(l, unpacked);
            Py_DECREF(unpacked); // Clean up the reference from unpack_isinstance_spec

            if (is_inst < 0) {
                return nullptr; // Exception in isinstance (e.g. invalid type in tuple)
            }

            if (
                (self->mode == BINARY_CHECK_MODE_ISINSTANCE  && is_inst > 0) ||
                (self->mode == BINARY_CHECK_MODE_NOT_ISINSTANCE  && is_inst == 0)
            ) {
                return Py_NewRef(l);
            }

            // is_inst == 0, fall through to Python fallback for error formatting
            break;
        }

        case BINARY_CHECK_MODE_ISSUBCLASS:
        case BINARY_CHECK_MODE_NOT_ISSUBCLASS: {
            int is_sub = PyObject_IsSubclass(l, r);
            if (is_sub < 0) {
                return nullptr;
            }

            if (
                (self->mode == BINARY_CHECK_MODE_ISSUBCLASS && is_sub > 0) ||
                (self->mode == BINARY_CHECK_MODE_NOT_ISSUBCLASS && is_sub == 0)
            ) {
                return Py_NewRef(l);
            }

            break;
        }

        default:
            // Fallback to Python for unknown modes
            break;
    }

    // Slow path: logic failed or unknown mode, let Python handle exception raising
    return PyObject_CallFunctionObjArgs(self->fn, l, r, msg, nullptr);
}

static PyObject * BoundBinaryCheck_call(BoundBinaryCheck *self, PyObject *args, PyObject *kwargs)
{
    PyObject *l;
    PyObject *r;
    PyObject *msg = Py_None;

    if (kwargs != nullptr && PyDict_GET_SIZE(kwargs) != 0) {
        PyErr_SetString(PyExc_TypeError, "binary_check() takes no keyword arguments");
        return nullptr;
    }

    if (!PyArg_ParseTuple(args, "OO|O:binary_check", &l, &r, &msg)) {
        return nullptr;
    }

    return BoundBinaryCheck_execute(self, l, r, msg);
}

static PyObject * BoundBinaryCheck_vectorcall(PyObject *callable, PyObject *const *args, size_t nargsf, PyObject *kwnames)
{
    BoundBinaryCheck *self = (BoundBinaryCheck *)callable;
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);

    if (kwnames != nullptr && PyTuple_GET_SIZE(kwnames) != 0) {
        PyErr_SetString(PyExc_TypeError, "binary_check() takes no keyword arguments");
        return nullptr;
    }

    if (nargs < 2 || nargs > 3) {
        PyErr_Format(PyExc_TypeError, "binary_check() takes from 2 to 3 positional arguments but %zd were given", nargs);
        return nullptr;
    }

    PyObject *l = args[0];
    PyObject *r = args[1];
    PyObject *msg = (nargs == 3) ? args[2] : Py_None;

    return BoundBinaryCheck_execute(self, l, r, msg);
}

static PyType_Slot BoundBinaryCheck_slots[] = {
    {Py_tp_dealloc, (void *)BoundBinaryCheck_dealloc},
    {Py_tp_traverse, (void *)BoundBinaryCheck_traverse},
    {Py_tp_clear, (void *)BoundBinaryCheck_clear},
    {Py_tp_call, (void *)BoundBinaryCheck_call},
    {Py_tp_doc, (void *)"Bound binary check callable with C acceleration"},
    {0, nullptr}
};

static PyType_Spec BoundBinaryCheck_spec = {
    .name = _MODULE_FULL_NAME ".BoundBinaryCheck",
    .basicsize = sizeof(BoundBinaryCheck),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_HAVE_VECTORCALL,
    .slots = BoundBinaryCheck_slots,
};

PyDoc_STRVAR(bind_binary_check_doc, "bind_binary_check(fn)\n\nBind a binary check callable with C acceleration.");

static PyObject * bind_binary_check(PyObject *module, PyObject *fn)
{
    if (!PyCallable_Check(fn)) {
        PyErr_SetString(PyExc_TypeError, "fn must be callable");
        return nullptr;
    }

    // Determine mode from __name__
    PyObject *name_obj = PyObject_GetAttrString(fn, "__name__");
    if (name_obj == nullptr) {
        return nullptr;
    }

    bound_binary_check_mode mode = BINARY_CHECK_MODE_UNKNOWN;
    if (PyUnicode_Check(name_obj)) {
        if (PyUnicode_CompareWithASCIIString(name_obj, "equal") == 0) {
            mode = BINARY_CHECK_MODE_EQUAL;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "not_equal") == 0) {
            mode = BINARY_CHECK_MODE_NOT_EQUAL;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "is_") == 0) {
            mode = BINARY_CHECK_MODE_IS;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "is_not") == 0) {
            mode = BINARY_CHECK_MODE_IS_NOT;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "in_") == 0) {
            mode = BINARY_CHECK_MODE_IN;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "not_in") == 0) {
            mode = BINARY_CHECK_MODE_NOT_IN;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "isinstance") == 0) {
            mode = BINARY_CHECK_MODE_ISINSTANCE;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "not_isinstance") == 0) {
            mode = BINARY_CHECK_MODE_NOT_ISINSTANCE;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "issubclass") == 0) {
            mode = BINARY_CHECK_MODE_ISSUBCLASS;
        } else if (PyUnicode_CompareWithASCIIString(name_obj, "not_issubclass") == 0) {
            mode = BINARY_CHECK_MODE_NOT_ISSUBCLASS;
        }
    }

    if (mode == BINARY_CHECK_MODE_UNKNOWN) {
        PyErr_Format(PyExc_TypeError, "Unsupported binary check function: %S", name_obj);
        Py_DECREF(name_obj);
        return nullptr;
    }
    Py_DECREF(name_obj);

    check_state *state = get_check_state(module);
    BoundBinaryCheck *self = PyObject_GC_New(BoundBinaryCheck, state->BoundBinaryCheckType);
    if (self == nullptr) {
        return nullptr;
    }

    self->fn = Py_NewRef(fn);
    self->module = Py_NewRef(module);
    self->vectorcall = BoundBinaryCheck_vectorcall;
    self->mode = mode;

    PyObject_GC_Track(self);
    return (PyObject *)self;
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

    // Create the BoundUnaryCheck type dynamically
    state->BoundUnaryCheckType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &BoundUnaryCheck_spec,
        nullptr
    );
    if (state->BoundUnaryCheckType == nullptr) {
        return -1;
    }
    state->BoundUnaryCheckType->tp_vectorcall_offset = offsetof(BoundUnaryCheck, vectorcall);

    // Create the BoundBinaryCheck type dynamically
    state->BoundBinaryCheckType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &BoundBinaryCheck_spec,
        nullptr
    );
    if (state->BoundBinaryCheckType == nullptr) {
        return -1;
    }
    state->BoundBinaryCheckType->tp_vectorcall_offset = offsetof(BoundBinaryCheck, vectorcall);

    return 0;
}

static int check_traverse(PyObject *module, visitproc visit, void *arg)
{
    check_state *state = get_check_state(module);
    Py_VISIT(state->typing_any);
    Py_VISIT(state->nonetype);
    Py_VISIT(state->BoundUnaryCheckType);
    Py_VISIT(state->BoundBinaryCheckType);
    return 0;
}

static int check_clear(PyObject *module)
{
    check_state *state = get_check_state(module);
    Py_CLEAR(state->typing_any);
    Py_CLEAR(state->nonetype);
    Py_CLEAR(state->BoundUnaryCheckType);
    Py_CLEAR(state->BoundBinaryCheckType);
    return 0;
}

static void check_free(void *module)
{
    check_clear((PyObject *)module);
}

static PyMethodDef check_methods[] = {
    {"unpack_isinstance_spec", (PyCFunction)unpack_isinstance_spec, METH_O, unpack_isinstance_spec_doc},
    {"bind_unary_check", (PyCFunction)bind_unary_check, METH_O, bind_unary_check_doc},
    {"bind_binary_check", (PyCFunction)bind_binary_check, METH_O, bind_binary_check_doc},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef_Slot check_slots[] = {
    {Py_mod_exec, (void *) check_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, nullptr}
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
