// @omlish-cext
/*
TODO:
 - error handle no arg / no dispatched type (NULL / None)
  - with func_name
 - pickle
 - repr
*/
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

#define _MODULE_NAME "_dispatch"
#define _PACKAGE_NAME "x.dev.c"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

//static struct PyModuleDef _dispatch_module;

//

typedef struct _dispatch_module_state {
    PyTypeObject *function_wrapper_type;
} _dispatch_module_state;

static inline _dispatch_module_state * get_dispatch_module_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_dispatch_module_state *)state;
}

//static inline _dispatch_module_state * get_dispatch_module_state_by_type(PyTypeObject *type)
//{
//    PyObject *module = PyType_GetModuleByDef(type, &_dispatch_module_module);
//    if (module == NULL) {
//        return NULL;
//    }
//    return get_dispatch_module_state(module);
//}

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
    vectorcallfunc vectorcall;
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

static PyObject * function_wrapper_vectorcall(function_wrapper_object *self, PyObject *const *args, size_t nargsf, PyObject *kwnames);

static PyObject * function_wrapper_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (PyTuple_GET_SIZE(args) != 1) {
        PyErr_SetString(PyExc_TypeError, "type 'function_wrapper' takes exactly one positional argument");
        return NULL;
    }

    PyObject *dispatch = PyTuple_GET_ITEM(args, 0);
    if (!PyCallable_Check(dispatch)) {
        PyErr_SetString(PyExc_TypeError, "the argument must be callable");
        return NULL;
    }

    function_wrapper_object *self;
    self = (function_wrapper_object *) type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }

    self->dispatch = Py_NewRef(dispatch);
    self->vectorcall = (vectorcallfunc) function_wrapper_vectorcall;

    if (kwds != NULL) {
        self->dict = PyDict_Copy(kwds);
    }

    return (PyObject *) self;
}

static PyObject * function_wrapper_do_dispatch(function_wrapper_object *self, PyObject *arg) {
    PyTypeObject *arg_ty = Py_TYPE(arg);

    PyObject *args[2] = {NULL, (PyObject *) arg_ty};
    PyObject *disp_res = PyObject_Vectorcall(self->dispatch, &args[1], 1 | PY_VECTORCALL_ARGUMENTS_OFFSET, NULL);

    return disp_res;
}

static PyObject * function_wrapper_call(function_wrapper_object *self, PyObject *args, PyObject *kwargs) {
    assert(PyCallable_Check(self->dispatch));

    if (PyTuple_GET_SIZE(args) < 1) {
        PyErr_SetString(PyExc_TypeError, "function_wrapper takes at least one positional argument");
        return NULL;
    }

    PyObject *arg = PyTuple_GET_ITEM(args, 0);
    PyObject *disp_res = function_wrapper_do_dispatch(self, arg);
    if (disp_res == NULL) {
        return NULL;
    }

    PyObject *res = PyObject_Call(disp_res, args, kwargs);

    Py_DECREF(disp_res);

    return res;
}

static PyObject * function_wrapper_vectorcall(function_wrapper_object *self, PyObject *const *args, size_t nargsf, PyObject *kwnames)
{
    assert(PyCallable_Check(self->dispatch));

    if (PyVectorcall_NARGS(nargsf) < 1) {
        PyErr_SetString(PyExc_TypeError, "function_wrapper takes at least one positional argument");
        return NULL;
    }

    PyObject *arg = args[0];
    PyObject *disp_res = function_wrapper_do_dispatch(self, arg);
    if (disp_res == NULL) {
        return NULL;
    }

    PyObject *res = PyObject_Vectorcall(disp_res, args, nargsf, kwnames);

    Py_DECREF(disp_res);

    return res;
}

static PyObject *
function_wrapper_reduce(function_wrapper_object *self, PyObject *unused)
{
    return Py_BuildValue(
            "O(O)(OO)",
            Py_TYPE(self),
            self->dispatch,
            self->dispatch, self->dict ? self->dict : Py_None);
}

static PyObject *
function_wrapper_setstate(function_wrapper_object *self, PyObject *state)
{
    PyObject *dispatch, *dict;

    if (!PyTuple_Check(state) ||
        !PyArg_ParseTuple(state, "OO", &dispatch, &dict) ||
        !PyCallable_Check(dispatch))
    {
        PyErr_SetString(PyExc_TypeError, "invalid function_wrapper state");
        return NULL;
    }

    if (dict == Py_None) {
        dict = NULL;
    } else {
        Py_INCREF(dict);
    }

    Py_SETREF(self->dispatch, Py_NewRef(dispatch));
    Py_XSETREF(self->dict, dict);
    Py_RETURN_NONE;
}

static PyMemberDef function_wrapper_members[] = {
    {"dispatch", T_OBJECT, offsetof(function_wrapper_object, dispatch), READONLY},
    {"__weaklistoffset__", T_PYSSIZET, offsetof(function_wrapper_object, weakreflist), READONLY},
    {"__dictoffset__", T_PYSSIZET, offsetof(function_wrapper_object, dict), READONLY},
    {"__vectorcalloffset__", T_PYSSIZET, offsetof(function_wrapper_object , vectorcall), READONLY},
    {NULL}
};

static PyGetSetDef function_wrapper_getsetters[] = {
    {"__dict__", PyObject_GenericGetDict, PyObject_GenericSetDict},
    {NULL}
};

static PyMethodDef function_wrapper_methods[] = {
    {"__reduce__", (PyCFunction) function_wrapper_reduce, METH_NOARGS},
    {"__setstate__", (PyCFunction) function_wrapper_setstate, METH_O},
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
    {Py_tp_call, (void *) function_wrapper_call},
    {0, 0}
};

static PyType_Spec function_wrapper_type_spec = {
    .name = _MODULE_FULL_NAME ".function_wrapper",
    .basicsize = sizeof(function_wrapper_object),
    .itemsize = 0,
    .flags =
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
        Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_VECTORCALL |
        Py_TPFLAGS_IMMUTABLETYPE,
    .slots = function_wrapper_type_slots
};

//

static int _dispatch_module_exec(PyObject *module)
{
    _dispatch_module_state *state = get_dispatch_module_state(module);

    state->function_wrapper_type = (PyTypeObject *)PyType_FromModuleAndSpec(module, &function_wrapper_type_spec, NULL);
    if (state->function_wrapper_type == NULL) {
        return -1;
    }
    if (PyModule_AddType(module, state->function_wrapper_type) < 0) {
        return -1;
    }

    return 0;
}

static int _dispatch_module_traverse(PyObject *module, visitproc visit, void *arg)
{
    _dispatch_module_state *state = get_dispatch_module_state(module);
    Py_VISIT(state->function_wrapper_type);
    return 0;
}

static int _dispatch_module_clear(PyObject *module)
{
    _dispatch_module_state *state = get_dispatch_module_state(module);
    Py_CLEAR(state->function_wrapper_type);
    return 0;
}

static void _dispatch_module_free(void *module)
{
    _dispatch_module_clear((PyObject *)module);
}

static PyMethodDef _dispatch_module_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _dispatch_module_slots[] = {
    {Py_mod_exec, (void *) _dispatch_module_exec},
    {0, NULL}
};

static struct PyModuleDef _dispatch_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_size = sizeof(_dispatch_module_state),
    .m_methods = _dispatch_module_methods,
    .m_slots = _dispatch_module_slots,
    .m_traverse = _dispatch_module_traverse,
    .m_clear = _dispatch_module_clear,
    .m_free = _dispatch_module_free,
};

extern "C" {

PyMODINIT_FUNC PyInit__dispatch(void)
{
    return PyModuleDef_Init(&_dispatch_module);
}

}
