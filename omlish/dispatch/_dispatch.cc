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
    PyObject *weakref_ref;
    PyObject *dict;
} DispatchCache;

static int DispatchCache_traverse(DispatchCache *self, visitproc visit, void *arg)
{
    Py_VISIT(self->token);
    Py_VISIT(self->dct);
    Py_VISIT(self->impls_by_arg_cls);
    Py_VISIT(self->find_impl);
    Py_VISIT(self->reset_cache_for_token);
    Py_VISIT(self->abc_get_cache_token);
    Py_VISIT(self->weakref_ref);
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
    Py_CLEAR(self->weakref_ref);
    Py_CLEAR(self->dict);
    return 0;
}

static void DispatchCache_dealloc(DispatchCache *self)
{
    PyObject_GC_UnTrack(self);
    DispatchCache_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

// Callback function for weakref cleanup
// Called as: dct_remove(dct, cls_weakref) due to functools.partial binding order
static PyObject * dct_remove_callback(PyObject *self, PyObject *args)
{
    PyObject *dct;
    PyObject *cls_weakref;

    if (!PyArg_ParseTuple(args, "OO", &dct, &cls_weakref)) {
        return nullptr;
    }

    // Remove the entry from dct
    if (PyDict_DelItem(dct, cls_weakref) < 0) {
        // KeyError is expected if already removed
        if (PyErr_ExceptionMatches(PyExc_KeyError)) {
            PyErr_Clear();
        }
    }

    Py_RETURN_NONE;
}

static PyMethodDef dct_remove_method_def = {
    "dct_remove",
    (PyCFunction)dct_remove_callback,
    METH_VARARGS,
    "Cleanup callback for weakref"
};

// Helper to create a weakref with cleanup callback
static PyObject * create_weakref_with_callback(DispatchCache *self, PyObject *cls)
{
    // Create callback using functools.partial(dct_remove, dct=self.dct)
    PyObject *functools = PyImport_ImportModule("functools");
    if (functools == nullptr) {
        return nullptr;
    }

    PyObject *partial = PyObject_GetAttrString(functools, "partial");
    Py_DECREF(functools);
    if (partial == nullptr) {
        return nullptr;
    }

    // Create the C function object
    PyObject *dct_remove_func = PyCFunction_New(&dct_remove_method_def, nullptr);
    if (dct_remove_func == nullptr) {
        Py_DECREF(partial);
        return nullptr;
    }

    // Create partial(dct_remove, self.dct)
    // The callback signature will be: callback(cls_weakref)
    // Which calls: dct_remove(self.dct, cls_weakref)
    PyObject *partial_args = PyTuple_Pack(2, dct_remove_func, self->dct);
    Py_DECREF(dct_remove_func);
    if (partial_args == nullptr) {
        Py_DECREF(partial);
        return nullptr;
    }

    PyObject *callback = PyObject_Call(partial, partial_args, nullptr);
    Py_DECREF(partial_args);
    Py_DECREF(partial);
    if (callback == nullptr) {
        return nullptr;
    }

    // Create weakref.ref(cls, callback)
    PyObject *weakref_args = PyTuple_Pack(2, cls, callback);
    Py_DECREF(callback);
    if (weakref_args == nullptr) {
        return nullptr;
    }

    PyObject *cls_ref = PyObject_Call(self->weakref_ref, weakref_args, nullptr);
    Py_DECREF(weakref_args);
    return cls_ref;
}

static PyObject * DispatchCache_call(DispatchCache *self, PyObject *args, PyObject *kwargs)
{
    // Expect single argument: cls (type)
    PyObject *cls;
    if (!PyArg_ParseTuple(args, "O", &cls)) {
        return nullptr;
    }

    // Check ABC token if present
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
            // Token changed, reset cache
            PyObject *result = PyObject_CallOneArg(self->reset_cache_for_token, (PyObject *)self);
            if (result == nullptr) {
                return nullptr;
            }
            Py_DECREF(result);

            // Call find_impl directly
            PyObject *find_args = PyTuple_Pack(2, cls, self->impls_by_arg_cls);
            if (find_args == nullptr) {
                return nullptr;
            }
            result = PyObject_Call(self->find_impl, find_args, nullptr);
            Py_DECREF(find_args);
            return result;
        }
    }

    // Try weakref cache lookup (temporary weakref, no callback)
    PyObject *cls_ref = PyObject_CallOneArg(self->weakref_ref, cls);
    if (cls_ref == nullptr) {
        return nullptr;
    }

    PyObject *impl = PyDict_GetItem(self->dct, cls_ref);
    if (impl != nullptr) {
        Py_DECREF(cls_ref);
        Py_INCREF(impl);
        return impl;
    }
    Py_DECREF(cls_ref);

    // Clear any error from PyDict_GetItem
    if (PyErr_Occurred()) {
        return nullptr;
    }

    // Try direct lookup in impls_by_arg_cls
    impl = PyDict_GetItem(self->impls_by_arg_cls, cls);
    if (impl != nullptr) {
        Py_INCREF(impl);

        // Create weakref with callback and store in dct
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

    // Clear any error from PyDict_GetItem
    if (PyErr_Occurred()) {
        return nullptr;
    }

    // Call find_impl
    PyObject *find_args = PyTuple_Pack(2, cls, self->impls_by_arg_cls);
    if (find_args == nullptr) {
        return nullptr;
    }
    impl = PyObject_Call(self->find_impl, find_args, nullptr);
    Py_DECREF(find_args);

    if (impl == nullptr) {
        return nullptr;
    }

    // Store in cache with weakref
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

static PyObject * DispatchCache_get_dict(DispatchCache *self, void *closure)
{
    if (self->dict == nullptr) {
        self->dict = PyDict_New();
        if (self->dict == nullptr) {
            return nullptr;
        }
    }
    Py_INCREF(self->dict);
    return self->dict;
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
    // First check instance dict
    if (self->dict != nullptr) {
        PyObject *res = PyDict_GetItemWithError(self->dict, name);
        if (res != nullptr) {
            Py_INCREF(res);
            return res;
        }
        if (PyErr_Occurred()) {
            return nullptr;
        }
    }

    // Fall back to type's getattro
    return PyObject_GenericGetAttr((PyObject *)self, name);
}

static int DispatchCache_setattro(DispatchCache *self, PyObject *name, PyObject *value)
{
    // Ensure dict exists
    if (self->dict == nullptr) {
        self->dict = PyDict_New();
        if (self->dict == nullptr) {
            return -1;
        }
    }

    // Set in instance dict
    if (value == nullptr) {
        return PyDict_DelItem(self->dict, name);
    } else {
        return PyDict_SetItem(self->dict, name, value);
    }
}

static PyObject * DispatchCache_get_dispatch(DispatchCache *self, void *closure)
{
    // Return self since the object is callable
    Py_INCREF(self);
    return (PyObject *)self;
}

static PyObject * DispatchCache_get_token(DispatchCache *self, void *closure)
{
    Py_INCREF(self->token);
    return self->token;
}

static PyObject * DispatchCache_get_dct(DispatchCache *self, void *closure)
{
    Py_INCREF(self->dct);
    return self->dct;
}

static PyMemberDef DispatchCache_members[] = {
    {nullptr}
};

static PyGetSetDef DispatchCache_getsets[] = {
    {"__dict__", (getter)DispatchCache_get_dict, (setter)DispatchCache_set_dict, nullptr, nullptr},
    {"dispatch", (getter)DispatchCache_get_dispatch, nullptr, "Dispatch callable", nullptr},
    {"token", (getter)DispatchCache_get_token, nullptr, "ABC cache token", nullptr},
    {"dct", (getter)DispatchCache_get_dct, nullptr, "Weakref dict cache", nullptr},
    {nullptr}
};

static PyType_Slot DispatchCache_slots[] = {
    {Py_tp_dealloc, (void *)DispatchCache_dealloc},
    {Py_tp_call, (void *)DispatchCache_call},
    {Py_tp_traverse, (void *)DispatchCache_traverse},
    {Py_tp_clear, (void *)DispatchCache_clear},
    {Py_tp_getattro, (void *)DispatchCache_getattro},
    {Py_tp_setattro, (void *)DispatchCache_setattro},
    {Py_tp_members, DispatchCache_members},
    {Py_tp_getset, DispatchCache_getsets},
    {Py_tp_doc, (void *)"Fast dispatch cache for Dispatcher"},
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
    PyObject *impls_by_arg_cls;
    PyObject *find_impl;
    PyObject *reset_cache_for_token;
    PyObject *token;

    if (!PyArg_ParseTuple(args, "OOOO", &impls_by_arg_cls, &find_impl, &reset_cache_for_token, &token)) {
        return nullptr;
    }

    if (!PyDict_Check(impls_by_arg_cls)) {
        PyErr_SetString(PyExc_TypeError, "impls_by_arg_cls must be a dict");
        return nullptr;
    }

    if (!PyCallable_Check(find_impl)) {
        PyErr_SetString(PyExc_TypeError, "find_impl must be callable");
        return nullptr;
    }

    if (!PyCallable_Check(reset_cache_for_token)) {
        PyErr_SetString(PyExc_TypeError, "reset_cache_for_token must be callable");
        return nullptr;
    }

    dispatch_state *state = get_dispatch_state(module);
    DispatchCache *self = PyObject_GC_New(DispatchCache, state->DispatchCacheType);
    if (self == nullptr) {
        return nullptr;
    }

    self->token = Py_NewRef(token);
    self->dct = PyDict_New();
    if (self->dct == nullptr) {
        Py_DECREF(self);
        return nullptr;
    }
    self->impls_by_arg_cls = Py_NewRef(impls_by_arg_cls);
    self->find_impl = Py_NewRef(find_impl);
    self->reset_cache_for_token = Py_NewRef(reset_cache_for_token);

    // Cache abc.get_cache_token
    PyObject *abc_module = PyImport_ImportModule("abc");
    if (abc_module == nullptr) {
        Py_DECREF(self);
        return nullptr;
    }
    self->abc_get_cache_token = PyObject_GetAttrString(abc_module, "get_cache_token");
    Py_DECREF(abc_module);
    if (self->abc_get_cache_token == nullptr) {
        Py_DECREF(self);
        return nullptr;
    }

    // Cache weakref.ref
    PyObject *weakref_module = PyImport_ImportModule("weakref");
    if (weakref_module == nullptr) {
        Py_DECREF(self);
        return nullptr;
    }
    self->weakref_ref = PyObject_GetAttrString(weakref_module, "ref");
    Py_DECREF(weakref_module);
    if (self->weakref_ref == nullptr) {
        Py_DECREF(self);
        return nullptr;
    }

    // Initialize remaining fields
    self->dict = nullptr;

    // Track object for GC
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
