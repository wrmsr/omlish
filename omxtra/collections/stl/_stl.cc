// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <cstdint>
#include <cstring>
#include <exception>
#include <map>
#include <new>
#include <utility>
#include <vector>
#include <type_traits>


#define _MODULE_NAME "_stl"
#define _PACKAGE_NAME "omxtra.collections.stl"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME


struct stl_state;
struct BaseMapObject;
struct MapIterObject;

static PyModuleDef *stl_module_def(void);


typedef struct stl_state {
    PyTypeObject *MapIterType;
    PyTypeObject *MapI64I64Type;
    PyTypeObject *MapI64ObjType;
    PyTypeObject *MapObjI64Type;
    PyTypeObject *MapObjObjType;
} stl_state;

static inline stl_state *get_stl_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != nullptr);
    return (stl_state *)state;
}

static inline stl_state *get_stl_state_for_type(PyTypeObject *type)
{
    PyObject *module = PyType_GetModuleByDef(type, stl_module_def());
    if (module == nullptr) {
        return nullptr;
    }
    return get_stl_state(module);
}


enum map_kind : uint8_t {
    MAP_KIND_I64_I64 = 1,
    MAP_KIND_I64_OBJ = 2,
    MAP_KIND_OBJ_I64 = 3,
    MAP_KIND_OBJ_OBJ = 4,
};

enum map_iter_kind : uint8_t {
    MAP_ITER_KEYS = 1,
    MAP_ITER_VALUES = 2,
    MAP_ITER_ITEMS = 3,
};


struct BaseMapObject {
    PyObject_HEAD
    PyMutex mutex;
    uint64_t version;
    map_kind kind;
    void *impl;
};


// Thread-Local Context for Optimistic Lock Elision

struct CompareContext {
    CompareContext *prev;
    BaseMapObject *map_obj;
    uint64_t start_version;
};

// C++11 thread_local ensures thread safety without locking
thread_local CompareContext *g_compare_context = nullptr;

struct CompareContextGuard {
    CompareContext ctx;

    CompareContextGuard(BaseMapObject *map, uint64_t version) {
        ctx.prev = g_compare_context;
        ctx.map_obj = map;
        ctx.start_version = version;
        g_compare_context = &ctx;
    }

    ~CompareContextGuard() {
        g_compare_context = ctx.prev;
    }
};

struct PyCompareError final : std::exception {};
struct PyMapMutatedError final : std::exception {};

struct ObjKeyCompare {
    bool operator()(PyObject *l, PyObject *r) const
    {
        if (l == r) {
            return false;
        }

        CompareContext *ctx = g_compare_context;

        // Pin the objects. If another thread drops the lock and deletes these
        // from the map, we don't want a segfault inside RichCompareBool.
        Py_INCREF(l);
        Py_INCREF(r);

        // Drop the lock to avoid GC/Re-entrancy deadlocks
        PyMutex_Unlock(&ctx->map_obj->mutex);

        // std::map only requires Strict Weak Ordering, so Py_LT is sufficient.
        int lt = PyObject_RichCompareBool(l, r, Py_LT);

        // Re-acquire the lock to resume C++ STL invariants
        PyMutex_Lock(&ctx->map_obj->mutex);

        Py_DECREF(l);
        Py_DECREF(r);

        if (lt < 0) {
            throw PyCompareError();
        }

        // The Abort Switch: If another thread mutated the map while we were
        // in Python land, our iterators/tree-state are invalid. Abort!
        if (ctx->map_obj->version != ctx->start_version) {
            throw PyMapMutatedError();
        }

        return lt > 0;
    }
};


template <typename K, typename V>
struct PlainMapImpl {
    using map_type = std::map<K, V>;
    map_type map;
};

template <typename V>
struct ObjKeyMapImpl {
    using map_type = std::map<PyObject *, V, ObjKeyCompare>;
    map_type map;
};

using MapI64I64Impl = PlainMapImpl<int64_t, int64_t>;
using MapI64ObjImpl = PlainMapImpl<int64_t, PyObject *>;
using MapObjI64Impl = ObjKeyMapImpl<int64_t>;
using MapObjObjImpl = ObjKeyMapImpl<PyObject *>;


struct MapIterObject {
    PyObject_HEAD
    PyObject *owner;
    uint64_t expected_version;
    map_iter_kind kind;
    void *state;
};


static int py_to_i64(PyObject *obj, int64_t *out)
{
    long long v = PyLong_AsLongLong(obj);
    if (v == -1 && PyErr_Occurred()) {
        return -1;
    }
    *out = (int64_t)v;
    return 0;
}

static PyObject *i64_to_py(int64_t v)
{
    return PyLong_FromLongLong((long long)v);
}

static int py_to_obj_owned(PyObject *obj, PyObject **out)
{
    *out = Py_NewRef(obj);
    return 0;
}

static PyObject *obj_to_py(PyObject *obj)
{
    return Py_NewRef(obj);
}


template <typename T>
static inline int visit_maybe_pyobject(const T &, visitproc, void *)
{
    return 0;
}

template <>
inline int visit_maybe_pyobject<PyObject *>(PyObject *const &obj, visitproc visit, void *arg)
{
    Py_VISIT(obj);
    return 0;
}


template <typename T>
static inline void append_maybe_pyobject(std::vector<PyObject *> &, const T &)
{
}

template <>
inline void append_maybe_pyobject<PyObject *>(std::vector<PyObject *> &out, PyObject *const &obj)
{
    if (obj != nullptr) {
        out.push_back(obj);
    }
}


template <typename K, typename V, typename Map>
static int traverse_map_impl(Map &map, visitproc visit, void *arg)
{
    for (auto const &entry : map) {
        // BUG FIX: The Py_VISIT macro returns a positive integer if a cycle
        // path is found. Checking `< 0` silently swallowed the GC traversal.
        if (visit_maybe_pyobject<K>(entry.first, visit, arg) != 0) {
            return -1;
        }
        if (visit_maybe_pyobject<V>(entry.second, visit, arg) != 0) {
            return -1;
        }
    }

    return 0;
}


template <typename K, typename V, typename Map>
static void detach_map_impl_refs(Map &map, std::vector<PyObject *> &refs)
{
    for (auto const &entry : map) {
        append_maybe_pyobject<K>(refs, entry.first);
        append_maybe_pyobject<V>(refs, entry.second);
    }
    map.clear();
}


static Py_ssize_t map_len_unlocked(BaseMapObject *self)
{
    switch (self->kind) {
        case MAP_KIND_I64_I64:
            return (Py_ssize_t)((MapI64I64Impl *)self->impl)->map.size();
        case MAP_KIND_I64_OBJ:
            return (Py_ssize_t)((MapI64ObjImpl *)self->impl)->map.size();
        case MAP_KIND_OBJ_I64:
            return (Py_ssize_t)((MapObjI64Impl *)self->impl)->map.size();
        case MAP_KIND_OBJ_OBJ:
            return (Py_ssize_t)((MapObjObjImpl *)self->impl)->map.size();
        default:
            PyErr_SetString(PyExc_RuntimeError, "invalid map kind");
            return -1;
    }
}

static Py_ssize_t map_len(BaseMapObject *self)
{
    Py_ssize_t ret;
    PyMutex_Lock(&self->mutex);
    ret = map_len_unlocked(self);
    PyMutex_Unlock(&self->mutex);
    return ret;
}


static int map_traverse(BaseMapObject *self, visitproc visit, void *arg)
{
    PyMutex_Lock(&self->mutex);

    if (self->impl != nullptr) {
        switch (self->kind) {
            case MAP_KIND_I64_I64:
                if (traverse_map_impl<int64_t, int64_t>(((MapI64I64Impl *)self->impl)->map, visit, arg) < 0) {
                    PyMutex_Unlock(&self->mutex);
                    return -1;
                }
                break;

            case MAP_KIND_I64_OBJ:
                if (traverse_map_impl<int64_t, PyObject *>(((MapI64ObjImpl *)self->impl)->map, visit, arg) < 0) {
                    PyMutex_Unlock(&self->mutex);
                    return -1;
                }
                break;

            case MAP_KIND_OBJ_I64:
                if (traverse_map_impl<PyObject *, int64_t>(((MapObjI64Impl *)self->impl)->map, visit, arg) < 0) {
                    PyMutex_Unlock(&self->mutex);
                    return -1;
                }
                break;

            case MAP_KIND_OBJ_OBJ:
                if (traverse_map_impl<PyObject *, PyObject *>(((MapObjObjImpl *)self->impl)->map, visit, arg) < 0) {
                    PyMutex_Unlock(&self->mutex);
                    return -1;
                }
                break;

            default:
                PyMutex_Unlock(&self->mutex);
                PyErr_SetString(PyExc_RuntimeError, "invalid map kind");
                return -1;
        }
    }

    PyMutex_Unlock(&self->mutex);

    Py_VISIT(Py_TYPE((PyObject *)self));
    return 0;
}

static int map_clear(BaseMapObject *self)
{
    std::vector<PyObject *> refs;

    PyMutex_Lock(&self->mutex);

    if (self->impl != nullptr) {
        switch (self->kind) {
            case MAP_KIND_I64_I64:
                ((MapI64I64Impl *)self->impl)->map.clear();
                break;

            case MAP_KIND_I64_OBJ:
                detach_map_impl_refs<int64_t, PyObject *>(((MapI64ObjImpl *)self->impl)->map, refs);
                break;

            case MAP_KIND_OBJ_I64:
                detach_map_impl_refs<PyObject *, int64_t>(((MapObjI64Impl *)self->impl)->map, refs);
                break;

            case MAP_KIND_OBJ_OBJ:
                detach_map_impl_refs<PyObject *, PyObject *>(((MapObjObjImpl *)self->impl)->map, refs);
                break;

            default:
                PyMutex_Unlock(&self->mutex);
                PyErr_SetString(PyExc_RuntimeError, "invalid map kind");
                return -1;
        }
    }

    self->version++;

    PyMutex_Unlock(&self->mutex);

    for (PyObject *obj : refs) {
        Py_DECREF(obj);
    }

    return 0;
}

static void map_dealloc(BaseMapObject *self)
{
    PyObject_GC_UnTrack(self);

    if (map_clear(self) < 0) {
        PyErr_Clear();
    }

    if (self->impl != nullptr) {
        switch (self->kind) {
            case MAP_KIND_I64_I64:
                delete (MapI64I64Impl *)self->impl;
                break;
            case MAP_KIND_I64_OBJ:
                delete (MapI64ObjImpl *)self->impl;
                break;
            case MAP_KIND_OBJ_I64:
                delete (MapObjI64Impl *)self->impl;
                break;
            case MAP_KIND_OBJ_OBJ:
                delete (MapObjObjImpl *)self->impl;
                break;
            default:
                break;
        }
        self->impl = nullptr;
    }

    Py_TYPE(self)->tp_free((PyObject *)self);
}


static void *new_map_impl(map_kind kind)
{
    switch (kind) {
        case MAP_KIND_I64_I64:
            return new (std::nothrow) MapI64I64Impl();
        case MAP_KIND_I64_OBJ:
            return new (std::nothrow) MapI64ObjImpl();
        case MAP_KIND_OBJ_I64:
            return new (std::nothrow) MapObjI64Impl();
        case MAP_KIND_OBJ_OBJ:
            return new (std::nothrow) MapObjObjImpl();
        default:
            PyErr_SetString(PyExc_RuntimeError, "invalid map kind");
            return nullptr;
    }
}

static PyObject *map_new_common(PyTypeObject *type, map_kind kind)
{
    BaseMapObject *self = (BaseMapObject *)type->tp_alloc(type, 0);
    if (self == nullptr) {
        return nullptr;
    }

    std::memset(&self->mutex, 0, sizeof(self->mutex));
    self->version = 0;
    self->kind = kind;
    self->impl = new_map_impl(kind);
    if (self->impl == nullptr) {
        Py_DECREF(self);
        if (!PyErr_Occurred()) {
            PyErr_NoMemory();
        }
        return nullptr;
    }

    return (PyObject *)self;
}

static PyObject *MapI64I64_new(PyTypeObject *type, PyObject *, PyObject *)
{
    return map_new_common(type, MAP_KIND_I64_I64);
}

static PyObject *MapI64Obj_new(PyTypeObject *type, PyObject *, PyObject *)
{
    return map_new_common(type, MAP_KIND_I64_OBJ);
}

static PyObject *MapObjI64_new(PyTypeObject *type, PyObject *, PyObject *)
{
    return map_new_common(type, MAP_KIND_OBJ_I64);
}

static PyObject *MapObjObj_new(PyTypeObject *type, PyObject *, PyObject *)
{
    return map_new_common(type, MAP_KIND_OBJ_OBJ);
}


static int map_contains(BaseMapObject *self, PyObject *key)
{
    switch (self->kind) {
        case MAP_KIND_I64_I64: {
            int64_t k;
            if (py_to_i64(key, &k) < 0) {
                return -1;
            }

            PyMutex_Lock(&self->mutex);
            int ret = ((MapI64I64Impl *)self->impl)->map.find(k) != ((MapI64I64Impl *)self->impl)->map.end();
            PyMutex_Unlock(&self->mutex);
            return ret;
        }

        case MAP_KIND_I64_OBJ: {
            int64_t k;
            if (py_to_i64(key, &k) < 0) {
                return -1;
            }

            PyMutex_Lock(&self->mutex);
            int ret = ((MapI64ObjImpl *)self->impl)->map.find(k) != ((MapI64ObjImpl *)self->impl)->map.end();
            PyMutex_Unlock(&self->mutex);
            return ret;
        }

        case MAP_KIND_OBJ_I64: {
            while (true) {
                PyMutex_Lock(&self->mutex);
                uint64_t current_version = self->version;
                CompareContextGuard guard(self, current_version);
                try {
                    int ret = ((MapObjI64Impl *)self->impl)->map.find(key) != ((MapObjI64Impl *)self->impl)->map.end();
                    PyMutex_Unlock(&self->mutex);
                    return ret;
                } catch (const PyMapMutatedError &) {
                    PyMutex_Unlock(&self->mutex);
                    continue;
                } catch (const PyCompareError &) {
                    PyMutex_Unlock(&self->mutex);
                    return -1;
                }
            }
        }

        case MAP_KIND_OBJ_OBJ: {
            while (true) {
                PyMutex_Lock(&self->mutex);
                uint64_t current_version = self->version;
                CompareContextGuard guard(self, current_version);
                try {
                    int ret = ((MapObjObjImpl *)self->impl)->map.find(key) != ((MapObjObjImpl *)self->impl)->map.end();
                    PyMutex_Unlock(&self->mutex);
                    return ret;
                } catch (const PyMapMutatedError &) {
                    PyMutex_Unlock(&self->mutex);
                    continue;
                } catch (const PyCompareError &) {
                    PyMutex_Unlock(&self->mutex);
                    return -1;
                }
            }
        }

        default:
            PyErr_SetString(PyExc_RuntimeError, "invalid map kind");
            return -1;
    }
}


static PyObject *map_subscript(BaseMapObject *self, PyObject *key)
{
    switch (self->kind) {
        case MAP_KIND_I64_I64: {
            int64_t k;
            if (py_to_i64(key, &k) < 0) {
                return nullptr;
            }

            PyObject *ret = nullptr;
            PyMutex_Lock(&self->mutex);
            auto &map = ((MapI64I64Impl *)self->impl)->map;
            auto it = map.find(k);
            if (it == map.end()) {
                PyMutex_Unlock(&self->mutex);
                PyErr_SetObject(PyExc_KeyError, key);
                return nullptr;
            }
            ret = i64_to_py(it->second);
            PyMutex_Unlock(&self->mutex);
            return ret;
        }

        case MAP_KIND_I64_OBJ: {
            int64_t k;
            if (py_to_i64(key, &k) < 0) {
                return nullptr;
            }

            PyObject *ret = nullptr;
            PyMutex_Lock(&self->mutex);
            auto &map = ((MapI64ObjImpl *)self->impl)->map;
            auto it = map.find(k);
            if (it == map.end()) {
                PyMutex_Unlock(&self->mutex);
                PyErr_SetObject(PyExc_KeyError, key);
                return nullptr;
            }
            ret = obj_to_py(it->second);
            PyMutex_Unlock(&self->mutex);
            return ret;
        }

        case MAP_KIND_OBJ_I64: {
            while (true) {
                PyMutex_Lock(&self->mutex);
                uint64_t current_version = self->version;
                CompareContextGuard guard(self, current_version);
                try {
                    auto &map = ((MapObjI64Impl *)self->impl)->map;
                    auto it = map.find(key);
                    if (it == map.end()) {
                        PyMutex_Unlock(&self->mutex);
                        PyErr_SetObject(PyExc_KeyError, key);
                        return nullptr;
                    }
                    PyObject *ret = i64_to_py(it->second);
                    PyMutex_Unlock(&self->mutex);
                    return ret;
                } catch (const PyMapMutatedError &) {
                    PyMutex_Unlock(&self->mutex);
                    continue;
                } catch (const PyCompareError &) {
                    PyMutex_Unlock(&self->mutex);
                    return nullptr;
                }
            }
        }

        case MAP_KIND_OBJ_OBJ: {
            while (true) {
                PyMutex_Lock(&self->mutex);
                uint64_t current_version = self->version;
                CompareContextGuard guard(self, current_version);
                try {
                    auto &map = ((MapObjObjImpl *)self->impl)->map;
                    auto it = map.find(key);
                    if (it == map.end()) {
                        PyMutex_Unlock(&self->mutex);
                        PyErr_SetObject(PyExc_KeyError, key);
                        return nullptr;
                    }
                    PyObject *ret = obj_to_py(it->second);
                    PyMutex_Unlock(&self->mutex);
                    return ret;
                } catch (const PyMapMutatedError &) {
                    PyMutex_Unlock(&self->mutex);
                    continue;
                } catch (const PyCompareError &) {
                    PyMutex_Unlock(&self->mutex);
                    return nullptr;
                }
            }
        }

        default:
            PyErr_SetString(PyExc_RuntimeError, "invalid map kind");
            return nullptr;
    }
}


static int map_ass_subscript(BaseMapObject *self, PyObject *key, PyObject *value)
{
    if (value == nullptr) {
        switch (self->kind) {
            case MAP_KIND_I64_I64: {
                int64_t k;
                if (py_to_i64(key, &k) < 0) {
                    return -1;
                }

                PyMutex_Lock(&self->mutex);
                auto &map = ((MapI64I64Impl *)self->impl)->map;
                auto it = map.find(k);
                if (it == map.end()) {
                    PyMutex_Unlock(&self->mutex);
                    PyErr_SetObject(PyExc_KeyError, key);
                    return -1;
                }
                map.erase(it);
                self->version++;
                PyMutex_Unlock(&self->mutex);
                return 0;
            }

            case MAP_KIND_I64_OBJ: {
                int64_t k;
                if (py_to_i64(key, &k) < 0) {
                    return -1;
                }

                PyObject *old = nullptr;
                PyMutex_Lock(&self->mutex);
                auto &map = ((MapI64ObjImpl *)self->impl)->map;
                auto it = map.find(k);
                if (it == map.end()) {
                    PyMutex_Unlock(&self->mutex);
                    PyErr_SetObject(PyExc_KeyError, key);
                    return -1;
                }
                old = it->second;
                map.erase(it);
                self->version++;
                PyMutex_Unlock(&self->mutex);
                Py_DECREF(old);
                return 0;
            }

            case MAP_KIND_OBJ_I64: {
                while (true) {
                    PyMutex_Lock(&self->mutex);
                    uint64_t current_version = self->version;
                    CompareContextGuard guard(self, current_version);
                    try {
                        auto &map = ((MapObjI64Impl *)self->impl)->map;
                        auto it = map.find(key);
                        if (it == map.end()) {
                            PyMutex_Unlock(&self->mutex);
                            PyErr_SetObject(PyExc_KeyError, key);
                            return -1;
                        }
                        PyObject *old_key = it->first;
                        map.erase(it);
                        self->version++;
                        PyMutex_Unlock(&self->mutex);
                        Py_DECREF(old_key);
                        return 0;
                    } catch (const PyMapMutatedError &) {
                        PyMutex_Unlock(&self->mutex);
                        continue;
                    } catch (const PyCompareError &) {
                        PyMutex_Unlock(&self->mutex);
                        return -1;
                    }
                }
            }

            case MAP_KIND_OBJ_OBJ: {
                while (true) {
                    PyMutex_Lock(&self->mutex);
                    uint64_t current_version = self->version;
                    CompareContextGuard guard(self, current_version);
                    try {
                        auto &map = ((MapObjObjImpl *)self->impl)->map;
                        auto it = map.find(key);
                        if (it == map.end()) {
                            PyMutex_Unlock(&self->mutex);
                            PyErr_SetObject(PyExc_KeyError, key);
                            return -1;
                        }
                        PyObject *old_key = it->first;
                        PyObject *old_value = it->second;
                        map.erase(it);
                        self->version++;
                        PyMutex_Unlock(&self->mutex);
                        Py_DECREF(old_key);
                        Py_DECREF(old_value);
                        return 0;
                    } catch (const PyMapMutatedError &) {
                        PyMutex_Unlock(&self->mutex);
                        continue;
                    } catch (const PyCompareError &) {
                        PyMutex_Unlock(&self->mutex);
                        return -1;
                    }
                }
            }

            default:
                PyErr_SetString(PyExc_RuntimeError, "invalid map kind");
                return -1;
        }
    }

    switch (self->kind) {
        case MAP_KIND_I64_I64: {
            int64_t k;
            int64_t v;
            if (py_to_i64(key, &k) < 0 || py_to_i64(value, &v) < 0) {
                return -1;
            }

            PyMutex_Lock(&self->mutex);
            try {
                auto &map = ((MapI64I64Impl *)self->impl)->map;
                map[k] = v;
                self->version++;
                PyMutex_Unlock(&self->mutex);
                return 0;
            } catch (const std::bad_alloc &) {
                PyMutex_Unlock(&self->mutex);
                PyErr_NoMemory();
                return -1;
            }
        }

        case MAP_KIND_I64_OBJ: {
            int64_t k;
            PyObject *v = nullptr;
            if (py_to_i64(key, &k) < 0 || py_to_obj_owned(value, &v) < 0) {
                return -1;
            }

            PyObject *old = nullptr;
            PyMutex_Lock(&self->mutex);
            try {
                auto &map = ((MapI64ObjImpl *)self->impl)->map;
                auto it = map.find(k);
                if (it != map.end()) {
                    old = it->second;
                    it->second = v;
                } else {
                    map.emplace(k, v);
                }
                self->version++;
                PyMutex_Unlock(&self->mutex);
                Py_XDECREF(old);
                return 0;
            } catch (const std::bad_alloc &) {
                PyMutex_Unlock(&self->mutex);
                Py_DECREF(v);
                PyErr_NoMemory();
                return -1;
            }
        }

        case MAP_KIND_OBJ_I64: {
            PyObject *k = nullptr;
            int64_t v;
            if (py_to_obj_owned(key, &k) < 0) {
                return -1;
            }
            if (py_to_i64(value, &v) < 0) {
                Py_DECREF(k);
                return -1;
            }

            while (true) {
                PyMutex_Lock(&self->mutex);
                uint64_t current_version = self->version;
                CompareContextGuard guard(self, current_version);

                try {
                    auto &map = ((MapObjI64Impl *)self->impl)->map;
                    auto it = map.find(k);
                    PyObject *drop_key = nullptr;

                    if (it != map.end()) {
                        drop_key = k; // DEFERRED DECREF
                        it->second = v;
                    } else {
                        map.emplace(k, v);
                    }
                    self->version++;
                    PyMutex_Unlock(&self->mutex);

                    Py_XDECREF(drop_key);
                    return 0;
                } catch (const PyMapMutatedError &) {
                    PyMutex_Unlock(&self->mutex);
                    continue;
                } catch (const PyCompareError &) {
                    PyMutex_Unlock(&self->mutex);
                    Py_DECREF(k);
                    return -1;
                } catch (const std::bad_alloc &) {
                    PyMutex_Unlock(&self->mutex);
                    Py_DECREF(k);
                    PyErr_NoMemory();
                    return -1;
                }
            }
        }

        case MAP_KIND_OBJ_OBJ: {
            PyObject *k = nullptr;
            PyObject *v = nullptr;
            if (py_to_obj_owned(key, &k) < 0 || py_to_obj_owned(value, &v) < 0) {
                Py_XDECREF(k);
                return -1;
            }

            while (true) {
                PyMutex_Lock(&self->mutex);
                uint64_t current_version = self->version;
                CompareContextGuard guard(self, current_version);

                try {
                    auto &map = ((MapObjObjImpl *)self->impl)->map;
                    auto it = map.find(k);
                    PyObject *drop_value = nullptr;
                    PyObject *drop_key = nullptr;

                    if (it != map.end()) {
                        drop_value = it->second;
                        drop_key = k; // DEFERRED DECREF
                        it->second = v;
                    } else {
                        map.emplace(k, v);
                    }
                    self->version++;
                    PyMutex_Unlock(&self->mutex);

                    Py_XDECREF(drop_value);
                    Py_XDECREF(drop_key);
                    return 0;
                } catch (const PyMapMutatedError &) {
                    PyMutex_Unlock(&self->mutex);
                    continue;
                } catch (const PyCompareError &) {
                    PyMutex_Unlock(&self->mutex);
                    Py_DECREF(k);
                    Py_DECREF(v);
                    return -1;
                } catch (const std::bad_alloc &) {
                    PyMutex_Unlock(&self->mutex);
                    Py_DECREF(k);
                    Py_DECREF(v);
                    PyErr_NoMemory();
                    return -1;
                }
            }
        }

        default:
            PyErr_SetString(PyExc_RuntimeError, "invalid map kind");
            return -1;
    }
}


static int map_add_pair(BaseMapObject *self, PyObject *pair)
{
    PyObject *fast = PySequence_Fast(pair, "expected a 2-item iterable");
    if (fast == nullptr) {
        return -1;
    }

    if (PySequence_Fast_GET_SIZE(fast) != 2) {
        Py_DECREF(fast);
        PyErr_SetString(PyExc_ValueError, "expected a 2-item iterable");
        return -1;
    }

    PyObject *key = PySequence_Fast_GET_ITEM(fast, 0);
    PyObject *value = PySequence_Fast_GET_ITEM(fast, 1);
    int ret = map_ass_subscript(self, key, value);
    Py_DECREF(fast);
    return ret;
}

static int map_update_from_object(BaseMapObject *self, PyObject *arg)
{
    if (arg == nullptr || arg == Py_None) {
        return 0;
    }

    PyObject *items = nullptr;
    if (PyMapping_Check(arg)) {
        items = PyMapping_Items(arg);
        if (items == nullptr) {
            return -1;
        }
    } else {
        items = Py_NewRef(arg);
    }

    PyObject *it = PyObject_GetIter(items);
    Py_DECREF(items);
    if (it == nullptr) {
        return -1;
    }

    PyObject *item;
    while ((item = PyIter_Next(it)) != nullptr) {
        int rc = map_add_pair(self, item);
        Py_DECREF(item);
        if (rc < 0) {
            Py_DECREF(it);
            return -1;
        }
    }

    Py_DECREF(it);
    if (PyErr_Occurred()) {
        return -1;
    }

    return 0;
}

static int map_init(BaseMapObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *arg = Py_None;

    if (!PyArg_ParseTuple(args, "|O", &arg)) {
        return -1;
    }

    if (map_update_from_object(self, arg) < 0) {
        return -1;
    }

    if (kwargs != nullptr && PyDict_GET_SIZE(kwargs) != 0) {
        PyObject *items = PyMapping_Items(kwargs);
        if (items == nullptr) {
            return -1;
        }

        Py_ssize_t n = PyList_GET_SIZE(items);
        for (Py_ssize_t i = 0; i < n; ++i) {
            PyObject *item = PyList_GET_ITEM(items, i);
            if (map_add_pair(self, item) < 0) {
                Py_DECREF(items);
                return -1;
            }
        }

        Py_DECREF(items);
    }

    return 0;
}


static PyObject *map_clear_method(BaseMapObject *self, PyObject *)
{
    if (map_clear(self) < 0) {
        return nullptr;
    }
    Py_RETURN_NONE;
}


static PyObject *map_repr(BaseMapObject *self)
{
    Py_ssize_t n;
    PyMutex_Lock(&self->mutex);
    n = map_len_unlocked(self);
    PyMutex_Unlock(&self->mutex);
    if (n < 0) {
        return nullptr;
    }

    return PyUnicode_FromFormat("<%s len=%zd>", Py_TYPE(self)->tp_name, n);
}


struct I64I64IterState {
    MapI64I64Impl::map_type::iterator it;
    MapI64I64Impl::map_type::iterator end;
};

struct I64ObjIterState {
    MapI64ObjImpl::map_type::iterator it;
    MapI64ObjImpl::map_type::iterator end;
};

struct ObjI64IterState {
    MapObjI64Impl::map_type::iterator it;
    MapObjI64Impl::map_type::iterator end;
};

struct ObjObjIterState {
    MapObjObjImpl::map_type::iterator it;
    MapObjObjImpl::map_type::iterator end;
};

static void delete_iter_state(map_kind kind, void *state)
{
    if (state == nullptr) {
        return;
    }

    switch (kind) {
        case MAP_KIND_I64_I64:
            delete (I64I64IterState *)state;
            break;
        case MAP_KIND_I64_OBJ:
            delete (I64ObjIterState *)state;
            break;
        case MAP_KIND_OBJ_I64:
            delete (ObjI64IterState *)state;
            break;
        case MAP_KIND_OBJ_OBJ:
            delete (ObjObjIterState *)state;
            break;
        default:
            break;
    }
}


static int map_iter_traverse(MapIterObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->owner);
    Py_VISIT(Py_TYPE((PyObject *)self));
    return 0;
}

static int map_iter_clear(MapIterObject *self)
{
    if (self->owner != nullptr) {
        delete_iter_state(((BaseMapObject *)self->owner)->kind, self->state);
    }
    self->state = nullptr;
    Py_CLEAR(self->owner);
    return 0;
}

static void map_iter_dealloc(MapIterObject *self)
{
    PyObject_GC_UnTrack(self);
    map_iter_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *map_iter_self(PyObject *self)
{
    return Py_NewRef(self);
}


template <typename K, typename V>
static PyObject *build_iter_result(map_iter_kind kind, K const &k, V const &v)
{
    if (kind == MAP_ITER_KEYS) {
        if constexpr (std::is_same_v<K, int64_t>) {
            return i64_to_py(k);
        } else {
            return obj_to_py(k);
        }
    }

    if (kind == MAP_ITER_VALUES) {
        if constexpr (std::is_same_v<V, int64_t>) {
            return i64_to_py(v);
        } else {
            return obj_to_py(v);
        }
    }

    PyObject *pk;
    PyObject *pv;
    if constexpr (std::is_same_v<K, int64_t>) {
        pk = i64_to_py(k);
    } else {
        pk = obj_to_py(k);
    }
    if (pk == nullptr) {
        return nullptr;
    }

    if constexpr (std::is_same_v<V, int64_t>) {
        pv = i64_to_py(v);
    } else {
        pv = obj_to_py(v);
    }
    if (pv == nullptr) {
        Py_DECREF(pk);
        return nullptr;
    }

    PyObject *tup = PyTuple_New(2);
    if (tup == nullptr) {
        Py_DECREF(pk);
        Py_DECREF(pv);
        return nullptr;
    }

    PyTuple_SET_ITEM(tup, 0, pk);
    PyTuple_SET_ITEM(tup, 1, pv);
    return tup;
}

static PyObject *map_iter_next(MapIterObject *self)
{
    BaseMapObject *owner = (BaseMapObject *)self->owner;
    if (owner == nullptr) {
        return nullptr;
    }

    PyMutex_Lock(&owner->mutex);

    if (self->expected_version != owner->version) {
        PyMutex_Unlock(&owner->mutex);
        PyErr_SetString(PyExc_RuntimeError, "map mutated during iteration");
        return nullptr;
    }

    switch (owner->kind) {
        case MAP_KIND_I64_I64: {
            auto *state = (I64I64IterState *)self->state;
            if (state->it == state->end) {
                PyMutex_Unlock(&owner->mutex);
                return nullptr;
            }
            auto const &entry = *state->it;
            PyObject *ret = build_iter_result<int64_t, int64_t>(self->kind, entry.first, entry.second);
            ++state->it;
            PyMutex_Unlock(&owner->mutex);
            return ret;
        }

        case MAP_KIND_I64_OBJ: {
            auto *state = (I64ObjIterState *)self->state;
            if (state->it == state->end) {
                PyMutex_Unlock(&owner->mutex);
                return nullptr;
            }
            auto const &entry = *state->it;
            PyObject *ret = build_iter_result<int64_t, PyObject *>(self->kind, entry.first, entry.second);
            ++state->it;
            PyMutex_Unlock(&owner->mutex);
            return ret;
        }

        case MAP_KIND_OBJ_I64: {
            auto *state = (ObjI64IterState *)self->state;
            if (state->it == state->end) {
                PyMutex_Unlock(&owner->mutex);
                return nullptr;
            }
            auto const &entry = *state->it;
            PyObject *ret = build_iter_result<PyObject *, int64_t>(self->kind, entry.first, entry.second);
            ++state->it;
            PyMutex_Unlock(&owner->mutex);
            return ret;
        }

        case MAP_KIND_OBJ_OBJ: {
            auto *state = (ObjObjIterState *)self->state;
            if (state->it == state->end) {
                PyMutex_Unlock(&owner->mutex);
                return nullptr;
            }
            auto const &entry = *state->it;
            PyObject *ret = build_iter_result<PyObject *, PyObject *>(self->kind, entry.first, entry.second);
            ++state->it;
            PyMutex_Unlock(&owner->mutex);
            return ret;
        }

        default:
            PyMutex_Unlock(&owner->mutex);
            PyErr_SetString(PyExc_RuntimeError, "invalid map kind");
            return nullptr;
    }
}


static PyObject *map_make_iter(BaseMapObject *self, map_iter_kind kind)
{
    stl_state *state = get_stl_state_for_type(Py_TYPE(self));
    if (state == nullptr) {
        return nullptr;
    }

    MapIterObject *it = PyObject_GC_New(MapIterObject, state->MapIterType);
    if (it == nullptr) {
        return nullptr;
    }

    it->owner = Py_NewRef((PyObject *)self);
    it->expected_version = 0;
    it->kind = kind;
    it->state = nullptr;

    PyMutex_Lock(&self->mutex);
    it->expected_version = self->version;

    switch (self->kind) {
        case MAP_KIND_I64_I64: {
            auto *statep = new (std::nothrow) I64I64IterState{
                ((MapI64I64Impl *)self->impl)->map.begin(),
                ((MapI64I64Impl *)self->impl)->map.end(),
            };
            if (statep == nullptr) {
                PyMutex_Unlock(&self->mutex);
                Py_DECREF(it);
                PyErr_NoMemory();
                return nullptr;
            }
            it->state = statep;
            break;
        }

        case MAP_KIND_I64_OBJ: {
            auto *statep = new (std::nothrow) I64ObjIterState{
                ((MapI64ObjImpl *)self->impl)->map.begin(),
                ((MapI64ObjImpl *)self->impl)->map.end(),
            };
            if (statep == nullptr) {
                PyMutex_Unlock(&self->mutex);
                Py_DECREF(it);
                PyErr_NoMemory();
                return nullptr;
            }
            it->state = statep;
            break;
        }

        case MAP_KIND_OBJ_I64: {
            auto *statep = new (std::nothrow) ObjI64IterState{
                ((MapObjI64Impl *)self->impl)->map.begin(),
                ((MapObjI64Impl *)self->impl)->map.end(),
            };
            if (statep == nullptr) {
                PyMutex_Unlock(&self->mutex);
                Py_DECREF(it);
                PyErr_NoMemory();
                return nullptr;
            }
            it->state = statep;
            break;
        }

        case MAP_KIND_OBJ_OBJ: {
            auto *statep = new (std::nothrow) ObjObjIterState{
                ((MapObjObjImpl *)self->impl)->map.begin(),
                ((MapObjObjImpl *)self->impl)->map.end(),
            };
            if (statep == nullptr) {
                PyMutex_Unlock(&self->mutex);
                Py_DECREF(it);
                PyErr_NoMemory();
                return nullptr;
            }
            it->state = statep;
            break;
        }

        default:
            PyMutex_Unlock(&self->mutex);
            Py_DECREF(it);
            PyErr_SetString(PyExc_RuntimeError, "invalid map kind");
            return nullptr;
    }

    PyMutex_Unlock(&self->mutex);
    PyObject_GC_Track(it);
    return (PyObject *)it;
}

static PyObject *map_iter(BaseMapObject *self)
{
    return map_make_iter(self, MAP_ITER_KEYS);
}

static PyObject *map_itervalues(BaseMapObject *self, PyObject *)
{
    return map_make_iter(self, MAP_ITER_VALUES);
}

static PyObject *map_iteritems(BaseMapObject *self, PyObject *)
{
    return map_make_iter(self, MAP_ITER_ITEMS);
}


static PyMethodDef map_methods[] = {
    {"clear", (PyCFunction)map_clear_method, METH_NOARGS, "Remove all items."},
    {"itervalues", (PyCFunction)map_itervalues, METH_NOARGS, "Return a values iterator."},
    {"iteritems", (PyCFunction)map_iteritems, METH_NOARGS, "Return an items iterator."},
    {nullptr, nullptr, 0, nullptr},
};


static PyType_Slot MapIter_slots[] = {
    {Py_tp_dealloc, (void *)map_iter_dealloc},
    {Py_tp_traverse, (void *)map_iter_traverse},
    {Py_tp_clear, (void *)map_iter_clear},
    {Py_tp_iter, (void *)map_iter_self},
    {Py_tp_iternext, (void *)map_iter_next},
    {Py_tp_doc, (void *)"Map iterator"},
    {0, nullptr},
};

static PyType_Spec MapIter_spec = {
    .name = _MODULE_FULL_NAME ".MapIter",
    .basicsize = sizeof(MapIterObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = MapIter_slots,
};

static PyType_Slot MapI64I64_slots[] = {
    {Py_tp_dealloc, (void *)map_dealloc},
    {Py_tp_traverse, (void *)map_traverse},
    {Py_tp_clear, (void *)map_clear},
    {Py_tp_new, (void *)MapI64I64_new},
    {Py_tp_init, (void *)map_init},
    {Py_tp_methods, (void *)map_methods},
    {Py_mp_length, (void *)map_len},
    {Py_mp_subscript, (void *)map_subscript},
    {Py_mp_ass_subscript, (void *)map_ass_subscript},
    {Py_sq_contains, (void *)map_contains},
    {Py_tp_iter, (void *)map_iter},
    {Py_tp_repr, (void *)map_repr},
    {Py_tp_hash, (void *)PyObject_HashNotImplemented},
    {Py_tp_doc, (void *)"int64->int64 sorted map"},
    {0, nullptr},
};

static PyType_Slot MapI64Obj_slots[] = {
    {Py_tp_dealloc, (void *)map_dealloc},
    {Py_tp_traverse, (void *)map_traverse},
    {Py_tp_clear, (void *)map_clear},
    {Py_tp_new, (void *)MapI64Obj_new},
    {Py_tp_init, (void *)map_init},
    {Py_tp_methods, (void *)map_methods},
    {Py_mp_length, (void *)map_len},
    {Py_mp_subscript, (void *)map_subscript},
    {Py_mp_ass_subscript, (void *)map_ass_subscript},
    {Py_sq_contains, (void *)map_contains},
    {Py_tp_iter, (void *)map_iter},
    {Py_tp_repr, (void *)map_repr},
    {Py_tp_hash, (void *)PyObject_HashNotImplemented},
    {Py_tp_doc, (void *)"int64->object sorted map"},
    {0, nullptr},
};

static PyType_Slot MapObjI64_slots[] = {
    {Py_tp_dealloc, (void *)map_dealloc},
    {Py_tp_traverse, (void *)map_traverse},
    {Py_tp_clear, (void *)map_clear},
    {Py_tp_new, (void *)MapObjI64_new},
    {Py_tp_init, (void *)map_init},
    {Py_tp_methods, (void *)map_methods},
    {Py_mp_length, (void *)map_len},
    {Py_mp_subscript, (void *)map_subscript},
    {Py_mp_ass_subscript, (void *)map_ass_subscript},
    {Py_sq_contains, (void *)map_contains},
    {Py_tp_iter, (void *)map_iter},
    {Py_tp_repr, (void *)map_repr},
    {Py_tp_hash, (void *)PyObject_HashNotImplemented},
    {Py_tp_doc, (void *)"object->int64 sorted map"},
    {0, nullptr},
};

static PyType_Slot MapObjObj_slots[] = {
    {Py_tp_dealloc, (void *)map_dealloc},
    {Py_tp_traverse, (void *)map_traverse},
    {Py_tp_clear, (void *)map_clear},
    {Py_tp_new, (void *)MapObjObj_new},
    {Py_tp_init, (void *)map_init},
    {Py_tp_methods, (void *)map_methods},
    {Py_mp_length, (void *)map_len},
    {Py_mp_subscript, (void *)map_subscript},
    {Py_mp_ass_subscript, (void *)map_ass_subscript},
    {Py_sq_contains, (void *)map_contains},
    {Py_tp_iter, (void *)map_iter},
    {Py_tp_repr, (void *)map_repr},
    {Py_tp_hash, (void *)PyObject_HashNotImplemented},
    {Py_tp_doc, (void *)"object->object sorted map"},
    {0, nullptr},
};

static PyType_Spec MapI64I64_spec = {
    .name = _MODULE_FULL_NAME ".MapI64I64",
    .basicsize = sizeof(BaseMapObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE,
    .slots = MapI64I64_slots,
};

static PyType_Spec MapI64Obj_spec = {
    .name = _MODULE_FULL_NAME ".MapI64Obj",
    .basicsize = sizeof(BaseMapObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE,
    .slots = MapI64Obj_slots,
};

static PyType_Spec MapObjI64_spec = {
    .name = _MODULE_FULL_NAME ".MapObjI64",
    .basicsize = sizeof(BaseMapObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE,
    .slots = MapObjI64_slots,
};

static PyType_Spec MapObjObj_spec = {
    .name = _MODULE_FULL_NAME ".MapObjObj",
    .basicsize = sizeof(BaseMapObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE,
    .slots = MapObjObj_slots,
};


PyDoc_STRVAR(stl_doc, "Native STL-backed collection primitives for omlish.collections.stl");

static int stl_exec(PyObject *module)
{
    stl_state *state = get_stl_state(module);

    state->MapIterType = (PyTypeObject *)PyType_FromModuleAndSpec(module, &MapIter_spec, nullptr);
    if (state->MapIterType == nullptr) {
        return -1;
    }

    state->MapI64I64Type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &MapI64I64_spec, nullptr);
    if (state->MapI64I64Type == nullptr) {
        return -1;
    }

    state->MapI64ObjType = (PyTypeObject *)PyType_FromModuleAndSpec(module, &MapI64Obj_spec, nullptr);
    if (state->MapI64ObjType == nullptr) {
        return -1;
    }

    state->MapObjI64Type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &MapObjI64_spec, nullptr);
    if (state->MapObjI64Type == nullptr) {
        return -1;
    }

    state->MapObjObjType = (PyTypeObject *)PyType_FromModuleAndSpec(module, &MapObjObj_spec, nullptr);
    if (state->MapObjObjType == nullptr) {
        return -1;
    }

    if (PyModule_AddObjectRef(module, "MapIter", (PyObject *)state->MapIterType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(module, "MapI64I64", (PyObject *)state->MapI64I64Type) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(module, "MapI64Obj", (PyObject *)state->MapI64ObjType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(module, "MapObjI64", (PyObject *)state->MapObjI64Type) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(module, "MapObjObj", (PyObject *)state->MapObjObjType) < 0) {
        return -1;
    }

    return 0;
}

static int stl_traverse(PyObject *module, visitproc visit, void *arg)
{
    stl_state *state = get_stl_state(module);
    Py_VISIT(state->MapIterType);
    Py_VISIT(state->MapI64I64Type);
    Py_VISIT(state->MapI64ObjType);
    Py_VISIT(state->MapObjI64Type);
    Py_VISIT(state->MapObjObjType);
    return 0;
}

static int stl_clear(PyObject *module)
{
    stl_state *state = get_stl_state(module);
    Py_CLEAR(state->MapIterType);
    Py_CLEAR(state->MapI64I64Type);
    Py_CLEAR(state->MapI64ObjType);
    Py_CLEAR(state->MapObjI64Type);
    Py_CLEAR(state->MapObjObjType);
    return 0;
}

static void stl_free(void *module)
{
    stl_clear((PyObject *)module);
}

static PyMethodDef stl_methods[] = {
    {nullptr, nullptr, 0, nullptr},
};

static struct PyModuleDef_Slot stl_slots[] = {
    {Py_mod_exec, (void *)stl_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, nullptr},
};

static PyModuleDef stl_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = stl_doc,
    .m_size = sizeof(stl_state),
    .m_methods = stl_methods,
    .m_slots = stl_slots,
    .m_traverse = stl_traverse,
    .m_clear = stl_clear,
    .m_free = stl_free,
};


static PyModuleDef *stl_module_def(void)
{
    return &stl_module;
}

extern "C" {

PyMODINIT_FUNC PyInit__stl(void)
{
    return PyModuleDef_Init(&stl_module);
}

}
