// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

//

#define _MODULE_NAME "_dispatch"
#define _PACKAGE_NAME "omlish.dispatch"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

typedef struct {
    PyTypeObject *DispatchCacheType;
} dispatch_state;

static inline dispatch_state * get_dispatch_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (dispatch_state *)state;
}

//

typedef struct {
    PyObject_HEAD
    PyObject *token;
    PyObject *dct;  // weakref dict
    PyObject *impls_by_arg_cls;
    PyObject *find_impl;
    PyObject *reset_cache_for_token;
    PyObject *abc_get_cache_token;
    PyObject *dict;
} DispatchCache;

// Callback Logic

// Accepts 'self' as the DispatchCache instance directly
static PyObject * dct_remove_callback(PyObject *self, PyObject *cls_weakref)
{
    DispatchCache *cache = (DispatchCache *)self;
    // Remove the entry from dct using the weakref as key
    if (PyDict_DelItem(cache->dct, cls_weakref) < 0) {
        if (PyErr_ExceptionMatches(PyExc_KeyError)) {
            PyErr_Clear();
        }
    }
    Py_RETURN_NONE;
}

static PyMethodDef dct_remove_method_def = {
    "dct_remove",
    (PyCFunction)dct_remove_callback,
    METH_O,
    "Cleanup callback for weakref"
};

// Lifecycle

static int DispatchCache_traverse(DispatchCache *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self)); // Fix 3: Visit the heap type
    Py_VISIT(self->token);
    Py_VISIT(self->dct);
    Py_VISIT(self->impls_by_arg_cls);
    Py_VISIT(self->find_impl);
    Py_VISIT(self->reset_cache_for_token);
    Py_VISIT(self->abc_get_cache_token);
    Py_VISIT(self->dict);
    return 0;
}

static int DispatchCache_clear(DispatchCache *self)
{
    Py_CLEAR(self->token);
    Py_CLEAR(self->dct);
    Py_CLEAR(self->impls_by_arg_cls);
    Py_CLEAR(self->find_impl);
    Py_CLEAR(self->reset_cache_for_token);
    Py_CLEAR(self->abc_get_cache_token);
    Py_CLEAR(self->dict);
    return 0;
}

static void DispatchCache_dealloc(DispatchCache *self)
{
    PyObject_GC_UnTrack(self);
    DispatchCache_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

// Helper to create a weakref with cleanup callback using native API
static PyObject * create_weakref_with_callback(DispatchCache *self, PyObject *cls)
{
    // Create a bound C function where 'self' is this DispatchCache instance
    PyObject *callback = PyCFunction_New(&dct_remove_method_def, (PyObject *)self);
    if (callback == nullptr) {
        return nullptr;
    }

    // Native weakref creation: avoids 'import weakref'
    PyObject *cls_ref = PyWeakref_NewRef(cls, callback);
    Py_DECREF(callback);
    return cls_ref;
}

static PyObject * DispatchCache_call(DispatchCache *self, PyObject *args, PyObject *kwargs)
{
    PyObject *cls;
    if (!PyArg_ParseTuple(args, "O", &cls)) {
        return nullptr;
    }

    // ABC Token Check
    if (self->token != Py_None) {
        PyObject *current_token = PyObject_CallNoArgs(self->abc_get_cache_token);
        if (current_token == nullptr) {
            return nullptr;
        }

        int token_matches = PyObject_RichCompareBool(current_token, self->token, Py_EQ);
        Py_DECREF(current_token);
        if (token_matches < 0) {
            return nullptr;
        }

        if (!token_matches) {
            PyObject *result = PyObject_CallOneArg(self->reset_cache_for_token, (PyObject *)self);
            if (result == nullptr) {
                return nullptr;
            }
            Py_DECREF(result);

            // Re-find after reset
            PyObject *find_args = PyTuple_Pack(2, cls, self->impls_by_arg_cls);
            if (find_args == nullptr) {
                return nullptr;
            }
            result = PyObject_Call(self->find_impl, find_args, nullptr);
            Py_DECREF(find_args);
            return result;
        }
    }

    // 1. Fast Path: weakref cache lookup (No callback for temporary ref)
    PyObject *temp_ref = PyWeakref_NewRef(cls, nullptr);
    if (temp_ref == nullptr) {
        return nullptr;
    }

    // Fix 1: Use GetItemWithError to catch hashing exceptions
    PyObject *impl = PyDict_GetItemWithError(self->dct, temp_ref);
    Py_DECREF(temp_ref);

    if (impl != nullptr) {
        return Py_NewRef(impl);
    } else if (PyErr_Occurred()) {
        return nullptr;
    }

    // 2. Medium Path: Direct dict lookup
    impl = PyDict_GetItemWithError(self->impls_by_arg_cls, cls);
    if (impl == nullptr && PyErr_Occurred()) {
        return nullptr;
    }

    if (impl == nullptr) {
        // 3. Slow Path: find_impl
        PyObject *find_args = PyTuple_Pack(2, cls, self->impls_by_arg_cls);
        if (find_args == nullptr) {
            return nullptr;
        }
        impl = PyObject_Call(self->find_impl, find_args, nullptr);
        Py_DECREF(find_args);
        if (impl == nullptr) {
            return nullptr;
        }
    } else {
        Py_INCREF(impl); // Found in impls_by_arg_cls, need to own it for the return
    }

    // Store in cache with weakref + callback
    PyObject *cls_ref_with_callback = create_weakref_with_callback(self, cls);
    if (cls_ref_with_callback == nullptr) {
        Py_DECREF(impl);
        return nullptr;
    }

    if (PyDict_SetItem(self->dct, cls_ref_with_callback, impl) < 0) {
        Py_DECREF(cls_ref_with_callback);
        Py_DECREF(impl);
        return nullptr;
    }
    Py_DECREF(cls_ref_with_callback);
    return impl;
}

// ... (DispatchCache_get_dict, set_dict, getattro, setattro remain largely same,
// ensuring Py_NewRef usage for C++20 style)

static PyObject * DispatchCache_get_dict(DispatchCache *self, void *closure)
{
    if (self->dict == nullptr) {
        if ((self->dict = PyDict_New()) == nullptr) {
            return nullptr;
        }
    }
    return Py_NewRef(self->dict);
}

static int DispatchCache_set_dict(DispatchCache *self, PyObject *value, void *closure)
{
    if (value == nullptr) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete __dict__");
        return -1;
    }
    if (!PyDict_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "__dict__ must be a dictionary");
        return -1;
    }
    Py_XSETREF(self->dict, Py_NewRef(value));
    return 0;
}

static PyObject * DispatchCache_getattro(DispatchCache *self, PyObject *name)
{
    if (self->dict != nullptr) {
        PyObject *res = PyDict_GetItemWithError(self->dict, name);
        if (res != nullptr) {
            return Py_NewRef(res);
        }
        if (PyErr_Occurred()) {
            return nullptr;
        }
    }
    return PyObject_GenericGetAttr((PyObject *)self, name);
}

static int DispatchCache_setattro(DispatchCache *self, PyObject *name, PyObject *value)
{
    if (self->dict == nullptr) {
        if ((self->dict = PyDict_New()) == nullptr) {
            return -1;
        }
    }
    return (value == nullptr) ? PyDict_DelItem(self->dict, name)
                              : PyDict_SetItem(self->dict, name, value);
}

static PyObject * DispatchCache_get_dispatch(DispatchCache *self, void *closure)
{
    return Py_NewRef((PyObject *)self);
}

static PyObject * DispatchCache_get_token(DispatchCache *self, void *closure)
{
    return Py_NewRef(self->token);
}

static PyObject * DispatchCache_get_dct(DispatchCache *self, void *closure)
{
    return Py_NewRef(self->dct);
}

static PyGetSetDef DispatchCache_getsets[] = {
    {"__dict__", (getter)DispatchCache_get_dict, (setter)DispatchCache_set_dict, nullptr, nullptr},
    {"dispatch", (getter)DispatchCache_get_dispatch, nullptr, nullptr, nullptr},
    {"token", (getter)DispatchCache_get_token, nullptr, nullptr, nullptr},
    {"dct", (getter)DispatchCache_get_dct, nullptr, nullptr, nullptr},
    {nullptr}
};

static PyType_Slot DispatchCache_slots[] = {
    {Py_tp_dealloc, (void *)DispatchCache_dealloc},
    {Py_tp_call, (void *)DispatchCache_call},
    {Py_tp_traverse, (void *)DispatchCache_traverse},
    {Py_tp_clear, (void *)DispatchCache_clear},
    {Py_tp_getattro, (void *)DispatchCache_getattro},
    {Py_tp_setattro, (void *)DispatchCache_setattro},
    {Py_tp_getset, DispatchCache_getsets},
    {0, nullptr}
};

static PyType_Spec DispatchCache_spec = {
    .name = _MODULE_FULL_NAME ".DispatchCache",
    .basicsize = sizeof(DispatchCache),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = DispatchCache_slots,
};

//

PyDoc_STRVAR(build_dispatch_cache_doc,
"build_dispatch_cache(impls_by_arg_cls, find_impl, reset_cache_for_token, token)\n\
\n\
Create a fast dispatch cache.\n\
\n\
Args:\n\
    impls_by_arg_cls: Dict mapping types to implementations\n\
    find_impl: Callable for MRO-based lookup on cache miss\n\
    reset_cache_for_token: Callback to reset cache when token invalidates\n\
    token: ABC cache token (or None)\n\
\n\
Returns:\n\
    A callable DispatchCache instance");

static PyObject * build_dispatch_cache(PyObject *module, PyObject *args)
{
    PyObject *impls, *find, *reset, *token;
    if (!PyArg_ParseTuple(args, "OOOO", &impls, &find, &reset, &token)) {
        return nullptr;
    }

    dispatch_state *state = get_dispatch_state(module);
    DispatchCache *self = PyObject_GC_New(DispatchCache, state->DispatchCacheType);
    if (self == nullptr) {
        return nullptr;
    }

    // Fix 4: Initialize all fields to NULL immediately to prevent dealloc-on-failure crashes
    self->token = nullptr;
    self->dct = nullptr;
    self->impls_by_arg_cls = nullptr;
    self->find_impl = nullptr;
    self->reset_cache_for_token = nullptr;
    self->abc_get_cache_token = nullptr;
    self->dict = nullptr;

    self->token = Py_NewRef(token);
    self->impls_by_arg_cls = Py_NewRef(impls);
    self->find_impl = Py_NewRef(find);
    self->reset_cache_for_token = Py_NewRef(reset);

    if (!(self->dct = PyDict_New())) {
        Py_DECREF(self);
        return nullptr;
    }

    PyObject *abc = PyImport_ImportModule("abc");
    if (!abc) {
        Py_DECREF(self);
        return nullptr;
    }
    self->abc_get_cache_token = PyObject_GetAttrString(abc, "get_cache_token");
    Py_DECREF(abc);
    if (!self->abc_get_cache_token) {
        Py_DECREF(self);
        return nullptr;
    }

    PyObject_GC_Track(self);
    return (PyObject *)self;
}

//

PyDoc_STRVAR(dispatch_doc, "Native C++ implementations for omlish.dispatch");

static int dispatch_exec(PyObject *module)
{
    dispatch_state *state = get_dispatch_state(module);

    // Create the type dynamically
    state->DispatchCacheType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &DispatchCache_spec,
        nullptr
    );
    if (state->DispatchCacheType == nullptr) {
        return -1;
    }

    // Add the type to the module
    if (PyModule_AddType(module, state->DispatchCacheType) < 0) {
        Py_CLEAR(state->DispatchCacheType);
        return -1;
    }

    return 0;
}

static int dispatch_traverse(PyObject *module, visitproc visit, void *arg)
{
    dispatch_state *state = get_dispatch_state(module);
    Py_VISIT(state->DispatchCacheType);
    return 0;
}

static int dispatch_clear(PyObject *module)
{
    dispatch_state *state = get_dispatch_state(module);
    Py_CLEAR(state->DispatchCacheType);
    return 0;
}

static void dispatch_free(void *module)
{
    dispatch_clear((PyObject *)module);
}

static PyMethodDef dispatch_methods[] = {
    {"build_dispatch_cache", (PyCFunction)build_dispatch_cache, METH_VARARGS, build_dispatch_cache_doc},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot dispatch_slots[] = {
    {Py_mod_exec, (void *) dispatch_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, NULL}
};

static struct PyModuleDef dispatch_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = dispatch_doc,
    .m_size = sizeof(dispatch_state),
    .m_methods = dispatch_methods,
    .m_slots = dispatch_slots,
    .m_traverse = dispatch_traverse,
    .m_clear = dispatch_clear,
    .m_free = dispatch_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__dispatch(void)
{
    return PyModuleDef_Init(&dispatch_module);
}

}
