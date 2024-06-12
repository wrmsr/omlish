#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

static struct PyModuleDef _dispatch_module;

//

typedef struct _dispatch_state {
    PyTypeObject *function_wrapper_type;
} _dispatch_state;

static inline _dispatch_state * get_dispatch_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_dispatch_state *)state;
}

static inline _dispatch_state * get_dispatch_state_by_type(PyTypeObject *type)
{
    PyObject *module = PyType_GetModuleByDef(type, &_dispatch_module);
    if (module == NULL) {
        return NULL;
    }
    return get_dispatch_state(module);
}


//

/*
def wrapper(*args, **kwargs):
    if not args:
        raise TypeError(f'{func_name} requires at least 1 positional argument')
    if (impl := disp_dispatch(type(args[0]))) is not None:
        return impl(*args, **kwargs)
    raise RuntimeError(f'No dispatch: {type(args[0])}')
 */

typedef struct {
    PyObject_HEAD
    PyObject *dispatch;
    PyObject *dict;
    PyObject *weakreflist;
} function_wrapper_object;

static int function_wrapper_traverse(function_wrapper_object *self, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(self));
    Py_VISIT(self->dispatch);
    Py_VISIT(self->dict);
    return 0;
}

static int function_wrapper_clear(function_wrapper_object *self)
{
    Py_CLEAR(self->dispatch);
    Py_CLEAR(self->dict);
    return 0;
}

static void function_wrapper_dealloc(function_wrapper_object *self)
{
    PyTypeObject *tp = Py_TYPE(self);
    PyObject_GC_UnTrack(self);
    if (self->weakreflist != NULL) {
        PyObject_ClearWeakRefs((PyObject *) self);
    }
    function_wrapper_clear(self);
    tp->tp_free((PyObject *) self);
    Py_DECREF(tp);
}

static PyObject * function_wrapper_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (PyTuple_GET_SIZE(args) != 1) {
        PyErr_SetString(PyExc_TypeError, "type 'function_wrapper' takes exactly one argument");
        return NULL;
    }
    if (PyDict_GET_SIZE(kwds) != 0) {
        PyErr_SetString(PyExc_TypeError, "type 'function_wrapper' takes exactly no keyword arguments");
        return NULL;
    }

    PyObject *dispatch = PyTuple_GET_ITEM(args, 0);
    if (!PyCallable_Check(dispatch)) {
        PyErr_SetString(PyExc_TypeError, "the first argument must be callable");
        return NULL;
    }

    function_wrapper_object *self;
    self = (function_wrapper_object *) type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }

    self->dispatch = Py_NewRef(dispatch);

    return (PyObject *) self;
}

static PyObject * function_wrapper_call(function_wrapper_object *self, PyObject *args, PyObject *kwargs) {
    assert(PyCallable_Check(self->dispatch));

    PyObject *res = PyObject_Call(self->dispatch, args, kwargs);
    return res;
}

static PyMemberDef function_wrapper_members[] = {
    {"dispatch", T_OBJECT, offsetof(function_wrapper_object, dispatch), READONLY},
    {"__weaklistoffset__", T_PYSSIZET, offsetof(function_wrapper_object, weakreflist), READONLY},
    {"__dictoffset__", T_PYSSIZET, offsetof(function_wrapper_object, dict), READONLY},
    {NULL}
};

static PyGetSetDef function_wrapper_getsetters[] = {
        {"__dict__", PyObject_GenericGetDict, PyObject_GenericSetDict},
    {NULL}
};

static PyMethodDef function_wrapper_methods[] = {
    {NULL}
};

static PyType_Slot function_wrapper_type_slots[] = {
        {Py_tp_traverse, (void *) function_wrapper_traverse},
        {Py_tp_clear, (void *) function_wrapper_clear},
        {Py_tp_methods, function_wrapper_methods},
        {Py_tp_members, function_wrapper_members},
        {Py_tp_getset, function_wrapper_getsetters},
        {Py_tp_new, (void *) function_wrapper_new},
        {Py_tp_dealloc, (void *) function_wrapper_dealloc},
        {Py_tp_call, function_wrapper_call},

        {0, 0}
};

static PyType_Spec function_wrapper_type_spec = {
        .name = "_dispatch.function_wrapper",
        .basicsize = sizeof(function_wrapper_object),
        .itemsize = 0,
        .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
                 Py_TPFLAGS_BASETYPE | Py_TPFLAGS_IMMUTABLETYPE,
        .slots = function_wrapper_type_slots
};

//

static int _dispatch_exec(PyObject *module)
{
    _dispatch_state *state = get_dispatch_state(module);

    state->function_wrapper_type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &function_wrapper_type_spec, NULL);
    if (state->function_wrapper_type == NULL) {
        return -1;
    }
    if (PyModule_AddType(module, state->function_wrapper_type) < 0) {
        return -1;
    }

    return 0;
}

static int _dispatch_traverse(PyObject *module, visitproc visit, void *arg)
{
    _dispatch_state *state = get_dispatch_state(module);
    Py_VISIT(state->function_wrapper_type);
    return 0;
}

static int _dispatch_clear(PyObject *module)
{
    _dispatch_state *state = get_dispatch_state(module);
    Py_CLEAR(state->function_wrapper_type);
    return 0;
}

static void _dispatch_free(void *module)
{
    _dispatch_clear((PyObject *)module);
}

static PyMethodDef _dispatch_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _dispatch_slots[] = {
        {Py_mod_exec, (void *) _dispatch_exec},
        {0, NULL}
};

static struct PyModuleDef _dispatch_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_dispatch",
    .m_size = sizeof(_dispatch_state),
    .m_methods = _dispatch_methods,
    .m_slots = _dispatch_slots,
    .m_traverse = _dispatch_traverse,
    .m_clear = _dispatch_clear,
    .m_free = _dispatch_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__dispatch(void)
{
    return PyModuleDef_Init(&_dispatch_module);
}

}
