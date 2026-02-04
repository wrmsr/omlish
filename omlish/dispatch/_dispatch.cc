// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"

//

#define _MODULE_NAME "_dispatch"
#define _PACKAGE_NAME "omlish.dispatch"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

typedef struct {
    PyTypeObject *StrongCacheType;
    PyObject *abc_get_cache_token;
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
    PyObject *dct;
    PyObject *token;
    PyObject *impls_by_arg_cls;
    PyObject *find_impl;
    PyObject *reset_cache_for_token;
    PyObject *abc_get_cache_token;
} StrongCache;

static int StrongCache_traverse(StrongCache *self, visitproc visit, void *arg)
{
    Py_VISIT(self->dct);
    Py_VISIT(self->token);
    Py_VISIT(self->impls_by_arg_cls);
    Py_VISIT(self->find_impl);
    Py_VISIT(self->reset_cache_for_token);
    Py_VISIT(self->abc_get_cache_token);
    return 0;
}

static int StrongCache_clear(StrongCache *self)
{
    Py_CLEAR(self->dct);
    Py_CLEAR(self->token);
    Py_CLEAR(self->impls_by_arg_cls);
    Py_CLEAR(self->find_impl);
    Py_CLEAR(self->reset_cache_for_token);
    Py_CLEAR(self->abc_get_cache_token);
    return 0;
}

static void StrongCache_dealloc(StrongCache *self)
{
    PyObject_GC_UnTrack(self);
    StrongCache_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject * StrongCache_dispatch(StrongCache *self, PyObject *cls)
{
    // if token is not None and abc.get_cache_token() != token:
    //     reset_cache_for_token(self)
    //     return find_impl(cls, impls_by_arg_cls)
    if (self->token != Py_None) {
        PyObject *current_token = PyObject_CallNoArgs(self->abc_get_cache_token);
        if (current_token == nullptr) {
            return nullptr;
        }

        int token_changed = PyObject_RichCompareBool(current_token, self->token, Py_NE);
        Py_DECREF(current_token);

        if (token_changed < 0) {
            return nullptr;
        }

        if (token_changed) {
            // Call reset_cache_for_token(self)
            PyObject *reset_result = PyObject_CallOneArg(self->reset_cache_for_token, (PyObject *)self);
            if (reset_result == nullptr) {
                return nullptr;
            }
            Py_DECREF(reset_result);

            // Call find_impl(cls, impls_by_arg_cls)
            PyObject *impl = PyObject_CallFunctionObjArgs(
                self->find_impl,
                cls,
                self->impls_by_arg_cls,
                nullptr
            );
            return impl;
        }
    }

    // try:
    //     return dct[cls]
    // except KeyError:
    //     pass
    PyObject *cached = PyDict_GetItemWithError(self->dct, cls);
    if (cached != nullptr) {
        Py_INCREF(cached);
        return cached;
    }
    if (PyErr_Occurred()) {
        return nullptr;
    }

    // try:
    //     impl = impls_by_arg_cls[cls]
    // except KeyError:
    //     impl = find_impl(cls, impls_by_arg_cls)
    PyObject *impl = PyDict_GetItemWithError(self->impls_by_arg_cls, cls);
    if (impl != nullptr) {
        Py_INCREF(impl);
    } else if (PyErr_Occurred()) {
        return nullptr;
    } else {
        // Call find_impl(cls, impls_by_arg_cls)
        impl = PyObject_CallFunctionObjArgs(
            self->find_impl,
            cls,
            self->impls_by_arg_cls,
            nullptr
        );
        if (impl == nullptr) {
            return nullptr;
        }
    }

    // dct[cls] = impl
    if (PyDict_SetItem(self->dct, cls, impl) < 0) {
        Py_DECREF(impl);
        return nullptr;
    }

    Py_DECREF(impl);
    return impl;
}

static PyObject * StrongCache_get_dct(StrongCache *self, void *closure)
{
    Py_INCREF(self->dct);
    return self->dct;
}

static PyObject * StrongCache_get_token(StrongCache *self, void *closure)
{
    Py_INCREF(self->token);
    return self->token;
}

static PyMethodDef StrongCache_methods[] = {
    {"dispatch", (PyCFunction)StrongCache_dispatch, METH_O, "Dispatch to implementation for given class"},
    {nullptr}
};

static PyGetSetDef StrongCache_getsets[] = {
    {"dct", (getter)StrongCache_get_dct, nullptr, nullptr, nullptr},
    {"token", (getter)StrongCache_get_token, nullptr, nullptr, nullptr},
    {nullptr}
};

static PyType_Slot StrongCache_slots[] = {
    {Py_tp_dealloc, (void *)StrongCache_dealloc},
    {Py_tp_traverse, (void *)StrongCache_traverse},
    {Py_tp_clear, (void *)StrongCache_clear},
    {Py_tp_methods, StrongCache_methods},
    {Py_tp_getset, StrongCache_getsets},
    {Py_tp_doc, (void *)"Fast strong cache for dispatcher"},
    {0, nullptr}
};

static PyType_Spec StrongCache_spec = {
    .name = _MODULE_FULL_NAME ".StrongCache",
    .basicsize = sizeof(StrongCache),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = StrongCache_slots,
};

//

PyDoc_STRVAR(build_strong_dispatch_cache_doc,
"build_strong_dispatch_cache(impls_by_arg_cls, find_impl, reset_cache_for_token, token)\n\
\n\
Create a fast strong cache for dispatcher.\n\
\n\
Args:\n\
    params: Dispatcher._CacheParams object\n\
\n\
Returns:\n\
    A StrongCache instance");

static PyObject * build_strong_dispatch_cache(PyObject *module, PyObject *args)
{
    PyObject *params;

    if (!PyArg_ParseTuple(args, "O", &params)) {
        return nullptr;
    }

    dispatch_state *state = get_dispatch_state(module);
    StrongCache *self = PyObject_GC_New(StrongCache, state->StrongCacheType);
    if (self == nullptr) {
        return nullptr;
    }

    self->dct = nullptr;
    self->token = nullptr;
    self->impls_by_arg_cls = nullptr;
    self->find_impl = nullptr;
    self->reset_cache_for_token = nullptr;
    self->abc_get_cache_token = Py_NewRef(state->abc_get_cache_token);

    self->dct = PyDict_New();
    if (self->dct == nullptr) {
        Py_DECREF(self);
        return nullptr;
    }

    self->impls_by_arg_cls = PyObject_GetAttrString(params, "impls_by_arg_cls");
    if (self->impls_by_arg_cls == nullptr || !PyDict_Check(self->impls_by_arg_cls)) {
        PyErr_SetString(PyExc_TypeError, "impls_by_arg_cls must be a dictionary");
        Py_DECREF(self);
        return nullptr;
    }

    self->find_impl = PyObject_GetAttrString(params, "find_impl");
    if (self->find_impl == nullptr || !PyCallable_Check(self->find_impl)) {
        PyErr_SetString(PyExc_TypeError, "find_impl must be callable");
        Py_DECREF(self);
        return nullptr;
    }

    self->reset_cache_for_token = PyObject_GetAttrString(params, "reset_cache_for_token");
    if (self->reset_cache_for_token == nullptr || !PyCallable_Check(self->reset_cache_for_token)) {
        PyErr_SetString(PyExc_TypeError, "reset_cache_for_token must be callable");
        Py_DECREF(self);
        return nullptr;
    }

    self->token = PyObject_GetAttrString(params, "token");
    if (self->token == nullptr) {
        PyErr_SetString(PyExc_TypeError, "token is required");
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

    // Import abc.get_cache_token
    PyObject *abc_module = PyImport_ImportModule("abc");
    if (abc_module == nullptr) {
        return -1;
    }

    state->abc_get_cache_token = PyObject_GetAttrString(abc_module, "get_cache_token");
    Py_DECREF(abc_module);
    if (state->abc_get_cache_token == nullptr) {
        return -1;
    }

    // Create the type dynamically
    state->StrongCacheType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &StrongCache_spec,
        nullptr
    );
    if (state->StrongCacheType == nullptr) {
        return -1;
    }
    Py_INCREF(state->StrongCacheType);

    // Add the type to the module
    if (PyModule_AddType(module, state->StrongCacheType) < 0) {
        Py_CLEAR(state->StrongCacheType);
        return -1;
    }

    return 0;
}

static int dispatch_traverse(PyObject *module, visitproc visit, void *arg)
{
    dispatch_state *state = get_dispatch_state(module);
    Py_VISIT(state->StrongCacheType);
    Py_VISIT(state->abc_get_cache_token);
    return 0;
}

static int dispatch_clear(PyObject *module)
{
    dispatch_state *state = get_dispatch_state(module);
    Py_CLEAR(state->StrongCacheType);
    Py_CLEAR(state->abc_get_cache_token);
    return 0;
}

static void dispatch_free(void *module)
{
    dispatch_clear((PyObject *)module);
}

static PyMethodDef dispatch_methods[] = {
    {"build_strong_dispatch_cache", (PyCFunction)build_strong_dispatch_cache, METH_VARARGS, build_strong_dispatch_cache_doc},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef_Slot dispatch_slots[] = {
    {Py_mod_exec, (void *) dispatch_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, nullptr}
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
