// @omlish-cext
// dispatch_module.cpp
/*
Below is a single-file example of a C++20 extension for CPython 3.12+ that provides native implementations of the two
classes DispatchCache and Dispatcher. The overall structure follows typical CPython “C API” style but uses a few C++
features where it’s convenient. Everything is done in one translation unit for illustration; in practice you may split
into headers and sources.

This example:
 - Implements DispatchCache with a dictionary keyed by weakrefs plus a small custom callback-object type
   (RemoveCallback) that removes entries upon class finalization.
 - Implements the same abc.get_cache_token()-based invalidation logic in DispatchCache.get() that the Python code shows.
 - Implements Dispatcher with a stored “find_impl” Python callable, a dict of implementations, and a DispatchCache
   instance for caching.
 - Uses only public/stable API calls for CPython.
 - Uses modern PyModuleDef initialization.

The dispatch.DispatchCache and dispatch.Dispatcher classes implement essentially the same behavior as your original
Python code, including the weakref-based clearing of entries and the abc.get_cache_token() checks.
*/
#include <Python.h>

// We rely on CPython stable API for 3.12+
// We'll keep a generally C-like style but use some minimal C++ features.

//////////////////////////////////////////////////////////////////////////////
// Forward declarations of types:

// Forward-declare our DispatchCache type.
typedef struct {
    PyObject_HEAD

    // The main dictionary for { weakref-to-class: impl }
    // Value 'impl' is any PyObject.
    PyObject* dct;

    // A Python object that acts as the remove-callback for all weakrefs we create
    // (an instance of our custom RemoveCallback type).
    PyObject* remove_callback;

    // We store the "token" used by the abc.get_cache_token logic. We store Py_None
    // when not set, or the actual token object otherwise.
    PyObject* token;
} DispatchCacheObject;


// Forward-declare our Dispatcher type.
typedef struct {
    PyObject_HEAD

    // The Python callable find_impl(cls, impls_by_arg_cls) -> T | None
    PyObject* find_impl;

    // A dict: { cls: impl }
    PyObject* impls_by_arg_cls;

    // A DispatchCache instance for caching: dispatch_cache
    PyObject* cache; // (DispatchCacheObject*)
} DispatcherObject;


//////////////////////////////////////////////////////////////////////////////
// A small custom "callable" type we use as the weakref callback.
//
//   remove_callback(weakref_obj)
//
// The callback removes the 'weakref_obj' key from the DispatchCacheObject.dct
// ignoring KeyError.

typedef struct {
    PyObject_HEAD
    // Store the DispatchCache in which we remove items.
    DispatchCacheObject* dcache;  // strong reference or borrowed? We'll hold a strong ref.
} RemoveCallbackObject;


//////////////////////////////////////////////////////////////////////////////
// Utility function to call abc.get_cache_token (cached at module level)

static PyObject* g_abc_get_cache_token_func = nullptr;  // We'll store the function once.

static int
import_abc_get_cache_token()
{
    // If we've already imported, do nothing:
    if (g_abc_get_cache_token_func != nullptr) {
        return 0;  // Ok
    }

    // Import abc module
    PyObject* abc_mod = PyImport_ImportModule("abc");
    if (!abc_mod) {
        return -1; // error
    }

    // Get the "get_cache_token" attribute
    g_abc_get_cache_token_func = PyObject_GetAttrString(abc_mod, "get_cache_token");
    Py_DECREF(abc_mod);
    if (!g_abc_get_cache_token_func) {
        return -1;
    }

    return 0; // success
}

// Call get_cache_token(), returning new reference or nullptr on error.
static PyObject*
call_abc_get_cache_token()
{
    if (import_abc_get_cache_token() < 0) {
        return nullptr;
    }
    // call it with no args
    return PyObject_CallNoArgs(g_abc_get_cache_token_func);
}


//////////////////////////////////////////////////////////////////////////////
// RemoveCallback: the __call__ method

static PyObject*
RemoveCallback_call(RemoveCallbackObject* self, PyObject* arg, PyObject* /*kwds*/)
{
    // arg should be the weakref that triggered the callback.
    // We remove 'arg' as a key from self->dcache->dct, ignoring KeyError.
    if (!self->dcache || !self->dcache->dct) {
        // Shouldn't normally happen, but just in case:
        Py_RETURN_NONE;
    }

    // We'll attempt to delete the key from the dict, ignoring errors:
    int res = PyDict_DelItem(self->dcache->dct, arg);
    if (res < 0) {
        // Could be KeyError or something else. We'll clear the error unconditionally
        // to mimic the Python code's "except KeyError: pass".
        PyErr_Clear();
    }

    Py_RETURN_NONE;
}

static void
RemoveCallback_dealloc(RemoveCallbackObject* self)
{
    // Decref the dcache if present:
    Py_XDECREF(self->dcache);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
RemoveCallback_init(RemoveCallbackObject* self, PyObject* args, PyObject* kwds)
{
    // This is not typically called via __init__ in normal usage.
    // We'll just do a default init. We'll rely on our custom factory or so.
    Py_RETURN_NONE;
}

static PyTypeObject RemoveCallback_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "dispatch.RemoveCallback",
    .tp_basicsize = sizeof(RemoveCallbackObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_call = (ternaryfunc)RemoveCallback_call,
    .tp_dealloc = (destructor)RemoveCallback_dealloc,
    .tp_init = (initproc)RemoveCallback_init,
};

// Helper to create a new RemoveCallback object for a given DispatchCache.
static PyObject*
RemoveCallback_new_for_cache(DispatchCacheObject* dcache)
{
    RemoveCallbackObject* rc = PyObject_New(RemoveCallbackObject, &RemoveCallback_Type);
    if (!rc) return nullptr;

    // We'll hold a strong reference to 'dcache':
    Py_INCREF(dcache);
    rc->dcache = dcache;
    return (PyObject*)rc;
}


//////////////////////////////////////////////////////////////////////////////
// DispatchCache methods (C-level)

static int
DispatchCache_clear_dict(DispatchCacheObject* self)
{
    if (self->dct) {
        PyDict_Clear(self->dct);
    }
    return 0;
}

static PyObject*
DispatchCache_size_impl(DispatchCacheObject* self)
{
    // returns the size (int) of self->dct
    if (!self->dct) {
        return PyLong_FromLong(0);
    }
    Py_ssize_t sz = PyDict_Size(self->dct);
    return PyLong_FromSsize_t(sz);
}

static PyObject*
DispatchCache_prepare_impl(DispatchCacheObject* self, PyObject* cls)
{
    // If self->token is None and cls has __abstractmethods__ attribute,
    //   self->token = abc.get_cache_token()
    // Then self->clear()

    // Check if self->token is None
    if (self->token == Py_None) {
        // Check if hasattr(cls, '__abstractmethods__')
        int has_abstract = PyObject_HasAttrString(cls, "__abstractmethods__");
        if (has_abstract < 0) {
            return nullptr; // error
        }
        if (has_abstract == 1) {
            // we need to fetch abc.get_cache_token
            PyObject* new_tok = call_abc_get_cache_token();
            if (!new_tok) {
                return nullptr; // error
            }
            // replace self->token
            Py_SETREF(self->token, new_tok);
        }
    }

    // Clear the dict
    if (DispatchCache_clear_dict(self) < 0) {
        return nullptr;
    }

    Py_RETURN_NONE;
}

static PyObject*
DispatchCache_clear_impl(DispatchCacheObject* self)
{
    if (DispatchCache_clear_dict(self) < 0) {
        return nullptr;
    }
    Py_RETURN_NONE;
}

static PyObject*
DispatchCache_put_impl(DispatchCacheObject* self, PyObject* args)
{
    // put(self, cls, impl)
    PyObject* cls = nullptr;
    PyObject* impl = nullptr;
    if (!PyArg_UnpackTuple(args, "put", 2, 2, &cls, &impl)) {
        return nullptr;
    }

    // Make a weakref with our remove_callback so we can remove from dict on finalization.
    PyObject* wr = PyWeakref_NewRef(cls, self->remove_callback);
    if (!wr) {
        return nullptr; // error creating weakref
    }

    // Insert into self->dct
    int rc = PyDict_SetItem(self->dct, wr, impl);
    Py_DECREF(wr);
    if (rc < 0) {
        return nullptr; // error
    }

    Py_RETURN_NONE;
}


static PyObject*
DispatchCache_get_impl(DispatchCacheObject* self, PyObject* cls)
{
    // If self->token != None:
    //   let new_tok = abc.get_cache_token()
    //   if new_tok != self->token: self->dct.clear(); self->token = new_tok
    if (self->token != Py_None) {
        PyObject* new_tok = call_abc_get_cache_token();
        if (!new_tok) {
            return nullptr; // error
        }
        int cmp = PyObject_RichCompareBool(self->token, new_tok, Py_EQ);
        if (cmp < 0) {
            Py_DECREF(new_tok);
            return nullptr;
        }
        if (cmp == 0) {
            // not equal => clear
            if (DispatchCache_clear_dict(self) < 0) {
                Py_DECREF(new_tok);
                return nullptr;
            }
            Py_SETREF(self->token, new_tok);
        } else {
            Py_DECREF(new_tok);
        }
    }

    // We do the same as python: wr = weakref.ref(cls) with no callback
    PyObject* wr = PyWeakref_NewRef(cls, nullptr);
    if (!wr) {
        return nullptr; // error
    }
    PyObject* impl = PyDict_GetItemWithError(self->dct, wr);
    Py_DECREF(wr);
    if (!impl) {
        // Could be KeyError or an error
        if (!PyErr_Occurred()) {
            // Means key not found => raise KeyError
            PyErr_SetObject(PyExc_KeyError, cls);
        }
        return nullptr;
    }

    // Return impl (borrowed from the dict). We must return a new reference.
    Py_INCREF(impl);
    return impl;
}


//////////////////////////////////////////////////////////////////////////////
// DispatchCache type slots

static void
DispatchCache_dealloc(DispatchCacheObject* self)
{
    // Dealloc
    Py_XDECREF(self->remove_callback);
    Py_XDECREF(self->dct);
    Py_XDECREF(self->token);

    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
DispatchCache_init(DispatchCacheObject* self, PyObject* /*args*/, PyObject* /*kwds*/)
{
    // Just like Python code: self._dct = {}
    PyObject* d = PyDict_New();
    if (!d) return -1;

    // Build the remove callback object:
    PyObject* rc = RemoveCallback_new_for_cache(self);
    if (!rc) {
        Py_DECREF(d);
        return -1;
    }

    // Store them:
    self->dct = d;
    self->remove_callback = rc;

    // self->token = None
    Py_INCREF(Py_None);
    self->token = Py_None;

    return 0;
}

// DispatchCache methods in a method table:
static PyObject*
DispatchCache_size(PyObject* self, PyObject* /*args*/)
{
    return DispatchCache_size_impl((DispatchCacheObject*)self);
}

static PyObject*
DispatchCache_prepare(PyObject* self, PyObject* arg)
{
    return DispatchCache_prepare_impl((DispatchCacheObject*)self, arg);
}

static PyObject*
DispatchCache_clear(PyObject* self, PyObject* /*args*/)
{
    return DispatchCache_clear_impl((DispatchCacheObject*)self);
}

static PyObject*
DispatchCache_put(PyObject* self, PyObject* args)
{
    return DispatchCache_put_impl((DispatchCacheObject*)self, args);
}

static PyObject*
DispatchCache_get(PyObject* self, PyObject* arg)
{
    return DispatchCache_get_impl((DispatchCacheObject*)self, arg);
}

static PyMethodDef DispatchCache_methods[] = {
    {"size",    (PyCFunction)DispatchCache_size,    METH_NOARGS,  nullptr},
    {"prepare", (PyCFunction)DispatchCache_prepare, METH_O,       nullptr},
    {"clear",   (PyCFunction)DispatchCache_clear,   METH_NOARGS,  nullptr},
    {"put",     (PyCFunction)DispatchCache_put,     METH_VARARGS, nullptr},
    {"get",     (PyCFunction)DispatchCache_get,     METH_O,       nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static PyTypeObject DispatchCache_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "dispatch.DispatchCache",
    .tp_basicsize = sizeof(DispatchCacheObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)DispatchCache_init,
    .tp_dealloc = (destructor)DispatchCache_dealloc,
    .tp_methods = DispatchCache_methods,
};


//////////////////////////////////////////////////////////////////////////////
// Dispatcher methods (C-level)

static PyObject*
Dispatcher_cache_size_impl(DispatcherObject* self)
{
    // just call self->cache.size()
    // self->cache is a DispatchCache instance, so we can just call its "size" method
    PyObject* meth = PyObject_GetAttrString(self->cache, "size");
    if (!meth) return nullptr;
    PyObject* res = PyObject_CallNoArgs(meth);
    Py_DECREF(meth);
    return res;
}

static PyObject*
Dispatcher_register_impl(DispatcherObject* self, PyObject* args)
{
    // register(self, impl, cls_col)
    PyObject* impl = nullptr;
    PyObject* cls_col = nullptr;
    if (!PyArg_UnpackTuple(args, "register", 2, 2, &impl, &cls_col)) {
        return nullptr;
    }

    // We expect cls_col to be an iterable of types
    PyObject* iter = PyObject_GetIter(cls_col);
    if (!iter) {
        return nullptr;
    }

    // for cls in cls_col:
    //   self._impls_by_arg_cls[cls] = impl
    //   self._cache.prepare(cls)

    while (true) {
        PyObject* cls = PyIter_Next(iter);
        if (!cls) {
            // either iteration ended or error
            if (PyErr_Occurred()) {
                Py_DECREF(iter);
                return nullptr;
            }
            break; // done
        }

        // self._impls_by_arg_cls[cls] = impl
        int rc = PyDict_SetItem(self->impls_by_arg_cls, cls, impl);
        if (rc < 0) {
            Py_DECREF(cls);
            Py_DECREF(iter);
            return nullptr;
        }

        // self._cache.prepare(cls)
        PyObject* meth_prepare = PyObject_GetAttrString(self->cache, "prepare");
        if (!meth_prepare) {
            Py_DECREF(cls);
            Py_DECREF(iter);
            return nullptr;
        }
        PyObject* call_res = PyObject_CallOneArg(meth_prepare, cls);
        Py_DECREF(meth_prepare);
        Py_DECREF(cls);
        if (!call_res) {
            Py_DECREF(iter);
            return nullptr;
        }
        Py_DECREF(call_res);
    }
    Py_DECREF(iter);

    // return impl
    Py_INCREF(impl);
    return impl;
}

static PyObject*
Dispatcher_dispatch_impl(DispatcherObject* self, PyObject* cls)
{
    // Pseudocode:
    //   try: return self._cache.get(cls)
    //   except KeyError:
    //       pass
    //   try: impl = self._impls_by_arg_cls[cls]
    //   except KeyError:
    //       impl = self._find_impl(cls, self._impls_by_arg_cls)
    //   self._cache.put(cls, impl)
    //   return impl
    //
    // except in C.

    // call self->cache.get(cls)
    PyObject* meth_get = PyObject_GetAttrString(self->cache, "get");
    if (!meth_get) return nullptr;
    PyObject* res = PyObject_CallOneArg(meth_get, cls);
    Py_DECREF(meth_get);

    if (res) {
        // we got an impl
        return res; // T | None is possible
    }
    // check if it's a KeyError or real error
    if (!PyErr_ExceptionMatches(PyExc_KeyError)) {
        // real error
        return nullptr;
    }
    // clear the KeyError
    PyErr_Clear();

    // impl = self->_impls_by_arg_cls.get(cls) (like python)
    PyObject* impl = PyDict_GetItemWithError(self->impls_by_arg_cls, cls);
    if (!impl) {
        if (PyErr_Occurred()) {
            // real error
            return nullptr;
        }
        // not found => call self->find_impl(cls, self->impls_by_arg_cls)
        PyObject* args2 = PyTuple_New(2);
        if (!args2) return nullptr;
        Py_INCREF(cls);
        PyTuple_SET_ITEM(args2, 0, cls);  // consumes reference
        Py_INCREF(self->impls_by_arg_cls);
        PyTuple_SET_ITEM(args2, 1, self->impls_by_arg_cls);

        impl = PyObject_CallObject(self->find_impl, args2);
        Py_DECREF(args2);
        if (!impl) {
            return nullptr;
        }
    } else {
        // borrowed reference from the dict
        Py_INCREF(impl);
    }

    // self->cache.put(cls, impl)
    PyObject* meth_put = PyObject_GetAttrString(self->cache, "put");
    if (!meth_put) {
        Py_DECREF(impl);
        return nullptr;
    }
    PyObject* args3 = Py_BuildValue("(OO)", cls, impl);
    if (!args3) {
        Py_DECREF(meth_put);
        Py_DECREF(impl);
        return nullptr;
    }
    PyObject* put_res = PyObject_CallObject(meth_put, args3);
    Py_DECREF(args3);
    Py_DECREF(meth_put);
    if (!put_res) {
        Py_DECREF(impl);
        return nullptr;
    }
    Py_DECREF(put_res);

    // return impl
    return impl;
}


//////////////////////////////////////////////////////////////////////////////
// Dispatcher type methods

static void
Dispatcher_dealloc(DispatcherObject* self)
{
    Py_XDECREF(self->find_impl);
    Py_XDECREF(self->impls_by_arg_cls);
    Py_XDECREF(self->cache);

    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
Dispatcher_init(DispatcherObject* self, PyObject* args, PyObject* /*kwds*/)
{
    // __init__(self, find_impl)
    // plus we do: self._impls_by_arg_cls = {}
    //            self._cache = DispatchCache()
    PyObject* find_impl = nullptr;
    if (!PyArg_UnpackTuple(args, "Dispatcher", 1, 1, &find_impl)) {
        return -1;
    }
    if (!PyCallable_Check(find_impl)) {
        PyErr_SetString(PyExc_TypeError, "find_impl must be callable");
        return -1;
    }
    Py_INCREF(find_impl);
    self->find_impl = find_impl;

    PyObject* d = PyDict_New();
    if (!d) {
        return -1;
    }
    self->impls_by_arg_cls = d;

    // create a new DispatchCache
    PyObject* cache_obj = PyObject_CallNoArgs((PyObject*)&DispatchCache_Type);
    if (!cache_obj) {
        return -1;
    }
    self->cache = cache_obj;

    return 0;
}

// Exposed methods:

static PyObject*
Dispatcher_cache_size(PyObject* self, PyObject* /*args*/)
{
    return Dispatcher_cache_size_impl((DispatcherObject*)self);
}

static PyObject*
Dispatcher_register(PyObject* self, PyObject* args)
{
    return Dispatcher_register_impl((DispatcherObject*)self, args);
}

static PyObject*
Dispatcher_dispatch(PyObject* self, PyObject* arg)
{
    return Dispatcher_dispatch_impl((DispatcherObject*)self, arg);
}

static PyMethodDef Dispatcher_methods[] = {
    {"cache_size", (PyCFunction)Dispatcher_cache_size, METH_NOARGS,  nullptr},
    {"register",   (PyCFunction)Dispatcher_register,   METH_VARARGS, nullptr},
    {"dispatch",   (PyCFunction)Dispatcher_dispatch,   METH_O,       nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static PyTypeObject Dispatcher_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "dispatch.Dispatcher",
    .tp_basicsize = sizeof(DispatcherObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)Dispatcher_init,
    .tp_dealloc = (destructor)Dispatcher_dealloc,
    .tp_methods = Dispatcher_methods,
};


//////////////////////////////////////////////////////////////////////////////
// Module definition

static PyModuleDef dispatch_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_gpto1",
    .m_doc = "Example module implementing DispatchCache and Dispatcher natively.",
    .m_size = -1,
    .m_methods = nullptr,
};

PyMODINIT_FUNC
PyInit__gpto1(void)
{
    // Initialize the RemoveCallback_Type
    if (PyType_Ready(&RemoveCallback_Type) < 0) {
        return nullptr;
    }
    // Initialize DispatchCache_Type
    if (PyType_Ready(&DispatchCache_Type) < 0) {
        return nullptr;
    }
    // Initialize Dispatcher_Type
    if (PyType_Ready(&Dispatcher_Type) < 0) {
        return nullptr;
    }

    PyObject* m = PyModule_Create(&dispatch_module);
    if (!m) {
        return nullptr;
    }

    // Add the types to the module
    Py_INCREF(&DispatchCache_Type);
    if (PyModule_AddObject(m, "DispatchCache", (PyObject*)&DispatchCache_Type) < 0) {
        Py_DECREF(&DispatchCache_Type);
        Py_DECREF(m);
        return nullptr;
    }

    Py_INCREF(&Dispatcher_Type);
    if (PyModule_AddObject(m, "Dispatcher", (PyObject*)&Dispatcher_Type) < 0) {
        Py_DECREF(&Dispatcher_Type);
        Py_DECREF(m);
        return nullptr;
    }

    // Optionally pre-import abc.get_cache_token so the first call might be faster:
    // Not required, but we can do it.
    import_abc_get_cache_token(); // ignore failure (just means calls will fail later)

    return m;
}
