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

// Views for FixedMap
struct FixedMapViewObject {
    PyObject_HEAD
    FixedMapObject* map;
};

// Iterator modes
enum IterMode {
    ITER_KEYS_VALUES = 0,
    ITER_KEYS_ITEMS = 1,
    ITER_MAP_ITEMS = 2
};

struct FixedMapIterObject {
    PyObject_HEAD
    PyObject* source;
    int mode;
    Py_ssize_t index;
};

typedef struct fixedmap_state {
    PyTypeObject* FixedMapKeys_Type;
    PyTypeObject* FixedMap_Type;
    PyTypeObject* FixedMapIter_Type;
    PyTypeObject* FixedMapValuesView_Type;
    PyTypeObject* FixedMapItemsView_Type;
} fixedmap_state;

static inline fixedmap_state* get_module_state(PyObject* module) {
    void* state = PyModule_GetState(module);
    assert(state != NULL);
    return (fixedmap_state*)state;
}

static inline fixedmap_state* get_type_state(PyTypeObject* type) {
    PyTypeObject* current = type;
    while (current != NULL) {
        void* state = PyType_GetModuleState(current);
        if (state != NULL) {
            return (fixedmap_state*)state;
        }
        current = current->tp_base;
    }
    Py_FatalError("_fixedmap state not found in type hierarchy");
    return NULL;
}

//
// Utilities
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
    std::atomic_ref<Py_ssize_t> index_ref(self->index);
    Py_ssize_t i = index_ref.fetch_add(1, std::memory_order_relaxed);

    if (self->mode == ITER_KEYS_VALUES || self->mode == ITER_KEYS_ITEMS) {
        FixedMapKeysObject* keys = (FixedMapKeysObject*)self->source;
        if (i >= PyTuple_GET_SIZE(keys->keys_tuple)) {
            return NULL;
        }

        if (self->mode == ITER_KEYS_VALUES) {
            return PyLong_FromSsize_t(i);
        } else {  // ITER_KEYS_ITEMS
            PyObject* key = PyTuple_GET_ITEM(keys->keys_tuple, i);
            PyObject* val = PyLong_FromSsize_t(i);
            if (!val) {
                return NULL;
            }
            PyObject* tuple = PyTuple_Pack(2, key, val);
            Py_DECREF(val);
            return tuple;
        }
    } else {
        FixedMapObject* map = (FixedMapObject*)self->source;
        if (i >= PyTuple_GET_SIZE(map->values_tuple)) {
            return NULL;
        }

        PyObject* key = PyTuple_GET_ITEM(map->keys->keys_tuple, i);
        PyObject* val = PyTuple_GET_ITEM(map->values_tuple, i);
        return PyTuple_Pack(2, key, val);
    }
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
// View Implementations (ValuesView and ItemsView)
//

static int FixedMapView_traverse(FixedMapViewObject* self, visitproc visit, void* arg) {
    Py_VISIT(self->map);
    return 0;
}

static int FixedMapView_clear(FixedMapViewObject* self) {
    Py_CLEAR(self->map);
    return 0;
}

static void FixedMapView_dealloc(FixedMapViewObject* self) {
    PyObject_GC_UnTrack(self);
    FixedMapView_clear(self);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static Py_ssize_t FixedMapView_len(FixedMapViewObject* self) {
    return PyTuple_GET_SIZE(self->map->values_tuple);
}

static PyObject* FixedMapValuesView_iter(FixedMapViewObject* self) {
    return PyObject_GetIter(self->map->values_tuple);
}

static PyObject* FixedMapItemsView_iter(FixedMapViewObject* self) {
    fixedmap_state* state = get_type_state(Py_TYPE(self));
    return new_iterator((PyObject*)self->map, ITER_MAP_ITEMS, state);
}

static PyType_Slot FixedMapValuesView_slots[] = {
    {Py_tp_dealloc, (void*)FixedMapView_dealloc},
    {Py_tp_traverse, (void*)FixedMapView_traverse},
    {Py_tp_clear, (void*)FixedMapView_clear},
    {Py_tp_iter, (void*)FixedMapValuesView_iter},
    {Py_mp_length, (void*)FixedMapView_len},
    {0, NULL}
};

static PyType_Spec FixedMapValuesView_spec = {
    .name = _MODULE_FULL_NAME ".FixedMapValuesView",
    .basicsize = sizeof(FixedMapViewObject),
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = FixedMapValuesView_slots,
};

static PyType_Slot FixedMapItemsView_slots[] = {
    {Py_tp_dealloc, (void*)FixedMapView_dealloc},
    {Py_tp_traverse, (void*)FixedMapView_traverse},
    {Py_tp_clear, (void*)FixedMapView_clear},
    {Py_tp_iter, (void*)FixedMapItemsView_iter},
    {Py_mp_length, (void*)FixedMapView_len},
    {0, NULL}
};

static PyType_Spec FixedMapItemsView_spec = {
    .name = _MODULE_FULL_NAME ".FixedMapItemsView",
    .basicsize = sizeof(FixedMapViewObject),
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = FixedMapItemsView_slots,
};

static PyObject* new_view(FixedMapObject* map, PyTypeObject* type) {
    FixedMapViewObject* view = PyObject_GC_New(FixedMapViewObject, type);
    if (!view) {
        return NULL;
    }
    view->map = (FixedMapObject*)Py_NewRef(map);
    PyObject_GC_Track(view);
    return (PyObject*)view;
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

    self->keys_tuple = PySequence_Tuple(keys_arg);
    if (!self->keys_tuple) {
        Py_DECREF(self);
        return NULL;
    }

    self->key_indexes = PyDict_New();
    if (!self->key_indexes) {
        Py_DECREF(self);
        return NULL;
    }

    Py_ssize_t size = PyTuple_GET_SIZE(self->keys_tuple);
    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject* key = PyTuple_GET_ITEM(self->keys_tuple, i);
        int contains = PyDict_Contains(self->key_indexes, key);
        if (contains == -1 || contains == 1) {
            if (contains == 1) {
                PyErr_SetObject(PyExc_KeyError, key);
            }
            Py_DECREF(self);
            return NULL;
        }
        PyObject* val = PyLong_FromSsize_t(i);
        if (!val || PyDict_SetItem(self->key_indexes, key, val) < 0) {
            Py_XDECREF(val);
            Py_DECREF(self);
            return NULL;
        }
        Py_DECREF(val);
    }

    self->hash_cache = 0;

    if (!PyObject_GC_IsTracked((PyObject*)self)) {
        PyObject_GC_Track(self);
    }
    return (PyObject*)self;
}

static Py_ssize_t FixedMapKeys_len(FixedMapKeysObject* self) {
    return PyTuple_GET_SIZE(self->keys_tuple);
}

static PyObject* FixedMapKeys_getitem(FixedMapKeysObject* self, PyObject* key) {
    PyObject* val;
    if (PyDict_GetItemRef(self->key_indexes, key, &val) < 0) {
        return NULL;
    }
    if (!val) {
        PyErr_SetObject(PyExc_KeyError, key);
        return NULL;
    }
    return val;
}

static PyObject* FixedMapKeys_get(FixedMapKeysObject* self, PyObject* args) {
    PyObject *key = Py_None;
    PyObject *def = Py_None;
    if (!PyArg_ParseTuple(args, "O|O", &key, &def)) {
        return NULL;
    }
    PyObject* val;
    if (PyDict_GetItemRef(self->key_indexes, key, &val) < 0) {
        return NULL;
    }
    return val ? val : Py_NewRef(def);
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

static PyObject* FixedMapKeys_richcompare(PyObject* a, PyObject* b, int op) {
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    if (a == b) {
        if (op == Py_EQ) {
            Py_RETURN_TRUE;
        } else {
            Py_RETURN_FALSE;
        }
    }
    fixedmap_state* state = get_type_state(Py_TYPE(a));
    if (!PyObject_TypeCheck(a, state->FixedMapKeys_Type)) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    if (PyObject_TypeCheck(b, state->FixedMapKeys_Type)) {
        return PyObject_RichCompare(((FixedMapKeysObject*)a)->keys_tuple, ((FixedMapKeysObject*)b)->keys_tuple, op);
    }
    Py_RETURN_NOTIMPLEMENTED;
}

static PyObject* FixedMapKeys_keys(FixedMapKeysObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyObject_CallMethod(self->key_indexes, "keys", NULL);
}

static PyObject* FixedMapKeys_values(FixedMapKeysObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyObject_CallMethod(self->key_indexes, "values", NULL);
}

static PyObject* FixedMapKeys_items(FixedMapKeysObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyObject_CallMethod(self->key_indexes, "items", NULL);
}

static PyMethodDef FixedMapKeys_methods[] = {
    {"get", (PyCFunction)FixedMapKeys_get, METH_VARARGS, NULL},
    {"keys", (PyCFunction)FixedMapKeys_keys, METH_NOARGS, NULL},
    {"values", (PyCFunction)FixedMapKeys_values, METH_NOARGS, NULL},
    {"items", (PyCFunction)FixedMapKeys_items, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static PyObject* FixedMapKeys_get_fixed_keys(FixedMapKeysObject* self, void* Py_UNUSED(closure)) {
    return Py_NewRef(self->keys_tuple);
}

static PyObject* FixedMapKeys_get_debug(FixedMapKeysObject* self, void* Py_UNUSED(closure)) {
    return PyDictProxy_New(self->key_indexes);
}

static PyObject* FixedMapKeys_repr(FixedMapKeysObject* self) {
    PyObject* name = PyType_GetName(Py_TYPE(self));
    if (!name) {
        return NULL;
    }
    PyObject *repr = PyUnicode_FromFormat("%U(%R)", name, self->key_indexes);
    Py_DECREF(name);
    return repr;
}

static PyObject* FixedMapKeys_iter(FixedMapKeysObject* self) {
    return PyObject_GetIter(self->keys_tuple);
}

static int FixedMapKeys_contains(FixedMapKeysObject* self, PyObject* key) {
    return PyDict_Contains(self->key_indexes, key);
}

static PyGetSetDef FixedMapKeys_getsets[] = {
    {"fixed_keys", (getter)FixedMapKeys_get_fixed_keys, NULL, NULL, NULL},
    {"debug", (getter)FixedMapKeys_get_debug, NULL, NULL, NULL},
    {NULL, NULL, NULL, NULL, NULL}
};

static PyType_Slot FixedMapKeys_slots[] = {
    {Py_tp_dealloc, (void*)FixedMapKeys_dealloc},
    {Py_tp_traverse, (void*)FixedMapKeys_traverse},
    {Py_tp_clear, (void*)FixedMapKeys_clear},
    {Py_tp_hash, (void*)FixedMapKeys_hash},
    {Py_tp_richcompare, (void*)FixedMapKeys_richcompare},
    {Py_tp_repr, (void*)FixedMapKeys_repr},
    {Py_tp_iter, (void*)FixedMapKeys_iter},
    {Py_tp_methods, (void*)FixedMapKeys_methods},
    {Py_tp_getset, (void*)FixedMapKeys_getsets},
    {Py_mp_length, (void*)FixedMapKeys_len},
    {Py_mp_subscript, (void*)FixedMapKeys_getitem},
    {Py_sq_contains, (void*)FixedMapKeys_contains},
    {Py_tp_new, (void*)FixedMapKeys_new},
    {Py_tp_init, (void*)dummy_init},
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

    self->values_tuple = PyTuple_CheckExact(values_arg) ? Py_NewRef(values_arg) : PySequence_Tuple(values_arg);
    if (!self->values_tuple) {
        Py_DECREF(self);
        return NULL;
    }

    FixedMapKeysObject* keys_obj = (FixedMapKeysObject*)keys_arg;
    if (PyTuple_GET_SIZE(self->values_tuple) != PyTuple_GET_SIZE(keys_obj->keys_tuple)) {
        PyErr_SetString(PyExc_ValueError, "length mismatch");
        Py_DECREF(self);
        return NULL;
    }

    self->keys = (FixedMapKeysObject*)Py_NewRef(keys_obj);
    self->hash_cache = 0;
    if (!PyObject_GC_IsTracked((PyObject*)self)) {
        PyObject_GC_Track(self);
    }
    return (PyObject*)self;
}

static Py_hash_t FixedMap_hash(FixedMapObject* self) {
    std::atomic_ref<Py_hash_t> cache(self->hash_cache);
    Py_hash_t h = cache.load(std::memory_order_acquire);
    if (h != 0) {
        return h;
    }
    if (Py_EnterRecursiveCall(" in FixedMap hash")) {
        return -1;
    }

    Py_hash_t kh = PyObject_Hash((PyObject*)self->keys);
    if (kh == -1) {
        Py_LeaveRecursiveCall();
        return -1;
    }

    Py_ssize_t size = PyTuple_GET_SIZE(self->values_tuple);
    Py_hash_t res = 0x9e3779b9;
    for (Py_ssize_t i = 0; i < size; i++) {
        Py_hash_t vh = PyObject_Hash(PyTuple_GET_ITEM(self->values_tuple, i));
        if (vh == -1) {
            Py_LeaveRecursiveCall();
            return -1;
        }
        res = (res ^ vh) * 1000003 + (82520L + size + size + 2);
    }
    res ^= kh;
    Py_LeaveRecursiveCall();
    if (res == -1) {
        res = -2;
    } else if (res == 0) {
        res = 1;
    }
    cache.store(res, std::memory_order_release);
    return res;
}

static PyObject* FixedMap_richcompare(PyObject* a, PyObject* b, int op) {
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    if (a == b) {
        if (op == Py_EQ) {
            Py_RETURN_TRUE;
        } else {
            Py_RETURN_FALSE;
        }
    }

    if (Py_EnterRecursiveCall(" in FixedMap richcompare")) {
        return NULL;
    }

    fixedmap_state* state = get_type_state(Py_TYPE(a));
    if (PyObject_TypeCheck(b, state->FixedMap_Type)) {
        FixedMapObject *ma = (FixedMapObject*)a, *mb = (FixedMapObject*)b;
        if (PyTuple_GET_SIZE(ma->values_tuple) != PyTuple_GET_SIZE(mb->values_tuple)) {
            Py_LeaveRecursiveCall();
            if (op == Py_EQ) {
                Py_RETURN_FALSE;
            } else {
                Py_RETURN_TRUE;
            }
        }
        if (ma->keys == mb->keys) {
            PyObject* ret = PyObject_RichCompare(ma->values_tuple, mb->values_tuple, op);
            Py_LeaveRecursiveCall();
            return ret;
        }
    }

    Py_ssize_t al = PyObject_Length(a);
    if (al < 0) {
        PyErr_Clear();
    }
    Py_ssize_t bl = PyObject_Length(b);
    if (bl < 0) {
        PyErr_Clear();
    }
    if (al >= 0 && bl >= 0 && al != bl) {
        Py_LeaveRecursiveCall();
        if (op == Py_EQ) {
            Py_RETURN_FALSE;
        } else {
            Py_RETURN_TRUE;
        }
    }

    PyObject *it = PyObject_GetIter(a), *k;
    if (!it) {
        PyErr_Clear();
        Py_LeaveRecursiveCall();
        Py_RETURN_NOTIMPLEMENTED;
    }
    while ((k = PyIter_Next(it))) {
        PyObject *va = PyObject_GetItem(a, k), *vb = PyObject_GetItem(b, k);
        if (!va || !vb) {
            Py_XDECREF(va);
            Py_XDECREF(vb);
            Py_DECREF(k);
            Py_DECREF(it);
            if (!vb && PyErr_ExceptionMatches(PyExc_KeyError)) {
                PyErr_Clear();
                Py_LeaveRecursiveCall();
                if (op == Py_EQ) {
                    Py_RETURN_FALSE;
                } else {
                    Py_RETURN_TRUE;
                }
            }
            Py_LeaveRecursiveCall();
            return NULL;
        }
        int eq = PyObject_RichCompareBool(va, vb, Py_EQ);
        Py_DECREF(va);
        Py_DECREF(vb);
        Py_DECREF(k);
        if (eq <= 0) {
            Py_DECREF(it);
            if (eq < 0) {
                Py_LeaveRecursiveCall();
                return NULL;
            } else {
                Py_LeaveRecursiveCall();
                if (op == Py_EQ) {
                    Py_RETURN_FALSE;
                } else {
                    Py_RETURN_TRUE;
                }
            }
        }
    }
    Py_DECREF(it);
    if (PyErr_Occurred()) {
        Py_LeaveRecursiveCall();
        return NULL;
    }
    Py_LeaveRecursiveCall();
    if (op == Py_EQ) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
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

    if (idx < 0 || idx >= PyTuple_GET_SIZE(self->values_tuple)) {
        PyErr_SetString(PyExc_RuntimeError, "corrupt FixedMap index");
        return NULL;
    }

    return Py_NewRef(PyTuple_GET_ITEM(self->values_tuple, idx));
}

static PyObject* FixedMap_get(FixedMapObject* self, PyObject* args) {
    PyObject *key, *def = Py_None, *idx;
    if (!PyArg_ParseTuple(args, "O|O", &key, &def)) {
        return NULL;
    }
    if (PyDict_GetItemRef(self->keys->key_indexes, key, &idx) < 0) {
        return NULL;
    }
    if (!idx) {
        return Py_NewRef(def);
    }

    Py_ssize_t i = PyLong_AsSsize_t(idx);
    Py_DECREF(idx);
    if (i == -1 && PyErr_Occurred()) {
        return NULL;
    }

    if (i < 0 || i >= PyTuple_GET_SIZE(self->values_tuple)) {
        PyErr_SetString(PyExc_RuntimeError, "corrupt FixedMap index");
        return NULL;
    }

    return Py_NewRef(PyTuple_GET_ITEM(self->values_tuple, i));
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
    PyObject* name = PyType_GetName(Py_TYPE(self));
    if (!name) {
        Py_DECREF(d);
        return NULL;
    }
    PyObject* res = PyUnicode_FromFormat("%U(%R)", name, d);
    Py_DECREF(name);
    Py_DECREF(d);
    return res;
}

static PyObject* FixedMap_keys(FixedMapObject* self, PyObject* Py_UNUSED(ignored)) {
    return Py_NewRef(self->keys);
}

static PyObject* FixedMap_values(FixedMapObject* self, PyObject* Py_UNUSED(ignored)) {
    return new_view(self, get_type_state(Py_TYPE(self))->FixedMapValuesView_Type);
}

static PyObject* FixedMap_items(FixedMapObject* self, PyObject* Py_UNUSED(ignored)) {
    return new_view(self, get_type_state(Py_TYPE(self))->FixedMapItemsView_Type);
}

static PyObject* FixedMap_itervalues(FixedMapObject* self, PyObject* Py_UNUSED(ignored)) {
    return PyObject_GetIter(self->values_tuple);
}

static PyObject* FixedMap_iteritems(FixedMapObject* self, PyObject* Py_UNUSED(ignored)) {
    return new_iterator((PyObject*)self, ITER_MAP_ITEMS, get_type_state(Py_TYPE(self)));
}

static PyObject* FixedMap_iter(FixedMapObject* self) {
    return PyObject_GetIter(self->keys->keys_tuple);
}

static Py_ssize_t FixedMap_len(FixedMapObject* self) {
    return PyTuple_GET_SIZE(self->values_tuple);
}

static int FixedMap_contains(FixedMapObject* self, PyObject* key) {
    return PyDict_Contains(self->keys->key_indexes, key);
}


static PyMethodDef FixedMap_methods[] = {
    {"get", (PyCFunction)FixedMap_get, METH_VARARGS, NULL},
    {"keys", (PyCFunction)FixedMap_keys, METH_NOARGS, NULL},
    {"values", (PyCFunction)FixedMap_values, METH_NOARGS, NULL},
    {"items", (PyCFunction)FixedMap_items, METH_NOARGS, NULL},
    {"itervalues", (PyCFunction)FixedMap_itervalues, METH_NOARGS, NULL},
    {"iteritems", (PyCFunction)FixedMap_iteritems, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static PyGetSetDef FixedMap_getsets[] = {
    {"fixed_keys", (getter)FixedMap_get_fixed_keys, NULL, NULL, NULL},
    {"fixed_values", (getter)FixedMap_get_fixed_values, NULL, NULL, NULL},
    {"debug", (getter)FixedMap_get_debug, NULL, NULL, NULL},
    {NULL, NULL, NULL, NULL, NULL}
};

static PyType_Slot FixedMap_slots[] = {
    {Py_tp_dealloc, (void*)FixedMap_dealloc},
    {Py_tp_traverse, (void*)FixedMap_traverse},
    {Py_tp_clear, (void*)FixedMap_clear},
    {Py_tp_hash, (void*)FixedMap_hash},
    {Py_tp_richcompare, (void*)FixedMap_richcompare},
    {Py_tp_repr, (void*)FixedMap_repr},
    {Py_tp_iter, (void*)FixedMap_iter},
    {Py_tp_methods, (void*)FixedMap_methods},
    {Py_tp_getset, (void*)FixedMap_getsets},
    {Py_mp_length, (void*)FixedMap_len},
    {Py_mp_subscript, (void*)FixedMap_getitem},
    {Py_sq_contains, (void*)FixedMap_contains},
    {Py_tp_new, (void*)FixedMap_new},
    {Py_tp_init, (void*)dummy_init},
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

    state->FixedMapIter_Type = (PyTypeObject*)PyType_FromModuleAndSpec(module, &FixedMapIter_spec, NULL);
    if (!state->FixedMapIter_Type) {
        return -1;
    }
    if (PyModule_AddType(module, state->FixedMapIter_Type) < 0) {
        return -1;
    }

    state->FixedMapValuesView_Type = (PyTypeObject*)PyType_FromModuleAndSpec(module, &FixedMapValuesView_spec, NULL);
    if (!state->FixedMapValuesView_Type) {
        return -1;
    }
    if (PyModule_AddType(module, state->FixedMapValuesView_Type) < 0) {
        return -1;
    }

    state->FixedMapItemsView_Type = (PyTypeObject*)PyType_FromModuleAndSpec(module, &FixedMapItemsView_spec, NULL);
    if (!state->FixedMapItemsView_Type) {
        return -1;
    }
    if (PyModule_AddType(module, state->FixedMapItemsView_Type) < 0) {
        return -1;
    }

    return 0;
}

static int fixedmap_traverse(PyObject* module, visitproc visit, void* arg) {
    fixedmap_state* state = get_module_state(module);
    Py_VISIT(state->FixedMapKeys_Type);
    Py_VISIT(state->FixedMap_Type);
    Py_VISIT(state->FixedMapIter_Type);
    Py_VISIT(state->FixedMapValuesView_Type);
    Py_VISIT(state->FixedMapItemsView_Type);
    return 0;
}

static int fixedmap_clear(PyObject* module) {
    fixedmap_state* state = get_module_state(module);
    Py_CLEAR(state->FixedMapKeys_Type);
    Py_CLEAR(state->FixedMap_Type);
    Py_CLEAR(state->FixedMapIter_Type);
    Py_CLEAR(state->FixedMapValuesView_Type);
    Py_CLEAR(state->FixedMapItemsView_Type);
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
