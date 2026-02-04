// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

//

#define _MODULE_NAME "_methods"
#define _PACKAGE_NAME "omlish.dispatch"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

typedef struct {
    PyTypeObject *MethodDispatchFuncType;
} methods_state;

static inline methods_state * get_methods_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (methods_state *)state;
}

//

typedef struct {
    PyObject_HEAD
    PyObject *dispatch_func;
    PyObject *base_func;
    PyObject *func_name;
    PyObject *dict;
} MethodDispatchFunc;

static int MethodDispatchFunc_traverse(MethodDispatchFunc *self, visitproc visit, void *arg)
{
    Py_VISIT(self->dispatch_func);
    Py_VISIT(self->base_func);
    Py_VISIT(self->func_name);
    Py_VISIT(self->dict);
    return 0;
}

static int MethodDispatchFunc_clear(MethodDispatchFunc *self)
{
    Py_CLEAR(self->dispatch_func);
    Py_CLEAR(self->base_func);
    Py_CLEAR(self->func_name);
    Py_CLEAR(self->dict);
    return 0;
}

static void MethodDispatchFunc_dealloc(MethodDispatchFunc *self)
{
    PyObject_GC_UnTrack(self);
    MethodDispatchFunc_clear(self);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject * MethodDispatchFunc_call(MethodDispatchFunc *self, PyObject *args, PyObject *kwargs)
{
    // This is the unbound call - args[0] should be the instance (self)
    // args[1:] are the actual method arguments

    Py_ssize_t nargs = PyTuple_GET_SIZE(args);
    if (nargs < 2) {
        PyErr_Format(
            PyExc_TypeError,
            "%U requires at least 1 positional argument",
            self->func_name
        );
        return nullptr;
    }

    // Get the instance (first positional arg - the 'self')
    PyObject *instance = PyTuple_GET_ITEM(args, 0);  // borrowed reference

    // Get type of first method arg directly: Py_TYPE(args[1])
    PyObject *first_method_arg = PyTuple_GET_ITEM(args, 1);  // borrowed reference
    PyTypeObject *first_arg_type = Py_TYPE(first_method_arg);

    // Call dispatch(type_(method_args[0]))
    PyObject *impl_att = PyObject_CallOneArg(self->dispatch_func, (PyObject *)first_arg_type);
    if (impl_att == nullptr) {
        return nullptr;
    }

    PyObject *result = nullptr;

    // Check if impl_att is not None
    if (impl_att != Py_None) {
        PyObject *impl_method = PyObject_GetAttr(instance, impl_att);
        Py_DECREF(impl_att);

        if (impl_method == nullptr) {
            return nullptr;
        }

        // Optimize for common case of single argument with no kwargs
        Py_ssize_t method_nargs = nargs - 1;
        if (method_nargs == 1 && (kwargs == nullptr || PyDict_GET_SIZE(kwargs) == 0)) {
            // Fast path for single argument, no kwargs
            result = PyObject_CallOneArg(impl_method, PyTuple_GET_ITEM(args, 1));
            Py_DECREF(impl_method);
        } else {
            // Build method_args tuple (args[1:])
            PyObject *method_args = PyTuple_New(method_nargs);
            if (method_args == nullptr) {
                Py_DECREF(impl_method);
                return nullptr;
            }

            for (Py_ssize_t i = 0; i < method_nargs; i++) {
                PyObject *item = PyTuple_GET_ITEM(args, i + 1);
                Py_INCREF(item);
                PyTuple_SET_ITEM(method_args, i, item);
            }

            // Call impl_method(*method_args, **kwargs)
            result = PyObject_Call(impl_method, method_args, kwargs);
            Py_DECREF(impl_method);
            Py_DECREF(method_args);
        }

    } else {
        Py_DECREF(impl_att);

        // base_func.__get__(instance)
        PyObject *get = PyObject_GetAttrString(self->base_func, "__get__");  // new ref or NULL
        if (get == nullptr) {
            return nullptr;
        }

        PyObject *owner = (PyObject *)Py_TYPE(instance);  // borrowed
        PyObject *bound_func = PyObject_CallFunctionObjArgs(get, instance, owner, NULL);
        Py_DECREF(get);

        if (bound_func == nullptr) {
            return nullptr;
        }

        // Optimize for common case of single argument with no kwargs
        Py_ssize_t method_nargs = nargs - 1;
        if (method_nargs == 1 && (kwargs == nullptr || PyDict_GET_SIZE(kwargs) == 0)) {
            // Fast path for single argument, no kwargs
            result = PyObject_CallOneArg(bound_func, PyTuple_GET_ITEM(args, 1));
            Py_DECREF(bound_func);
        } else {
            // Build method_args tuple (args[1:])
            PyObject *method_args = PyTuple_New(method_nargs);
            if (method_args == nullptr) {
                Py_DECREF(bound_func);
                return nullptr;
            }

            for (Py_ssize_t i = 0; i < method_nargs; i++) {
                PyObject *item = PyTuple_GET_ITEM(args, i + 1);
                Py_INCREF(item);
                PyTuple_SET_ITEM(method_args, i, item);
            }

            // Call bound_func(*method_args, **kwargs)
            result = PyObject_Call(bound_func, method_args, kwargs);
            Py_DECREF(bound_func);
            Py_DECREF(method_args);
        }
    }

    return result;
}

static PyObject * MethodDispatchFunc_get(MethodDispatchFunc *self, PyObject *instance, PyObject *owner)
{
    // Implement descriptor protocol for binding
    if (instance == Py_None || instance == nullptr) {
        // Unbound access - return self
        Py_INCREF(self);
        return (PyObject *)self;
    }

    // Bound access - return a bound method
    return PyMethod_New((PyObject *)self, instance);
}

static PyObject * MethodDispatchFunc_get_dict(MethodDispatchFunc *self, void *closure)
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

static int MethodDispatchFunc_set_dict(MethodDispatchFunc *self, PyObject *value, void *closure)
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

static PyObject * MethodDispatchFunc_getattro(MethodDispatchFunc *self, PyObject *name)
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

static int MethodDispatchFunc_setattro(MethodDispatchFunc *self, PyObject *name, PyObject *value)
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

static PyGetSetDef MethodDispatchFunc_getsets[] = {
    {"__dict__", (getter)MethodDispatchFunc_get_dict, (setter)MethodDispatchFunc_set_dict, nullptr, nullptr},
    {nullptr}
};

static PyType_Slot MethodDispatchFunc_slots[] = {
    {Py_tp_dealloc, (void *)MethodDispatchFunc_dealloc},
    {Py_tp_call, (void *)MethodDispatchFunc_call},
    {Py_tp_descr_get, (void *)MethodDispatchFunc_get},
    {Py_tp_traverse, (void *)MethodDispatchFunc_traverse},
    {Py_tp_clear, (void *)MethodDispatchFunc_clear},
    {Py_tp_getattro, (void *)MethodDispatchFunc_getattro},
    {Py_tp_setattro, (void *)MethodDispatchFunc_setattro},
    {Py_tp_getset, MethodDispatchFunc_getsets},
    {Py_tp_doc, (void *)"Fast dispatch function for Method instances"},
    {0, nullptr}
};

static PyType_Spec MethodDispatchFunc_spec = {
    .name = _MODULE_FULL_NAME ".MethodDispatchFunc",
    .basicsize = sizeof(MethodDispatchFunc),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = MethodDispatchFunc_slots,
};

//

PyDoc_STRVAR(build_method_dispatch_func_doc,
"build_method_dispatch_func(dispatch_func, base_func, func_name)\n\
\n\
Create a fast dispatch function for Method instances.\n\
\n\
Args:\n\
    dispatch_func: The dispatcher's dispatch callable\n\
    base_func: The base function to call if no implementation is found\n\
    func_name: The name of the function (for error messages)\n\
\n\
Returns:\n\
    A callable that performs method dispatch");

static PyObject * build_method_dispatch_func(PyObject *module, PyObject *args)
{
    PyObject *dispatch_func;
    PyObject *base_func;
    PyObject *func_name;

    if (!PyArg_ParseTuple(args, "OOO", &dispatch_func, &base_func, &func_name)) {
        return nullptr;
    }

    if (!PyCallable_Check(dispatch_func)) {
        PyErr_SetString(PyExc_TypeError, "dispatch_func must be callable");
        return nullptr;
    }

    if (!PyCallable_Check(base_func) && !PyObject_HasAttrString(base_func, "__get__")) {
        PyErr_SetString(PyExc_TypeError, "base_func must be callable or a descriptor");
        return nullptr;
    }

    if (!PyUnicode_Check(func_name)) {
        PyErr_SetString(PyExc_TypeError, "func_name must be a string");
        return nullptr;
    }

    methods_state *state = get_methods_state(module);
    MethodDispatchFunc *self = PyObject_GC_New(MethodDispatchFunc, state->MethodDispatchFuncType);
    if (self == nullptr) {
        return nullptr;
    }

    self->dispatch_func = Py_NewRef(dispatch_func);
    self->base_func = Py_NewRef(base_func);
    self->func_name = Py_NewRef(func_name);
    self->dict = nullptr;

    PyObject_GC_Track(self);
    return (PyObject *)self;
}

//

PyDoc_STRVAR(methods_doc, "Native C++ implementations for omlish.dispatch.methods");

static int methods_exec(PyObject *module)
{
    methods_state *state = get_methods_state(module);

    // Create the type dynamically
    state->MethodDispatchFuncType = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &MethodDispatchFunc_spec,
        nullptr
    );
    if (state->MethodDispatchFuncType == nullptr) {
        return -1;
    }

    // Add the type to the module
    if (PyModule_AddType(module, state->MethodDispatchFuncType) < 0) {
        Py_CLEAR(state->MethodDispatchFuncType);
        return -1;
    }

    return 0;
}

static int methods_traverse(PyObject *module, visitproc visit, void *arg)
{
    methods_state *state = get_methods_state(module);
    Py_VISIT(state->MethodDispatchFuncType);
    return 0;
}

static int methods_clear(PyObject *module)
{
    methods_state *state = get_methods_state(module);
    Py_CLEAR(state->MethodDispatchFuncType);
    return 0;
}

static void methods_free(void *module)
{
    methods_clear((PyObject *)module);
}

static PyMethodDef methods_methods[] = {
    {"build_method_dispatch_func", (PyCFunction)build_method_dispatch_func, METH_VARARGS, build_method_dispatch_func_doc},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot methods_slots[] = {
    {Py_mod_exec, (void *) methods_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED},
    {0, NULL}
};

static struct PyModuleDef methods_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = methods_doc,
    .m_size = sizeof(methods_state),
    .m_methods = methods_methods,
    .m_slots = methods_slots,
    .m_traverse = methods_traverse,
    .m_clear = methods_clear,
    .m_free = methods_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__methods(void)
{
    return PyModuleDef_Init(&methods_module);
}

}
