// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

//

#define _MODULE_NAME "_comparison"
#define _PACKAGE_NAME "omlish.lang"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

//

typedef struct comparison_state {
    PyTypeObject *KeyCmpType;
} comparison_state;

static comparison_state * get_comparison_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != nullptr);
    return (comparison_state *)state;
}

//

PyDoc_STRVAR(comparison_cmp_doc, "cmp(l, r)");

static PyObject * comparison_cmp(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2) {
        PyErr_Format(
            PyExc_TypeError,
            "cmp() takes exactly 2 positional arguments (%zd given)",
            nargs
        );
        return nullptr;
    }

    PyObject *l = args[0];
    PyObject *r = args[1];

    int lt = PyObject_RichCompareBool(l, r, Py_LT);
    if (lt < 0) {
        return nullptr;
    }
    if (lt) {
        return PyLong_FromLong(-1);
    }

    int gt = PyObject_RichCompareBool(l, r, Py_GT);
    if (gt < 0) {
        return nullptr;
    }

    return PyLong_FromLong(gt);
}

//

typedef struct {
    PyObject_HEAD
    PyObject *fn;
    vectorcallfunc vectorcall;
} KeyCmp;

static int KeyCmp_traverse(KeyCmp *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    Py_VISIT(self->fn);
    return 0;
}

static int KeyCmp_clear(KeyCmp *self)
{
    Py_CLEAR(self->fn);
    return 0;
}

static void KeyCmp_dealloc(KeyCmp *self)
{
    PyTypeObject *tp = Py_TYPE(self); // Grab reference before cleanup
    PyObject_GC_UnTrack(self);
    KeyCmp_clear(self);
    tp->tp_free((PyObject *)self);
    Py_DECREF(tp); // Drop reference to the heap type!
}

// Default vectorcall: inline rich compare on tuple keys
static PyObject * KeyCmp_vectorcall_default(
    PyObject *callable,
    PyObject *const *args,
    size_t nargsf,
    PyObject *kwnames
)
{
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);

    if (kwnames != nullptr && PyTuple_GET_SIZE(kwnames) != 0) {
        PyErr_SetString(PyExc_TypeError, "KeyCmp takes no keyword arguments");
        return nullptr;
    }

    if (nargs != 2) {
        PyErr_Format(
            PyExc_TypeError,
            "KeyCmp takes exactly 2 positional arguments (%zd given)",
            nargs
        );
        return nullptr;
    }

    PyObject *t0 = args[0];
    PyObject *t1 = args[1];

    // Quick, macro-based type and bounds checking
    if (!PyTuple_CheckExact(t0) || PyTuple_GET_SIZE(t0) < 2 ||
        !PyTuple_CheckExact(t1) || PyTuple_GET_SIZE(t1) < 2) {
        PyErr_SetString(
            PyExc_TypeError,
            "KeyCmp arguments must be exactly tuples of at least 2 items"
        );
        return nullptr;
    }

    PyObject *k0 = PyTuple_GET_ITEM(t0, 0);
    PyObject *k1 = PyTuple_GET_ITEM(t1, 0);

    int lt = PyObject_RichCompareBool(k0, k1, Py_LT);
    if (lt < 0) {
        return nullptr;
    }
    if (lt) {
        return PyLong_FromLong(-1);
    }

    int gt = PyObject_RichCompareBool(k0, k1, Py_GT);
    if (gt < 0) {
        return nullptr;
    }

    return PyLong_FromLong(gt);
}

// Custom vectorcall: extract keys, delegate to stored fn via vectorcall
static PyObject * KeyCmp_vectorcall_custom(
    PyObject *callable,
    PyObject *const *args,
    size_t nargsf,
    PyObject *kwnames
)
{
    KeyCmp *self = (KeyCmp *)callable;
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);

    if (kwnames != nullptr && PyTuple_GET_SIZE(kwnames) != 0) {
        PyErr_SetString(PyExc_TypeError, "KeyCmp takes no keyword arguments");
        return nullptr;
    }

    if (nargs != 2) {
        PyErr_Format(
            PyExc_TypeError,
            "KeyCmp takes exactly 2 positional arguments (%zd given)",
            nargs
        );
        return nullptr;
    }

    PyObject *t0 = args[0];
    PyObject *t1 = args[1];

    // Quick, macro-based type and bounds checking
    if (!PyTuple_CheckExact(t0) || PyTuple_GET_SIZE(t0) < 2 ||
        !PyTuple_CheckExact(t1) || PyTuple_GET_SIZE(t1) < 2) {
        PyErr_SetString(
            PyExc_TypeError,
            "KeyCmp arguments must be exactly tuples of at least 2 items"
        );
        return nullptr;
    }

    PyObject *keys[2] = {
        PyTuple_GET_ITEM(t0, 0),
        PyTuple_GET_ITEM(t1, 0),
    };

    return PyObject_Vectorcall(self->fn, keys, 2, nullptr);
}

// tp_call fallback for non-vectorcall callers
static PyObject * KeyCmp_call(KeyCmp *self, PyObject *args, PyObject *kwargs)
{
    if (kwargs != nullptr && PyDict_GET_SIZE(kwargs) != 0) {
        PyErr_SetString(PyExc_TypeError, "KeyCmp takes no keyword arguments");
        return nullptr;
    }

    Py_ssize_t nargs = PyTuple_GET_SIZE(args);
    if (nargs != 2) {
        PyErr_Format(
            PyExc_TypeError,
            "KeyCmp takes exactly 2 positional arguments (%zd given)",
            nargs
        );
        return nullptr;
    }

    PyObject *const call_args[2] = {
        PyTuple_GET_ITEM(args, 0),
        PyTuple_GET_ITEM(args, 1),
    };

    return self->vectorcall((PyObject *)self, call_args, 2, nullptr);
}

static PyMemberDef KeyCmp_members[] = {
    {"__vectorcalloffset__", T_PYSSIZET, offsetof(KeyCmp, vectorcall), READONLY, ""},
    {nullptr}
};

static PyType_Slot KeyCmp_slots[] = {
    {Py_tp_dealloc, (void *) KeyCmp_dealloc},
    {Py_tp_traverse, (void *) KeyCmp_traverse},
    {Py_tp_clear, (void *) KeyCmp_clear},
    {Py_tp_call, (void *) KeyCmp_call},
    {Py_tp_members, (void *) KeyCmp_members},
    {Py_tp_doc, (void *) "Callable comparing tuples by first element"},
    {0, nullptr}
};

static PyType_Spec KeyCmp_spec = {
    .name = _MODULE_FULL_NAME ".KeyCmp",
    .basicsize = sizeof(KeyCmp),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_HAVE_VECTORCALL,
    .slots = KeyCmp_slots,
};

//

PyDoc_STRVAR(comparison_key_cmp_doc, "key_cmp(fn=None)");

static PyObject * comparison_key_cmp(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs > 1) {
        PyErr_Format(
            PyExc_TypeError,
            "key_cmp() takes at most 1 positional argument (%zd given)",
            nargs
        );
        return nullptr;
    }

    PyObject *fn = nullptr;
    if (nargs == 1 && args[0] != Py_None) {
        fn = args[0];
        if (!PyCallable_Check(fn)) {
            PyErr_SetString(PyExc_TypeError, "key_cmp() argument must be callable or None");
            return nullptr;
        }
    }

    comparison_state *state = get_comparison_state(module);
    KeyCmp *self = PyObject_GC_New(KeyCmp, state->KeyCmpType);
    if (self == nullptr) {
        return nullptr;
    }

    self->fn = Py_XNewRef(fn);
    self->vectorcall = (fn != nullptr) ? KeyCmp_vectorcall_custom : KeyCmp_vectorcall_default;

    PyObject_GC_Track(self);
    return (PyObject *)self;
}

//

PyDoc_STRVAR(comparison_doc, "Native C++ implementations for omlish.lang.comparison");

static int comparison_exec(PyObject *module)
{
    comparison_state *state = get_comparison_state(module);

    state->KeyCmpType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &KeyCmp_spec,
        nullptr
    );
    if (state->KeyCmpType == nullptr) {
        return -1;
    }

    return 0;
}

static int comparison_traverse(PyObject *module, visitproc visit, void *arg)
{
    comparison_state *state = get_comparison_state(module);
    Py_VISIT(state->KeyCmpType);
    return 0;
}

static int comparison_clear(PyObject *module)
{
    comparison_state *state = get_comparison_state(module);
    Py_CLEAR(state->KeyCmpType);
    return 0;
}

static void comparison_free(void *module)
{
    comparison_clear((PyObject *)module);
}

static PyMethodDef comparison_methods[] = {
    {"cmp", (PyCFunction)comparison_cmp, METH_FASTCALL, comparison_cmp_doc},
    {"key_cmp", (PyCFunction)comparison_key_cmp, METH_FASTCALL, comparison_key_cmp_doc},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef_Slot comparison_slots[] = {
    {Py_mod_exec, (void *)comparison_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, nullptr}
};

static struct PyModuleDef comparison_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = comparison_doc,
    .m_size = sizeof(comparison_state),
    .m_methods = comparison_methods,
    .m_slots = comparison_slots,
    .m_traverse = comparison_traverse,
    .m_clear = comparison_clear,
    .m_free = comparison_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__comparison(void)
{
    return PyModuleDef_Init(&comparison_module);
}

}
