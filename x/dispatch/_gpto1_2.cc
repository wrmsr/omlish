// @omlish-cext
/*
Below is a single-file C++-based CPython 3.12+ extension that implements the same functionality as your Python
Dispatcher class, using a native PyDict for storage and carefully handling weak references. It adheres as closely as
possible to your Python logic (including the inlined weakref.WeakKeyDictionary-style caching), while using only the
public CPython C API and preserving a C-like style in most places.

Note: This code is somewhat long because of the need to create a custom callable object to serve as the weakref
callback, itself holding a (weak) reference back to the Dispatcher instance. This ensures that when the referent dies,
we can remove its entry from the dispatch cache, but if the Dispatcher is also dead, we do nothing.

The translation is done to keep it as “fast” and “native” as possible, and to avoid any dynamic lookups of weakref.ref
or abc.get_cache_token() at runtime beyond what’s necessary. You can of course tailor the code further for your exact
needs.

Highlights
 - Weakref Callback: We define a separate Python object type (DispatcherCacheRemove) whose tp_call slot removes the
   dying key from the Dispatcher’s dispatch_cache. This exactly matches your Python-level closure mechanism
   (cache_remove), while remaining in C.
 - ABC Cache Token: We store the result of abc.get_cache_token() in a long field on the Dispatcher whenever we first see
   a class with __abstractmethods__. On each dispatch, we compare the current token; if it has changed, we clear the
   cache.
 - GC Support: We implement tp_traverse and tp_clear carefully for both Dispatcher and DispatcherCacheRemove, as
   required when objects can contain references that might form reference cycles.
 - Module Layout: We use the modern PyModuleDef style with a PyInit_dispatcher entry point. It exports a single
   Dispatcher type (plus the internal callback type, which is not added to the module’s dictionary).
*/
#define PY_SSIZE_T_CLEAN

#include <Python.h>

#define MODULE_NAME "_gpto1_2"


// We need to call abc.get_cache_token(), so we’ll store a reference to that function globally upon module init.
static PyObject* g_abc_get_cache_token = nullptr;

// Forward-declare the Dispatcher type.
typedef struct {
    PyObject_HEAD

    PyObject *weakreflist;  // Field for weak references

    // The Python-level callables/objects we keep:
    //   find_impl: a Python callable
    //   impls_by_arg_cls: a dict
    //   dispatch_cache: a dict
    //   cache_remove_callable: a custom callable used as the weakref callback
    PyObject* find_impl;
    PyObject* impls_by_arg_cls;
    PyObject* dispatch_cache;

    // We'll store the ABC cache token as a 'long'. If it's 0, that means "None".
    long cache_token;

    // Our custom callback object that has a weakref to self, used for removing items from dispatch_cache when the key's
    // referent is dying.
    PyObject* cache_remove_callable;
} DispatcherObject;

// We define a small object type "DispatcherCacheRemove" which is a callable that holds a *weakref* to its associated
// Dispatcher.  This object is passed as the "callback" parameter to PyWeakref_NewRef(...).  When the referent (the
// class) is about to be finalized, CPython calls this object with the single argument "weakref".  We then look up the
// associated Dispatcher, and if it’s still alive, remove the key from its dispatch_cache.

// Forward-declare the type for the callback object.
typedef struct {
    PyObject_HEAD

    // A weak reference to the DispatcherObject that owns this.
    PyObject* dispatcher_ref;
} DispatcherCacheRemoveObject;

// The "call" method for our DispatcherCacheRemove object.
//
//  Signature:   callback(weakref)
//  - self is the callback object (DispatcherCacheRemoveObject).
//  - args is the single argument tuple (or single object if METH_O, etc.).
static PyObject*
dispatcher_cache_remove_call(PyObject* callable_obj, PyObject* arg)
{
    // 'callable_obj' is a DispatcherCacheRemoveObject* under the hood:
    DispatcherCacheRemoveObject* cobj = (DispatcherCacheRemoveObject*)callable_obj;

    // Get the actual 'Dispatcher' from its stored weakref:
    PyObject* disp_obj = PyWeakref_GetObject(cobj->dispatcher_ref);
    // If disp_obj == None, that means the dispatcher is dead.
    if (disp_obj == Py_None) {
        Py_RETURN_NONE;
    }

    // Otherwise, cast it to a DispatcherObject:
    DispatcherObject* disp = (DispatcherObject*)disp_obj;

    // Now we want to do:
    //    del self->_dispatch_cache[weakref]
    // ignoring any KeyError.
    // 'arg' is the weakref object that’s calling us back.
    if (PyDict_DelItem(disp->dispatch_cache, arg) < 0) {
        // If it’s a KeyError or anything else, clear that error:
        PyErr_Clear();
    }

    Py_RETURN_NONE;
}

// The 'tp_call' slot for our callback type, hooking to dispatcher_cache_remove_call.
static PyObject*
DispatcherCacheRemove_call(PyObject* self, PyObject* args, PyObject* kwds)
{
    // We expect exactly 1 positional argument (the weakref).
    if (!PyArg_UnpackTuple(args, "weakref_callback", 1, 1, &args)) {
        // If that fails, it sets an exception automatically.
        return nullptr;
    }
    // 'args' is now the single argument.  We pass 'self' and 'args' to our function:
    return dispatcher_cache_remove_call(self, args);
}

// Deallocation for the callback object.
static void
DispatcherCacheRemove_dealloc(PyObject* self)
{
    DispatcherCacheRemoveObject* cobj = (DispatcherCacheRemoveObject*)self;
    Py_XDECREF(cobj->dispatcher_ref);
    Py_TYPE(self)->tp_free(self);
}

// GC support: traverse and clear.
static int
DispatcherCacheRemove_traverse(PyObject* self, visitproc visit, void* arg)
{
    DispatcherCacheRemoveObject* cobj = (DispatcherCacheRemoveObject*)self;
    Py_VISIT(cobj->dispatcher_ref);
    return 0;
}

static int
DispatcherCacheRemove_clear(PyObject* self)
{
    DispatcherCacheRemoveObject* cobj = (DispatcherCacheRemoveObject*)self;
    Py_CLEAR(cobj->dispatcher_ref);
    return 0;
}

// Our callback object type definition.
static PyTypeObject DispatcherCacheRemove_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = MODULE_NAME ".DispatcherCacheRemove",
    .tp_basicsize = sizeof(DispatcherCacheRemoveObject),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .tp_call = DispatcherCacheRemove_call,
    .tp_dealloc = DispatcherCacheRemove_dealloc,
    .tp_traverse = DispatcherCacheRemove_traverse,
    .tp_clear = DispatcherCacheRemove_clear,
};

//  Now we define the core Dispatcher object and its methods:
//  - __init__
//  - cache_size
//  - register
//  - dispatch

// Constructor (equivalent to __init__). Signature: __init__(self, find_impl).
static int
Dispatcher_init(PyObject* self, PyObject* args, PyObject* kwds)
{
    // We expect exactly 1 positional argument: find_impl.
    // The Python signature: def __init__(self, find_impl: Callable[[type, Mapping[type, T]], T|None]) -> None:
    PyObject* find_impl = nullptr;

    static const char* kwlist[] = {"find_impl", nullptr};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", (char**)kwlist, &find_impl)) {
        return -1;
    }

    // Store it in our struct:
    DispatcherObject* disp = (DispatcherObject*)self;

    // Clear old references if any (in case re-init is called).
    Py_XDECREF(disp->find_impl);
    Py_XDECREF(disp->impls_by_arg_cls);
    Py_XDECREF(disp->dispatch_cache);
    Py_XDECREF(disp->cache_remove_callable);

    disp->find_impl = nullptr;
    disp->impls_by_arg_cls = nullptr;
    disp->dispatch_cache = nullptr;
    disp->cache_remove_callable = nullptr;
    disp->cache_token = 0; // "None"

    // Keep a strong reference to find_impl:
    Py_INCREF(find_impl);
    disp->find_impl = find_impl;

    // Create the two dicts:
    PyObject* impls_dict = nullptr;
    PyObject* cache_dict = nullptr;

    impls_dict = PyDict_New();
    if (!impls_dict) {
        goto fail;
    }
    disp->impls_by_arg_cls = impls_dict;

    cache_dict = PyDict_New();
    if (!cache_dict) {
        goto fail;
    }
    disp->dispatch_cache = cache_dict;

    // Create our custom callback object (DispatcherCacheRemove) to pass to PyWeakref_NewRef.
    {
        PyObject* cb_obj = DispatcherCacheRemove_Type.tp_alloc(&DispatcherCacheRemove_Type, 0);
        if (!cb_obj) {
            goto fail;
        }
        DispatcherCacheRemoveObject* cobj = (DispatcherCacheRemoveObject*)cb_obj;

        // cobj->dispatcher_ref = weakref.ref(self) so that we do not keep self alive.
        PyObject* disp_weak = PyWeakref_NewRef(self, nullptr);
        if (!disp_weak) {
            Py_DECREF(cb_obj);
            goto fail;
        }
        cobj->dispatcher_ref = disp_weak;

        disp->cache_remove_callable = cb_obj;
    }

    return 0;

fail:
    // We only get here on error, so free everything properly:
    Py_XDECREF(cache_dict);
    Py_XDECREF(impls_dict);
    Py_XDECREF(disp->find_impl); disp->find_impl = nullptr;
    Py_XDECREF(disp->impls_by_arg_cls); disp->impls_by_arg_cls = nullptr;
    Py_XDECREF(disp->dispatch_cache); disp->dispatch_cache = nullptr;
    Py_XDECREF(disp->cache_remove_callable); disp->cache_remove_callable = nullptr;
    return -1;
}

//  def cache_size(self) -> int:
//      return len(self._dispatch_cache)
static PyObject*
Dispatcher_cache_size(PyObject* self, PyObject* Py_UNUSED(ignored))
{
    DispatcherObject* disp = (DispatcherObject*)self;
    Py_ssize_t sz = PyDict_Size(disp->dispatch_cache);
    return PyLong_FromSsize_t(sz);
}

// def register(self, impl: T, cls_col: Iterable[type]) -> T:
//     for cls in cls_col:
//         self._impls_by_arg_cls[cls] = impl
//         if self._cache_token is None and hasattr(cls, '__abstractmethods__'):
//             self._cache_token = abc.get_cache_token()
//     self._dispatch_cache.clear()
//     return impl
static PyObject*
Dispatcher_register(PyObject* self, PyObject* args)
{
    DispatcherObject* disp = (DispatcherObject*)self;
    PyObject* impl = nullptr;
    PyObject* cls_col = nullptr;

    if (!PyArg_ParseTuple(args, "OO", &impl, &cls_col)) {
        return nullptr;
    }

    // We'll iterate over cls_col:
    PyObject* iter = PyObject_GetIter(cls_col);
    if (!iter) {
        return nullptr;
    }

    while (true) {
        PyObject* cls = PyIter_Next(iter);
        if (!cls) {
            // No more items or error.  If error, PyErr_Occurred() is set.
            if (PyErr_Occurred()) {
                Py_DECREF(iter);
                return nullptr;
            }
            break; // done
        }

        // impls_by_arg_cls[cls] = impl
        if (PyDict_SetItem(disp->impls_by_arg_cls, cls, impl) < 0) {
            Py_DECREF(cls);
            Py_DECREF(iter);
            return nullptr;
        }

        // If we haven't set cache_token yet, check for __abstractmethods__:
        if (disp->cache_token == 0) {
            int has_attr = PyObject_HasAttrString(cls, "__abstractmethods__");
            if (has_attr < 0) {
                // error
                Py_DECREF(cls);
                Py_DECREF(iter);
                return nullptr;
            }
            if (has_attr == 1) {
                // we call abc.get_cache_token() once
                PyObject* py_token = PyObject_CallNoArgs(g_abc_get_cache_token);
                if (!py_token) {
                    Py_DECREF(cls);
                    Py_DECREF(iter);
                    return nullptr;
                }
                long tk = PyLong_AsLong(py_token);
                Py_DECREF(py_token);
                if (tk == -1 && PyErr_Occurred()) {
                    Py_DECREF(cls);
                    Py_DECREF(iter);
                    return nullptr;
                }
                disp->cache_token = tk;
            }
        }

        Py_DECREF(cls);
    }
    Py_DECREF(iter);

    // self._dispatch_cache.clear()
    PyDict_Clear(disp->dispatch_cache);

    // Return impl (as in Python, we just return the same object).
    Py_INCREF(impl);
    return impl;
}

//  def dispatch(self, cls: type) -> T | None:
//      if self._cache_token is not None:
//          current_token = abc.get_cache_token()
//          if current_token != self._cache_token:
//              self._dispatch_cache.clear()
//              self._cache_token = current_token
//
//      cls_ref = weakref.ref(cls)
//      try:
//          return self._dispatch_cache[cls_ref]
//      except KeyError:
//          pass
//
//      # find impl
//      try:
//          impl = self._impls_by_arg_cls[cls]
//      except KeyError:
//          impl = self._find_impl(cls, self._impls_by_arg_cls)
//
//      self._dispatch_cache[weakref.ref(cls, self._cache_remove)] = impl
//      return impl
static PyObject*
Dispatcher_dispatch(PyObject* self, PyObject* args)
{
    DispatcherObject* disp = (DispatcherObject*)self;
    PyObject* cls = nullptr;
    if (!PyArg_ParseTuple(args, "O", &cls)) {
        return nullptr;
    }

    // If we have a nonzero cache_token, check if it’s still valid:
    if (disp->cache_token != 0) {
        PyObject* py_token = PyObject_CallNoArgs(g_abc_get_cache_token);
        if (!py_token) {
            return nullptr;
        }

        long new_token = PyLong_AsLong(py_token);
        Py_DECREF(py_token);
        if (new_token == -1 && PyErr_Occurred()) {
            return nullptr;
        }

        if (new_token != disp->cache_token) {
            // clear dispatch_cache
            PyDict_Clear(disp->dispatch_cache);
            disp->cache_token = new_token;
        }
    }

    // Attempt to get from dispatch_cache with a short-lived "cls_ref = weakref.ref(cls)"
    PyObject* cls_ref = PyWeakref_NewRef(cls, nullptr);
    if (!cls_ref) {
        return nullptr;
    }

    PyObject* res = PyDict_GetItem(disp->dispatch_cache, cls_ref);
    if (res) {
        // Found. Return it.
        Py_INCREF(res);
        Py_DECREF(cls_ref);
        return res;
    }
    // else KeyError path:
    Py_DECREF(cls_ref);

    // We attempt to do impl = _impls_by_arg_cls.get(cls), else find_impl
    PyObject* impl = PyDict_GetItem(disp->impls_by_arg_cls, cls);
    if (!impl) {
        // call self->find_impl(cls, self->impls_by_arg_cls)
        PyObject* args2 = Py_BuildValue("(OO)", cls, disp->impls_by_arg_cls);
        if (!args2) {
            return nullptr;
        }

        impl = PyObject_CallObject(disp->find_impl, args2);
        Py_DECREF(args2);
        if (!impl) {
            return nullptr;
        }

    } else {
        // We only borrowed 'impl' from the dict, so inc-ref:
        Py_INCREF(impl);

    }

    // Store in dispatch_cache under a new ref with callback:
    PyObject* callback = disp->cache_remove_callable;
    PyObject* new_ref = PyWeakref_NewRef(cls, callback);
    if (!new_ref) {
        Py_DECREF(impl);
        return nullptr;
    }
    if (PyDict_SetItem(disp->dispatch_cache, new_ref, impl) < 0) {
        Py_DECREF(new_ref);
        Py_DECREF(impl);
        return nullptr;
    }
    Py_DECREF(new_ref);

    // Return impl
    return impl;
}

// Define the methods of Dispatcher.
static PyMethodDef Dispatcher_methods[] = {
    {"cache_size", (PyCFunction)Dispatcher_cache_size, METH_NOARGS, "Return the size of the dispatch cache."},
    {"register", (PyCFunction)Dispatcher_register, METH_VARARGS, "Register an implementation for each class in cls_col."},
    {"dispatch", (PyCFunction)Dispatcher_dispatch, METH_VARARGS, "Dispatch an implementation for the given class (or None)."},
    {nullptr, nullptr, 0, nullptr}
};

// Deallocation (tp_dealloc) for Dispatcher.
static void
Dispatcher_dealloc(PyObject* self)
{
    DispatcherObject* disp = (DispatcherObject*)self;
    PyObject_GC_UnTrack(self);  // required if we are GC-tracked

    if (disp->weakreflist != nullptr) {
        PyObject_ClearWeakRefs((PyObject*) disp);
    }

    // Clear references:
    Py_XDECREF(disp->find_impl);
    Py_XDECREF(disp->impls_by_arg_cls);
    Py_XDECREF(disp->dispatch_cache);
    Py_XDECREF(disp->cache_remove_callable);

    Py_TYPE(self)->tp_free(self);
}

// GC support: traverse all Python references.
static int
Dispatcher_traverse(PyObject* self, visitproc visit, void* arg)
{
    DispatcherObject* disp = (DispatcherObject*)self;
    Py_VISIT(disp->find_impl);
    Py_VISIT(disp->impls_by_arg_cls);
    Py_VISIT(disp->dispatch_cache);
    Py_VISIT(disp->cache_remove_callable);
    return 0;
}

// GC support: clear strong references.
static int
Dispatcher_clear(PyObject* self)
{
    DispatcherObject* disp = (DispatcherObject*)self;
    Py_CLEAR(disp->find_impl);
    Py_CLEAR(disp->impls_by_arg_cls);
    Py_CLEAR(disp->dispatch_cache);
    Py_CLEAR(disp->cache_remove_callable);
    disp->cache_token = 0;
    return 0;
}

// The type definition for our Dispatcher class.
static PyTypeObject Dispatcher_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = MODULE_NAME ".Dispatcher",
    .tp_basicsize = sizeof(DispatcherObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .tp_doc = "Native Dispatcher type",
    .tp_methods = Dispatcher_methods,
    .tp_init = Dispatcher_init,
    .tp_new = PyType_GenericNew,    // let Python handle basic allocation
    .tp_dealloc = Dispatcher_dealloc,
    .tp_traverse = Dispatcher_traverse,
    .tp_clear = Dispatcher_clear,
    .tp_weaklistoffset = offsetof(DispatcherObject, weakreflist),
};

// Module-level method table (if any).
static PyMethodDef dispatcher_module_methods[] = {
    {nullptr, nullptr, 0, nullptr} // sentinel
};

// Module definition.
static struct PyModuleDef dispatcher_module = {
    PyModuleDef_HEAD_INIT,
    MODULE_NAME,
    "A fast native Dispatcher with weakref-based caching",
    -1,  // m_size
    dispatcher_module_methods,
    nullptr, // slots
    nullptr, // traverse
    nullptr, // clear
    nullptr  // free
};

// Module initialization function.
PyMODINIT_FUNC
PyInit__gpto1_2(void)
{
    // Initialize our DispatcherCacheRemove type
    if (PyType_Ready(&DispatcherCacheRemove_Type) < 0) {
        return nullptr;
    }

    // Initialize our Dispatcher type
    if (PyType_Ready(&Dispatcher_Type) < 0) {
        return nullptr;
    }

    // Create the module
    PyObject* m = PyModule_Create(&dispatcher_module);
    if (!m) {
        return nullptr;
    }

    // Expose the Dispatcher type
    Py_INCREF(&Dispatcher_Type);
    if (PyModule_AddObject(m, "Dispatcher", (PyObject*)&Dispatcher_Type) < 0) {
        Py_DECREF(&Dispatcher_Type);
        Py_DECREF(m);
        return nullptr;
    }

    // Import abc and store abc.get_cache_token globally
    {
        PyObject* abc_mod = PyImport_ImportModule("abc");
        if (!abc_mod) {
            Py_DECREF(m);
            return nullptr;
        }
        g_abc_get_cache_token = PyObject_GetAttrString(abc_mod, "get_cache_token");
        Py_DECREF(abc_mod);
        if (!g_abc_get_cache_token) {
            Py_DECREF(m);
            return nullptr;
        }
        // we keep g_abc_get_cache_token alive for the duration of the process
        // no DECREF here, as we need it permanently
    }

    return m;
}
