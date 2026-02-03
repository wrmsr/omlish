// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

//

#define _MODULE_NAME "_dispatch"
#define _PACKAGE_NAME "omlish.dispatch"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

// No module state needed

//

typedef struct {
    PyObject_HEAD
    PyObject *dispatch_func;
    PyObject *base_func;
    PyObject *func_name;
    PyObject *dict;
} MethodDispatchFunc;

static void MethodDispatchFunc_dealloc(MethodDispatchFunc *self)
{
    PyObject_GC_UnTrack(self);
    Py_XDECREF(self->dispatch_func);
    Py_XDECREF(self->base_func);
    Py_XDECREF(self->func_name);
    Py_XDECREF(self->dict);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

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
        // Use PyObject_GetAttr directly instead of calling getattr builtin
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
        PyObject *bound_func = PyObject_CallMethodOneArg(
            self->base_func,
            PyUnicode_InternFromString("__get__"),
            instance
        );

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

static PyTypeObject MethodDispatchFunc_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = _MODULE_FULL_NAME ".MethodDispatchFunc",
    .tp_basicsize = sizeof(MethodDispatchFunc),
    .tp_dealloc = (destructor)MethodDispatchFunc_dealloc,
    .tp_call = (ternaryfunc)MethodDispatchFunc_call,
    .tp_descr_get = (descrgetfunc)MethodDispatchFunc_get,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .tp_doc = PyDoc_STR("Fast dispatch function for Method instances"),
    .tp_traverse = (traverseproc)MethodDispatchFunc_traverse,
    .tp_clear = (inquiry)MethodDispatchFunc_clear,
    .tp_dictoffset = offsetof(MethodDispatchFunc, dict),
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

    MethodDispatchFunc *self = PyObject_GC_New(MethodDispatchFunc, &MethodDispatchFunc_Type);
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

PyDoc_STRVAR(dispatch_doc, "Native C++ implementations for omlish.dispatch");

static int dispatch_exec(PyObject *module)
{
    // Add the type to the module
    if (PyType_Ready(&MethodDispatchFunc_Type) < 0) {
        return -1;
    }

    return 0;
}

static PyMethodDef dispatch_methods[] = {
    {"build_method_dispatch_func", (PyCFunction)build_method_dispatch_func, METH_VARARGS, build_method_dispatch_func_doc},
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
    .m_size = 0,
    .m_methods = dispatch_methods,
    .m_slots = dispatch_slots,
};

extern "C" {

PyMODINIT_FUNC PyInit__dispatch(void)
{
    return PyModuleDef_Init(&dispatch_module);
}

}
