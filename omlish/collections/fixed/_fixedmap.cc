// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <atomic>

#define _MODULE_NAME "_fixedmap"
#define _PACKAGE_NAME "omlish.collections.fixed"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

//
// Types & Structs
//

struct FixedMapKeysObject {
    PyObject_HEAD
    PyObject* keys_tuple;
    PyObject* key_indexes;
    Py_hash_t hash_cache;
};

struct FixedMapObject {
    PyObject_HEAD
    FixedMapKeysObject* keys;
    PyObject* values_tuple;
    Py_hash_t hash_cache;
};

// Iterator modes
enum IterMode {
    ITER_KEYS_VALUES = 0,  // Yields integers 0...len
    ITER_KEYS_ITEMS = 1,   // Yields (key, index)
    ITER_MAP_ITEMS = 2     // Yields (key, value)
};

struct FixedMapIterObject {
    PyObject_HEAD
    PyObject* source;  // FixedMapKeysObject or FixedMapObject
    int mode;
    Py_ssize_t index;
};

typedef struct fixedmap_state {
    PyTypeObject* FixedMapKeys_Type;
    PyTypeObject* FixedMap_Type;
    PyTypeObject* FixedMapIter_Type;
} fixedmap_state;

static inline fixedmap_state* get_module_state(PyObject* module) {
    void* state = PyModule_GetState(module);
    assert(state != NULL);
    return (fixedmap_state*)state;
}

static inline fixedmap_state* get_type_state(PyTypeObject* type) {
    void* state = PyType_GetModuleState(type);
    assert(state != NULL);
    return (fixedmap_state*)state;
}

//
// Common Utilities
//

static int dummy_init(PyObject* self, PyObject* args, PyObject* kwds) {
    // Swallow the arguments since everything is handled in tp_new
    return 0;
}

//
// FixedMapIter Implementation
//

static int FixedMapIter_traverse(FixedMapIterObject* self, visitproc visit, void* arg) {
    Py_VISIT(self->source);
    return 0;
}

static int FixedMapIter_clear(FixedMapIterObject* self) {
    Py_CLEAR(self->source);
    return 0;
}

static void FixedMapIter_dealloc(FixedMapIterObject* self) {
    PyObject_GC_UnTrack(self);
    FixedMapIter_clear(self);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* FixedMapIter_iternext(FixedMapIterObject* self) {
    PyObject* source = Py_NewRef(self->source);

    std::atomic_ref<Py_ssize_t> index_ref(self->index);
    Py_ssize_t i = index_ref.fetch_add(1, std::memory_order_relaxed);

    PyObject* result = NULL;

    if (self->mode == ITER_KEYS_VALUES || self->mode == ITER_KEYS_ITEMS) {
        FixedMapKeysObject* keys = (FixedMapKeysObject*)source;
        if (i >= PyTuple_GET_SIZE(keys->keys_tuple)) {
            goto done;
        }

        if (self->mode == ITER_KEYS_VALUES) {
            result = PyLong_FromSsize_t(i);
        } else {  // ITER_KEYS_ITEMS
            PyObject* key = PyTuple_GET_ITEM(keys->keys_tuple, i);
            PyObject* val = PyLong_FromSsize_t(i);
            if (!val) {
                goto done;
            }
            result = PyTuple_Pack(2, key, val);
            Py_DECREF(val);
        }
    } else {  // ITER_MAP_ITEMS
        FixedMapObject* map = (FixedMapObject*)source;
        if (i >= PyTuple_GET_SIZE(map->values_tuple)) {
            goto done;
        }

        PyObject* key = PyTuple_GET_ITEM(map->keys->keys_tuple, i);
        PyObject* val = PyTuple_GET_ITEM(map->values_tuple, i);
        result = PyTuple_Pack(2, key, val);
    }

done:
    Py_DECREF(source);
    return result;
}

static PyType_Slot FixedMapIter_slots[] = {
    {Py_tp_dealloc, (void*)FixedMapIter_dealloc},
    {Py_tp_traverse, (void*)FixedMapIter_traverse},
    {Py_tp_clear, (void*)FixedMapIter_clear},
    {Py_tp_iter, (void*)PyObject_SelfIter},
    {Py_tp_iternext, (void*)FixedMapIter_iternext},
    {0, NULL}
};

static PyType_Spec FixedMapIter_spec = {
    .name = _MODULE_FULL_NAME ".FixedMapIter",
    .basicsize = sizeof(FixedMapIterObject),
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = FixedMapIter_slots,
};

static PyObject* new_iterator(PyObject* source, int mode, fixedmap_state* state) {
    FixedMapIterObject* iter = PyObject_GC_New(FixedMapIterObject, state->FixedMapIter_Type);
    if (!iter) {
        return NULL;
    }
    iter->source = Py_NewRef(source);
    iter->mode = mode;
    iter->index = 0;
    PyObject_GC_Track(iter);
    return (PyObject*)iter;
}

//
// FixedMapKeys Implementation
//

static int FixedMapKeys_traverse(FixedMapKeysObject* self, visitproc visit, void* arg) {
    Py_VISIT(self->keys_tuple);
    Py_VISIT(self->key_indexes);
    return 0;
}

static int FixedMapKeys_clear(FixedMapKeysObject* self) {
    Py_CLEAR(self->keys_tuple);
    Py_CLEAR(self->key_indexes);
    return 0;
}

static void FixedMapKeys_dealloc(FixedMapKeysObject* self) {
    PyObject_GC_UnTrack(self);
    FixedMapKeys_clear(self);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* FixedMapKeys_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    PyObject* keys_arg;
    if (!PyArg_ParseTuple(args, "O", &keys_arg)) {
        return NULL;
    }

    FixedMapKeysObject* self = (FixedMapKeysObject*)type->tp_alloc(type, 0);
    if (!self) {
        return NULL;
    }

    self->keys_tuple = NULL;
    self->key_indexes = NULL;
    self->hash_cache = 0;

    PyObject_GC_Track(self);

    PyObject* keys_tuple = PySequence_Tuple(keys_arg);
    if (!keys_tuple) {
        Py_DECREF(self);
        return NULL;
    }

    PyObject* key_indexes = PyDict_New();
    if (!key_indexes) {
        Py_DECREF(keys_tuple);
        Py_DECREF(self);
        return NULL;
    }

    Py_ssize_t size = PyTuple_GET_SIZE(keys_tuple);
    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject* key = PyTuple_GET_ITEM(keys_tuple, i);

        // PyDict_Contains handles the thread-safe lookup we need
        int contains = PyDict_Contains(key_indexes, key);
        if (contains == -1) goto error;
        if (contains == 1) {
            PyErr_SetObject(PyExc_KeyError, key);
            goto error;
        }

        PyObject* val = PyLong_FromSsize_t(i);
        if (!val) goto error;
        int err = PyDict_SetItem(key_indexes, key, val);
        Py_DECREF(val);
        if (err < 0) goto error;
    }

    self->keys_tuple = keys_tuple;
    self->key_indexes = key_indexes;
    return (PyObject*)self;

error:
    Py_DECREF(keys_tuple);
    Py_DECREF(key_indexes);
    Py_DECREF(self);
    return NULL;
}

static Py_ssize_t FixedMapKeys_len(FixedMapKeysObject* self) {
    return PyTuple_GET_SIZE(self->keys_tuple);
}

static PyObject* FixedMapKeys_getitem(FixedMapKeysObject* self, PyObject* key) {
    PyObject* val;
    if (PyDict_GetItemRef(self->key_indexes, key, &val) < 0) {
        return NULL;  // Exception raised by GetItemRef
    }
    if (!val) {
        PyErr_SetObject(PyExc_KeyError, key);
        return NULL;
    }
    return val;
}

static int FixedMapKeys_contains(FixedMapKeysObject* self, PyObject* key) {
    return PyDict_Contains(self->key_indexes, key);
}

static Py_hash_t FixedMapKeys_hash(FixedMapKeysObject* self) {
    std::atomic_ref<Py_hash_t> hash_cache_ref(self->hash_cache);
    Py_hash_t cached = hash_cache_ref.load(std::memory_order_acquire);
    if (cached != 0) {
        return cached;
    }

    Py_hash_t computed = PyObject_Hash(self->keys_tuple);
    if (computed == -1) {
        return -1;
    }
    if (computed == 0) {
        computed = 1;
    }

    // Benign race: another thread may store the same value.
    hash_cache_ref.store(computed, std::memory_order_release);
    return computed;
}

static PyObject* FixedMapKeys_iter(FixedMapKeysObject* self) {
    return PyObject_GetIter(self->keys_tuple);
}

static PyObject* FixedMapKeys_keys(FixedMapKeysObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyObject_GetIter(self->keys_tuple);
}

static PyObject* FixedMapKeys_values(FixedMapKeysObject* self, PyObject* Py_UNUSED(ignored)) {
    fixedmap_state* state = get_type_state(Py_TYPE(self));
    return new_iterator((PyObject*)self, ITER_KEYS_VALUES, state);
}

static PyObject* FixedMapKeys_items(FixedMapKeysObject* self, PyObject* Py_UNUSED(ignored)) {
    fixedmap_state* state = get_type_state(Py_TYPE(self));
    return new_iterator((PyObject*)self, ITER_KEYS_ITEMS, state);
}

static PyObject* FixedMapKeys_get_fixed_keys(FixedMapKeysObject* self, void* closure) {
    return Py_NewRef(self->keys_tuple);
}

static PyObject* FixedMapKeys_get_debug(FixedMapKeysObject* self, void* closure) {
    return Py_NewRef(self->key_indexes);
}

static PyObject* FixedMapKeys_repr(FixedMapKeysObject* self) {
    PyObject* debug_repr = PyObject_Repr(self->key_indexes);
    if (!debug_repr) {
        return NULL;
    }
    PyObject* res = PyUnicode_FromFormat("%s(%U)", Py_TYPE(self)->tp_name, debug_repr);
    Py_DECREF(debug_repr);
    return res;
}

static PyMethodDef FixedMapKeys_methods[] = {
    {"keys", (PyCFunction)FixedMapKeys_keys, METH_NOARGS, NULL},
    {"values", (PyCFunction)FixedMapKeys_values, METH_NOARGS, NULL},
    {"items", (PyCFunction)FixedMapKeys_items, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static PyGetSetDef FixedMapKeys_getseters[] = {
    {"fixed_keys", (getter)FixedMapKeys_get_fixed_keys, NULL, NULL, NULL},
    {"debug", (getter)FixedMapKeys_get_debug, NULL, NULL, NULL},
    {NULL, NULL, NULL, NULL, NULL}
};

static PyType_Slot FixedMapKeys_slots[] = {
    {Py_tp_dealloc, (void *) FixedMapKeys_dealloc},
    {Py_tp_traverse, (void *) FixedMapKeys_traverse},
    {Py_tp_clear, (void *) FixedMapKeys_clear},
    {Py_tp_hash, (void *) FixedMapKeys_hash},
    {Py_tp_repr, (void *) FixedMapKeys_repr},
    {Py_tp_iter, (void *) FixedMapKeys_iter},
    {Py_tp_methods, (void *) FixedMapKeys_methods},
    {Py_tp_getset, (void *) FixedMapKeys_getseters},
    {Py_mp_length, (void *) FixedMapKeys_len},
    {Py_mp_subscript, (void *) FixedMapKeys_getitem},
    {Py_sq_contains, (void *) FixedMapKeys_contains},
    {Py_tp_new, (void *) FixedMapKeys_new},
    {Py_tp_init, (void *) dummy_init},
    {0, NULL}
};

static PyType_Spec FixedMapKeys_spec = {
    .name = _MODULE_FULL_NAME ".FixedMapKeys",
    .basicsize = sizeof(FixedMapKeysObject),
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE,
    .slots = FixedMapKeys_slots,
};

//
// FixedMap Implementation
//

static int FixedMap_traverse(FixedMapObject* self, visitproc visit, void* arg) {
    Py_VISIT(self->keys);
    Py_VISIT(self->values_tuple);
    return 0;
}

static int FixedMap_clear(FixedMapObject* self) {
    Py_CLEAR(self->keys);
    Py_CLEAR(self->values_tuple);
    return 0;
}

static void FixedMap_dealloc(FixedMapObject* self) {
    PyObject_GC_UnTrack(self);
    FixedMap_clear(self);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* FixedMap_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    PyObject* keys_arg;
    PyObject* values_arg;

    fixedmap_state* state = get_type_state(type);

    if (!PyArg_ParseTuple(args, "O!O", state->FixedMapKeys_Type, &keys_arg, &values_arg)) {
        return NULL;
    }

    FixedMapObject* self = (FixedMapObject*)type->tp_alloc(type, 0);
    if (!self) {
        return NULL;
    }

    self->keys = NULL;
    self->values_tuple = NULL;
    self->hash_cache = 0;

    // Explicitly track the object now so tp_dealloc is safe if we error out below
    PyObject_GC_Track(self);

    PyObject* values_tuple;
    if (PyTuple_CheckExact(values_arg)) {
        values_tuple = Py_NewRef(values_arg);
    } else {
        values_tuple = PySequence_Tuple(values_arg);
        if (!values_tuple) {
            Py_DECREF(self);
            return NULL;
        }
    }

    FixedMapKeysObject* keys_obj = (FixedMapKeysObject*)keys_arg;
    if (PyTuple_GET_SIZE(values_tuple) != PyTuple_GET_SIZE(keys_obj->keys_tuple)) {
        PyErr_SetString(PyExc_ValueError, "length of values does not match length of keys");
        Py_DECREF(values_tuple);
        Py_DECREF(self);
        return NULL;
    }

    self->keys = (FixedMapKeysObject*)Py_NewRef(keys_obj);
    self->values_tuple = values_tuple;
    return (PyObject*)self;
}

static Py_hash_t FixedMap_hash(FixedMapObject* self) {
    std::atomic_ref<Py_hash_t> hash_cache_ref(self->hash_cache);
    Py_hash_t cached = hash_cache_ref.load(std::memory_order_acquire);
    if (cached != 0) {
        return cached;
    }

    if (Py_EnterRecursiveCall(" in computing FixedMap hash")) {
        return -1;
    }

    // Get cached keys hash (delegates to FixedMapKeys_hash which caches internally)
    Py_hash_t keys_hash = PyObject_Hash((PyObject*)self->keys);
    if (keys_hash == -1) {
        Py_LeaveRecursiveCall();
        return -1;
    }

    Py_ssize_t size = PyTuple_GET_SIZE(self->values_tuple);
    Py_hash_t computed = 0x9e3779b9;  // Different seed from keys/tuple hash
    Py_hash_t mult = 1000003;

    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject* v = PyTuple_GET_ITEM(self->values_tuple, i);

        Py_hash_t h_v = PyObject_Hash(v);
        if (h_v == -1) {
            Py_LeaveRecursiveCall();
            return -1;
        }
        computed = (computed ^ h_v) * mult;
        mult += (Py_hash_t)(82520L + size + size + 2);
    }

    // Combine keys hash and values hash
    computed ^= keys_hash;

    Py_LeaveRecursiveCall();

    if (computed == -1) {
        computed = -2;
    }
    if (computed == 0) {
        computed = 1;
    }

    // Benign race: another thread may store the same value.
    hash_cache_ref.store(computed, std::memory_order_release);
    return computed;
}

static Py_ssize_t FixedMap_len(FixedMapObject* self) {
    return PyTuple_GET_SIZE(self->values_tuple);
}

static PyObject* FixedMap_getitem(FixedMapObject* self, PyObject* key) {
    PyObject* idx_obj;
    if (PyDict_GetItemRef(self->keys->key_indexes, key, &idx_obj) < 0) {
        return NULL;
    }
    if (!idx_obj) {
        PyErr_SetObject(PyExc_KeyError, key);
        return NULL;
    }

    Py_ssize_t idx = PyLong_AsSsize_t(idx_obj);
    Py_DECREF(idx_obj);
    if (idx == -1 && PyErr_Occurred()) {
        return NULL;
    }

    return Py_NewRef(PyTuple_GET_ITEM(self->values_tuple, idx));
}

static int FixedMap_contains(FixedMapObject* self, PyObject* key) {
    return PyDict_Contains(self->keys->key_indexes, key);
}

static PyObject* FixedMap_iter(FixedMapObject* self) {
    return PyObject_GetIter(self->keys->keys_tuple);
}

static PyObject* FixedMap_itervalues(FixedMapObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyObject_GetIter(self->values_tuple);
}

static PyObject* FixedMap_iteritems(FixedMapObject* self, PyObject* Py_UNUSED(ignored)) {
    fixedmap_state* state = get_type_state(Py_TYPE(self));
    return new_iterator((PyObject*)self, ITER_MAP_ITEMS, state);
}

static PyObject* FixedMap_get_fixed_keys(FixedMapObject* self, void* closure) {
    return Py_NewRef(self->keys);
}

static PyObject* FixedMap_get_fixed_values(FixedMapObject* self, void* closure) {
    return Py_NewRef(self->values_tuple);
}

static PyObject* FixedMap_get_debug(FixedMapObject* self, void* closure) {
    PyObject* d = PyDict_New();
    if (!d) {
        return NULL;
    }

    Py_ssize_t size = PyTuple_GET_SIZE(self->values_tuple);
    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject* k = PyTuple_GET_ITEM(self->keys->keys_tuple, i);
        PyObject* v = PyTuple_GET_ITEM(self->values_tuple, i);
        if (PyDict_SetItem(d, k, v) < 0) {
            Py_DECREF(d);
            return NULL;
        }
    }
    return d;
}

static PyObject* FixedMap_repr(FixedMapObject* self) {
    PyObject* d = FixedMap_get_debug(self, NULL);
    if (!d) {
        return NULL;
    }
    PyObject* debug_repr = PyObject_Repr(d);
    Py_DECREF(d);
    if (!debug_repr) {
        return NULL;
    }

    PyObject* res = PyUnicode_FromFormat("%s(%U)", Py_TYPE(self)->tp_name, debug_repr);
    Py_DECREF(debug_repr);
    return res;
}

static PyMethodDef FixedMap_methods[] = {
    {"itervalues", (PyCFunction)FixedMap_itervalues, METH_NOARGS, NULL},
    {"iteritems", (PyCFunction)FixedMap_iteritems, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static PyGetSetDef FixedMap_getseters[] = {
    {"fixed_keys", (getter)FixedMap_get_fixed_keys, NULL, NULL, NULL},
    {"fixed_values", (getter)FixedMap_get_fixed_values, NULL, NULL, NULL},
    {"debug", (getter)FixedMap_get_debug, NULL, NULL, NULL},
    {NULL, NULL, NULL, NULL, NULL}
};

static PyType_Slot FixedMap_slots[] = {
    {Py_tp_dealloc, (void *) FixedMap_dealloc},
    {Py_tp_traverse, (void *) FixedMap_traverse},
    {Py_tp_clear, (void *) FixedMap_clear},
    {Py_tp_hash, (void *) FixedMap_hash},
    {Py_tp_repr, (void *) FixedMap_repr},
    {Py_tp_iter, (void *) FixedMap_iter},
    {Py_tp_methods, (void *) FixedMap_methods},
    {Py_tp_getset, (void *) FixedMap_getseters},
    {Py_mp_length, (void *) FixedMap_len},
    {Py_mp_subscript, (void *) FixedMap_getitem},
    {Py_sq_contains, (void *) FixedMap_contains},
    {Py_tp_new, (void *) FixedMap_new},
    {Py_tp_init, (void *) dummy_init},
    {0, NULL}
};

static PyType_Spec FixedMap_spec = {
    .name = _MODULE_FULL_NAME ".FixedMap",
    .basicsize = sizeof(FixedMapObject),
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE,
    .slots = FixedMap_slots,
};

//
// Module Initialization
//

PyDoc_STRVAR(fixedmap_doc, "C++ optimized implementation of FixedMap.");

static int fixedmap_exec(PyObject* module) {
    fixedmap_state* state = get_module_state(module);

    state->FixedMapIter_Type = (PyTypeObject*)PyType_FromModuleAndSpec(module, &FixedMapIter_spec, NULL);
    if (!state->FixedMapIter_Type) {
        return -1;
    }

    state->FixedMapKeys_Type = (PyTypeObject*)PyType_FromModuleAndSpec(module, &FixedMapKeys_spec, NULL);
    if (!state->FixedMapKeys_Type) {
        return -1;
    }
    if (PyModule_AddType(module, state->FixedMapKeys_Type) < 0) {
        return -1;
    }

    state->FixedMap_Type = (PyTypeObject*)PyType_FromModuleAndSpec(module, &FixedMap_spec, NULL);
    if (!state->FixedMap_Type) {
        return -1;
    }
    if (PyModule_AddType(module, state->FixedMap_Type) < 0) {
        return -1;
    }

    return 0;
}

static int fixedmap_traverse(PyObject* module, visitproc visit, void* arg) {
    fixedmap_state* state = get_module_state(module);
    Py_VISIT(state->FixedMapKeys_Type);
    Py_VISIT(state->FixedMap_Type);
    Py_VISIT(state->FixedMapIter_Type);
    return 0;
}

static int fixedmap_clear(PyObject* module) {
    fixedmap_state* state = get_module_state(module);
    Py_CLEAR(state->FixedMapKeys_Type);
    Py_CLEAR(state->FixedMap_Type);
    Py_CLEAR(state->FixedMapIter_Type);
    return 0;
}

static void fixedmap_free(void* module) {
    fixedmap_clear((PyObject*)module);
}

static PyMethodDef fixedmap_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot fixedmap_slots[] = {
    {Py_mod_exec, (void*)fixedmap_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, NULL}
};

static struct PyModuleDef fixedmap_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = fixedmap_doc,
    .m_size = sizeof(fixedmap_state),
    .m_methods = fixedmap_methods,
    .m_slots = fixedmap_slots,
    .m_traverse = fixedmap_traverse,
    .m_clear = fixedmap_clear,
    .m_free = fixedmap_free,
};

extern "C" {
PyMODINIT_FUNC PyInit__fixedmap(void) {
    return PyModuleDef_Init(&fixedmap_module);
}
}
