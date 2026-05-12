// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#if PY_VERSION_HEX < 0x030E0000
#  error "This extension requires CPython 3.14+"
#endif

//

#define _MODULE_NAME "_functions"
#define _PACKAGE_NAME "omlish.lang"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

//

typedef struct functions_state {
    PyTypeObject *SetterType;
} functions_state;

static functions_state * get_functions_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != nullptr);
    return (functions_state *)state;
}

//

enum SetterMode {
    SETTER_MODE_ATTR = 0,
    SETTER_MODE_ITEM = 1,
};

typedef struct {
    PyObject_HEAD
    PyObject *key;    // attribute name (str) for attr, key object for item
    PyObject *value;  // bound value, or NULL if unbound
    int mode;         // SetterMode
    vectorcallfunc vectorcall;
} Setter;

static int Setter_traverse(Setter *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    Py_VISIT(self->key);
    Py_VISIT(self->value);
    return 0;
}

static int Setter_clear(Setter *self)
{
    Py_CLEAR(self->key);
    Py_CLEAR(self->value);
    return 0;
}

static void Setter_dealloc(Setter *self)
{
    PyTypeObject *tp = Py_TYPE(self);
    PyObject_GC_UnTrack(self);
    Setter_clear(self);
    tp->tp_free((PyObject *)self);
    Py_DECREF(tp);
}

static int Setter_do_set(Setter *self, PyObject *obj, PyObject *value)
{
    if (self->mode == SETTER_MODE_ATTR) {
        return PyObject_SetAttr(obj, self->key, value);
    } else {
        return PyObject_SetItem(obj, self->key, value);
    }
}

static PyObject * Setter_vectorcall(
    PyObject *callable,
    PyObject *const *args,
    size_t nargsf,
    PyObject *kwnames
)
{
    Setter *self = (Setter *)callable;
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);

    if (kwnames != nullptr && PyTuple_GET_SIZE(kwnames) != 0) {
        PyErr_SetString(PyExc_TypeError, "setter takes no keyword arguments");
        return nullptr;
    }

    PyObject *obj;
    PyObject *value;

    if (self->value != nullptr) {
        if (nargs != 1) {
            PyErr_Format(
                PyExc_TypeError,
                "setter takes exactly 1 positional argument (%zd given)",
                nargs
            );
            return nullptr;
        }
        obj = args[0];
        value = self->value;
    } else {
        if (nargs != 2) {
            PyErr_Format(
                PyExc_TypeError,
                "setter takes exactly 2 positional arguments (%zd given)",
                nargs
            );
            return nullptr;
        }
        obj = args[0];
        value = args[1];
    }

    if (Setter_do_set(self, obj, value) < 0) {
        return nullptr;
    }

    Py_RETURN_NONE;
}

// tp_call fallback for non-vectorcall callers
static PyObject * Setter_call(Setter *self, PyObject *args, PyObject *kwargs)
{
    if (kwargs != nullptr) {
        Py_ssize_t nkwargs = PyDict_Size(kwargs);
        if (nkwargs < 0) {
            return nullptr;
        }
        if (nkwargs != 0) {
            PyErr_SetString(PyExc_TypeError, "setter takes no keyword arguments");
            return nullptr;
        }
    }

    Py_ssize_t nargs = PyTuple_GET_SIZE(args);
    PyObject *const *stack = (nargs > 0) ? &PyTuple_GET_ITEM(args, 0) : nullptr;
    return Setter_vectorcall((PyObject *)self, stack, (size_t)nargs, nullptr);
}

static PyObject * Setter_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PyErr_SetString(PyExc_TypeError, "Setter objects cannot be created directly");
    return nullptr;
}

static PyMemberDef Setter_members[] = {
    {"__vectorcalloffset__", T_PYSSIZET, offsetof(Setter, vectorcall), READONLY, ""},
    {nullptr}
};

static PyType_Slot Setter_slots[] = {
    {Py_tp_dealloc, (void *) Setter_dealloc},
    {Py_tp_traverse, (void *) Setter_traverse},
    {Py_tp_clear, (void *) Setter_clear},
    {Py_tp_call, (void *) Setter_call},
    {Py_tp_new, (void *) Setter_new},
    {Py_tp_members, (void *) Setter_members},
    {Py_tp_doc, (void *) "Callable that sets an attribute or item"},
    {0, nullptr}
};

static PyType_Spec Setter_spec = {
    .name = _MODULE_FULL_NAME ".Setter",
    .basicsize = sizeof(Setter),
    .itemsize = 0,
    .flags =
        Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_HAVE_GC |
        Py_TPFLAGS_HAVE_VECTORCALL |
        Py_TPFLAGS_IMMUTABLETYPE,
    .slots = Setter_slots,
};

//

static PyObject * make_setter(
    PyObject *module,
    int mode,
    PyObject *key,
    PyObject *value
)
{
    functions_state *state = get_functions_state(module);
    Setter *self = PyObject_GC_New(Setter, state->SetterType);
    if (self == nullptr) {
        return nullptr;
    }

    self->mode = mode;
    self->key = Py_NewRef(key);
    self->value = Py_XNewRef(value);
    self->vectorcall = Setter_vectorcall;

    PyObject_GC_Track(self);
    return (PyObject *)self;
}

//

PyDoc_STRVAR(functions_attrsetter_doc, "attrsetter(a, v=...)");

static PyObject * functions_attrsetter(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs < 1 || nargs > 2) {
        PyErr_Format(
            PyExc_TypeError,
            "attrsetter() takes 1 or 2 positional arguments (%zd given)",
            nargs
        );
        return nullptr;
    }

    PyObject *a = args[0];
    if (!PyUnicode_Check(a)) {
        PyErr_SetString(PyExc_TypeError, "attrsetter() first argument must be a string");
        return nullptr;
    }

    PyObject *v = (nargs == 2) ? args[1] : nullptr;
    return make_setter(module, SETTER_MODE_ATTR, a, v);
}

//

PyDoc_STRVAR(functions_itemsetter_doc, "itemsetter(k, v=...)");

static PyObject * functions_itemsetter(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs < 1 || nargs > 2) {
        PyErr_Format(
            PyExc_TypeError,
            "itemsetter() takes 1 or 2 positional arguments (%zd given)",
            nargs
        );
        return nullptr;
    }

    PyObject *k = args[0];
    PyObject *v = (nargs == 2) ? args[1] : nullptr;
    return make_setter(module, SETTER_MODE_ITEM, k, v);
}

//

PyDoc_STRVAR(functions_doc, "Native C++ implementations for omlish.lang.functions");

static int functions_exec(PyObject *module)
{
    functions_state *state = get_functions_state(module);

    state->SetterType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &Setter_spec,
        nullptr
    );
    if (state->SetterType == nullptr) {
        return -1;
    }

    return 0;
}

static int functions_traverse(PyObject *module, visitproc visit, void *arg)
{
    functions_state *state = get_functions_state(module);
    Py_VISIT(state->SetterType);
    return 0;
}

static int functions_clear(PyObject *module)
{
    functions_state *state = get_functions_state(module);
    Py_CLEAR(state->SetterType);
    return 0;
}

static void functions_free(void *module)
{
    functions_clear((PyObject *)module);
}

static PyMethodDef functions_methods[] = {
    {"attrsetter", (PyCFunction)functions_attrsetter, METH_FASTCALL, functions_attrsetter_doc},
    {"itemsetter", (PyCFunction)functions_itemsetter, METH_FASTCALL, functions_itemsetter_doc},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef_Slot functions_slots[] = {
    {Py_mod_exec, (void *)functions_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, nullptr}
};

static struct PyModuleDef functions_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = functions_doc,
    .m_size = sizeof(functions_state),
    .m_methods = functions_methods,
    .m_slots = functions_slots,
    .m_traverse = functions_traverse,
    .m_clear = functions_clear,
    .m_free = functions_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__functions(void)
{
    return PyModuleDef_Init(&functions_module);
}

}
