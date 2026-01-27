// @omlish-cext
// @omlish-llm-author "claude-sonnet-4-5-20250929"
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <memory>
#include <unordered_map>
#include <variant>
#include <vector>

//

#define _MODULE_NAME "_collection"
#define _PACKAGE_NAME "omlish.typedvalues"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

typedef struct collection_state {
    PyObject *typed_value_type;
    PyObject *unique_typed_value_type;
    PyObject *duplicate_error_type;
} collection_state;

static inline collection_state * get_collection_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (collection_state *)state;
}

//

template<typename T = PyObject>
class PyRef {
    T* ptr_;
public:
    explicit PyRef(T* ptr = nullptr) : ptr_(ptr) {}
    ~PyRef() { Py_XDECREF(reinterpret_cast<PyObject*>(ptr_)); }

    // No copy
    PyRef(const PyRef&) = delete;
    PyRef& operator=(const PyRef&) = delete;

    // Move is OK
    PyRef(PyRef&& other) noexcept : ptr_(other.release()) {}
    PyRef& operator=(PyRef&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    void reset(T* ptr = nullptr) {
        PyObject* old = reinterpret_cast<PyObject*>(ptr_);
        ptr_ = ptr;
        Py_XDECREF(old);
    }

    T* get() const { return ptr_; }

    // Explicitly give up ownership
    [[nodiscard]] T* release() {
        T* p = ptr_;
        ptr_ = nullptr;
        return p;
    }

    explicit operator bool() const { return ptr_ != nullptr; }

    operator T*() const = delete;
};

//

template<typename F>
struct ScopeGuard {
    F cleanup;
    ~ScopeGuard() { cleanup(); }
};

template<typename F> ScopeGuard(F) -> ScopeGuard<F>;

//

PyDoc_STRVAR(init_typed_values_collection_doc,
"init_typed_values_collection(*tvs, override=False, check_type=None)\n"
"\n"
"Initialize a typed values collection.\n"
"\n"
"Returns a tuple of (tuple, dict, dict2) where:\n"
"- tuple: ordered sequence of typed values\n"
"- dict: mapping of type -> typed value or tuple of typed values\n"
"- dict2: extended dict including instance types for unique values");

static PyObject * init_typed_values_collection(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames)
{
    collection_state *state = get_collection_state(module);

    // Parse arguments
    bool override = false;
    PyObject *check_type = nullptr;

    // Handle keyword arguments
    Py_ssize_t nkwargs = kwnames ? PyTuple_GET_SIZE(kwnames) : 0;

    for (Py_ssize_t i = 0; i < nkwargs; i++) {
        PyObject *key = PyTuple_GET_ITEM(kwnames, i);
        PyObject *value = args[nargs + i];
        const char *key_str = PyUnicode_AsUTF8(key);

        if (key_str == nullptr) {
            return nullptr;
        }

        if (strcmp(key_str, "override") == 0) {
            int override_result = PyObject_IsTrue(value);
            if (override_result == -1) {
                return nullptr;
            }
            override = override_result;
        } else if (strcmp(key_str, "check_type") == 0) {
            check_type = value;
        } else {
            PyErr_Format(PyExc_TypeError, "unexpected keyword argument: %s", key_str);
            return nullptr;
        }
    }

    // If no positional arguments, return empty tuple and dicts
    if (nargs == 0) {
        PyRef empty_tuple(PyTuple_New(0));
        if (!empty_tuple) {
            return nullptr;
        }

        PyRef empty_dict(PyDict_New());
        if (!empty_dict) {
            return nullptr;
        }

        PyRef empty_dict2(PyDict_New());
        if (!empty_dict2) {
            return nullptr;
        }

        return PyTuple_Pack(3, empty_tuple.get(), empty_dict.get(), empty_dict2.get());
    }

    // Helper struct to track unique typed values during processing
    struct UniqueInfo {
        PyObject *unique_tv_cls;  // The unique class (borrowed from map key)
        PyObject *tv;             // The typed value (borrowed from args)
        size_t idx;               // Index in unique_lst when added
    };

    using TmpItem = std::variant<PyObject*, std::unique_ptr<UniqueInfo>>;

    // Temporary storage
    std::vector<TmpItem> tmp_lst;
    tmp_lst.reserve(nargs);

    // Map from unique type to list of typed values
    std::unordered_map<PyObject*, std::vector<PyObject*>> unique_dct;

    ScopeGuard keys_cleaner{[&unique_dct] {
        for (auto const& [key, _] : unique_dct) {
            Py_DECREF(key);
        }
    }};

    // Process each typed value
    for (Py_ssize_t i = 0; i < nargs; i++) {
        PyObject *tv = args[i];

        // Check type if requested
        if (check_type != nullptr && check_type != Py_None) {
            int result = PyObject_IsInstance(tv, check_type);
            if (result == -1) {
                return nullptr;
            }
            if (!result) {
                PyErr_SetObject(PyExc_TypeError, tv);
                return nullptr;
            }
        }

        // Check if it's a UniqueTypedValue
        int is_unique = PyObject_IsInstance(tv, state->unique_typed_value_type);
        if (is_unique == -1) {
            return nullptr;
        }

        if (is_unique) {
            // Get the _unique_typed_value_cls attribute
            PyRef unique_tv_cls(PyObject_GetAttrString(tv, "_unique_typed_value_cls"));
            if (!unique_tv_cls) {
                return nullptr;
            }

            // Check for duplicates if not override
            if (!override) {
                auto it = unique_dct.find(unique_tv_cls.get());
                if (it != unique_dct.end() && !it->second.empty()) {
                    // Duplicate found - raise error
                    PyObject *old_tv = it->second[0];

                    // Create DuplicateUniqueTypedValueError
                    PyRef error(PyObject_CallFunction(
                        state->duplicate_error_type,
                        "OOO",
                        unique_tv_cls.get(),
                        tv,
                        old_tv
                    ));

                    if (!error) {
                        return nullptr;
                    }

                    PyErr_SetObject(state->duplicate_error_type, error.get());
                    return nullptr;
                }
            }

            // Add to unique_dct
            // Use insert to avoid reference leak: if key already exists, we need to decref the new reference
            auto insertion = unique_dct.insert({unique_tv_cls.get(), std::vector<PyObject*>()});
            if (!insertion.second) {
                // Key already existed, PyRef will automatically decref
            } else {
                // Key was inserted, transfer ownership to map using .release()
                (void)unique_tv_cls.release();
            }
            std::vector<PyObject*> &unique_lst = insertion.first->second;
            unique_lst.push_back(tv);

            // Add to tmp_lst using make_unique
            tmp_lst.emplace_back(std::make_unique<UniqueInfo>(UniqueInfo{
                insertion.first->first,  // Borrowed from map
                tv,
                unique_lst.size()
            }));

        } else {
            // Check if it's a TypedValue
            int is_typed_value = PyObject_IsInstance(tv, state->typed_value_type);
            if (is_typed_value == -1) {
                return nullptr;
            }

            if (!is_typed_value) {
                PyErr_SetObject(PyExc_TypeError, tv);
                return nullptr;
            }

            // Non-unique typed value
            tmp_lst.emplace_back(tv);
        }
    }

    // Build output structures
    PyRef lst(PyList_New(0));
    if (!lst) {
        return nullptr;
    }

    PyRef tmp_dct(PyDict_New());
    if (!tmp_dct) {
        return nullptr;
    }

    // Process tmp_lst to build output list and tmp_dct
    for (auto &item : tmp_lst) {
        // Check if item holds unique_ptr<UniqueInfo>
        if (auto *uniq_ptr_wrapper = std::get_if<std::unique_ptr<UniqueInfo>>(&item)) {
            UniqueInfo *info = uniq_ptr_wrapper->get();

            // Look up the vector now (after all insertions are done, no more rehashing)
            auto it = unique_dct.find(info->unique_tv_cls);
            assert(it != unique_dct.end());

            // Last-in-wins: only include if this is the last one
            if (info->idx == it->second.size()) {
                // Add to output list
                if (PyList_Append(lst.get(), info->tv) == -1) {
                    return nullptr;
                }

                // Add to tmp_dct (scalar value for unique types)
                if (PyDict_SetItem(tmp_dct.get(), info->unique_tv_cls, info->tv) == -1) {
                    return nullptr;
                }
            }
        } else {
            // Must be PyObject*
            PyObject *tv = std::get<PyObject*>(item);

            // Add to output list
            if (PyList_Append(lst.get(), tv) == -1) {
                return nullptr;
            }

            // Add to tmp_dct (accumulating list for non-unique types)
            PyObject *tv_type = (PyObject *)Py_TYPE(tv);
            PyObject *existing = PyDict_GetItem(tmp_dct.get(), tv_type);  // Borrowed reference

            if (existing == nullptr) {
                // Check if an error occurred during lookup
                if (PyErr_Occurred()) {
                    return nullptr;
                }

                // Create new list
                PyRef new_list(PyList_New(0));
                if (!new_list) {
                    return nullptr;
                }

                if (PyList_Append(new_list.get(), tv) == -1) {
                    return nullptr;
                }

                if (PyDict_SetItem(tmp_dct.get(), tv_type, new_list.get()) == -1) {
                    return nullptr;
                }
            } else {
                // Append to existing list
                if (PyList_Append(existing, tv) == -1) {
                    return nullptr;
                }
            }
        }
    }

    // Convert list to tuple
    PyRef result_tuple(PyList_AsTuple(lst.get()));
    if (!result_tuple) {
        return nullptr;
    }

    // Build dct: convert lists to tuples
    PyRef dct(PyDict_New());
    if (!dct) {
        return nullptr;
    }

    PyObject *key, *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(tmp_dct.get(), &pos, &key, &value)) {
        if (PyList_Check(value)) {
            PyRef tuple_value(PyList_AsTuple(value));
            if (!tuple_value) {
                return nullptr;
            }

            if (PyDict_SetItem(dct.get(), key, tuple_value.get()) == -1) {
                return nullptr;
            }
        } else {
            // Scalar value (unique type)
            if (PyDict_SetItem(dct.get(), key, value) == -1) {
                return nullptr;
            }
        }
    }

    // Build dct2: dct + unique values keyed by instance type
    PyRef dct2(PyDict_Copy(dct.get()));
    if (!dct2) {
        return nullptr;
    }

    // Add unique values by their instance type
    pos = 0;
    while (PyDict_Next(dct.get(), &pos, &key, &value)) {
        // Check if value is a UniqueTypedValue (not a tuple)
        if (!PyTuple_Check(value)) {
            int is_unique = PyObject_IsInstance(value, state->unique_typed_value_type);
            if (is_unique == -1) {
                return nullptr;
            }

            if (is_unique) {
                PyObject *value_type = (PyObject *)Py_TYPE(value);
                if (PyDict_SetItem(dct2.get(), value_type, value) == -1) {
                    return nullptr;
                }
            }
        }
    }

    // Build final result
    return PyTuple_Pack(3, result_tuple.get(), dct.get(), dct2.get());
}

//

PyDoc_STRVAR(collection_doc, "Native C++ implementations for omlish.typedvalues.collection");

static int collection_exec(PyObject *module)
{
    collection_state *state = get_collection_state(module);

    // Import TypedValue
    PyObject *values_module = PyImport_ImportModule("omlish.typedvalues.values");
    if (values_module == nullptr) {
        return -1;
    }

    state->typed_value_type = PyObject_GetAttrString(values_module, "TypedValue");
    if (state->typed_value_type == nullptr) {
        Py_DECREF(values_module);
        return -1;
    }

    state->unique_typed_value_type = PyObject_GetAttrString(values_module, "UniqueTypedValue");
    Py_DECREF(values_module);
    if (state->unique_typed_value_type == nullptr) {
        return -1;
    }

    // Import DuplicateUniqueTypedValueError
    PyObject *collection_module = PyImport_ImportModule("omlish.typedvalues.collection");
    if (collection_module == nullptr) {
        return -1;
    }

    state->duplicate_error_type = PyObject_GetAttrString(collection_module, "DuplicateUniqueTypedValueError");
    Py_DECREF(collection_module);
    if (state->duplicate_error_type == nullptr) {
        return -1;
    }

    return 0;
}

static int collection_traverse(PyObject *module, visitproc visit, void *arg)
{
    collection_state *state = get_collection_state(module);
    Py_VISIT(state->typed_value_type);
    Py_VISIT(state->unique_typed_value_type);
    Py_VISIT(state->duplicate_error_type);
    return 0;
}

static int collection_clear(PyObject *module)
{
    collection_state *state = get_collection_state(module);
    Py_CLEAR(state->typed_value_type);
    Py_CLEAR(state->unique_typed_value_type);
    Py_CLEAR(state->duplicate_error_type);
    return 0;
}

static void collection_free(void *module)
{
    collection_clear((PyObject *)module);
}

static PyMethodDef collection_methods[] = {
    {"init_typed_values_collection", (PyCFunction)(void(*)(void))init_typed_values_collection, METH_FASTCALL | METH_KEYWORDS, init_typed_values_collection_doc},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot collection_slots[] = {
    {Py_mod_exec, (void *) collection_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, NULL}
};

static struct PyModuleDef collection_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = collection_doc,
    .m_size = sizeof(collection_state),
    .m_methods = collection_methods,
    .m_slots = collection_slots,
    .m_traverse = collection_traverse,
    .m_clear = collection_clear,
    .m_free = collection_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__collection(void)
{
    return PyModuleDef_Init(&collection_module);
}

}