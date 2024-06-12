#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

typedef struct _junk_state {

} _junk_state;

static inline _junk_state *
get_junk_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_junk_state *)state;
}


//

typedef struct {
    PyObject_HEAD
    PyObject *first;
    PyObject *last;
    int number;
} CustomObject;

static int Custom_traverse(CustomObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->first);
    Py_VISIT(self->last);
    return 0;
}

static int Custom_clear(CustomObject *self)
{
    Py_CLEAR(self->first);
    Py_CLEAR(self->last);
    return 0;
}

static void Custom_dealloc(CustomObject *self)
{
    PyObject_GC_UnTrack(self);
    Custom_clear(self);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject * Custom_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    CustomObject *self;
    self = (CustomObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->first = PyUnicode_FromString("");
        if (self->first == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->last = PyUnicode_FromString("");
        if (self->last == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->number = 0;
    }
    return (PyObject *) self;
}

static int Custom_init(CustomObject *self, PyObject *args, PyObject *kwds)
{
    static const char *kwlist[] = {"first", "last", "number", NULL};
    PyObject *first = NULL, *last = NULL, *tmp;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|UUi", (char **)kwlist, &first, &last, &self->number)) {
        return -1;
    }

    if (first) {
        tmp = self->first;
        Py_INCREF(first);
        self->first = first;
        Py_DECREF(tmp);
    }
    if (last) {
        tmp = self->last;
        Py_INCREF(last);
        self->last = last;
        Py_DECREF(tmp);
    }
    return 0;
}

static PyMemberDef Custom_members[] = {
    {"number", T_INT, offsetof(CustomObject, number), 0, "custom number"},
    {NULL}
};

static PyObject * Custom_getfirst(CustomObject *self, void *closure)
{
    Py_INCREF(self->first);
    return self->first;
}

static int Custom_setfirst(CustomObject *self, PyObject *value, void *closure)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete the first attribute");
        return -1;
    }
    if (!PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "The first attribute value must be a string");
        return -1;
    }
    Py_INCREF(value);
    Py_CLEAR(self->first);
    self->first = value;
    return 0;
}

static PyObject * Custom_getlast(CustomObject *self, void *closure)
{
    Py_INCREF(self->last);
    return self->last;
}

static int Custom_setlast(CustomObject *self, PyObject *value, void *closure)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete the last attribute");
        return -1;
    }
    if (!PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "The last attribute value must be a string");
        return -1;
    }
    Py_INCREF(value);
    Py_CLEAR(self->last);
    self->last = value;
    return 0;
}

static PyGetSetDef Custom_getsetters[] = {
    {"first", (getter) Custom_getfirst, (setter) Custom_setfirst, "first name", NULL},
    {"last", (getter) Custom_getlast, (setter) Custom_setlast, "last name", NULL},
    {NULL}
};

static PyObject * Custom_name(CustomObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyUnicode_FromFormat("%S %S", self->first, self->last);
}

static PyMethodDef Custom_methods[] = {
    {"name", (PyCFunction) Custom_name, METH_NOARGS, "Return the name, combining the first and last name"},
    {NULL}
};

static PyTypeObject CustomType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "junk.Custom",
    .tp_basicsize = sizeof(CustomObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor) Custom_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_doc = PyDoc_STR("Custom objects"),
    .tp_traverse = (traverseproc) Custom_traverse,
    .tp_clear = (inquiry) Custom_clear,
    .tp_methods = Custom_methods,
    .tp_members = Custom_members,
    .tp_getset = Custom_getsetters,
    .tp_init = (initproc) Custom_init,
    .tp_new = Custom_new,
};

//

static PyObject * junk(PyObject *self, PyObject *args)
{
    return Py_BuildValue("k", 422);
}

static PyObject *abc_get_cache_token = NULL;

static PyObject * abctok(PyObject *self, PyObject *args)
{
    return PyObject_Vectorcall(abc_get_cache_token, NULL, 0, NULL);
}

//

PyDoc_STRVAR(_junk_doc,
             "Tools that operate on functions.");

static int _junk_exec(PyObject *module)
{
    /*
    _junk_state *state = get_junk_state(module);
    state->kwd_mark = _PyObject_CallNoArgs((PyObject *)&PyBaseObject_Type);
    if (state->kwd_mark == NULL) {
        return -1;
    }

    state->partial_type = (PyTypeObject *)PyType_FromModuleAndSpec(module,
                                                                   &partial_type_spec, NULL);
    if (state->partial_type == NULL) {
        return -1;
    }
    if (PyModule_AddType(module, state->partial_type) < 0) {
        return -1;
    }

    PyObject *lru_cache_type = PyType_FromModuleAndSpec(module,
                                                        &lru_cache_type_spec, NULL);
    if (lru_cache_type == NULL) {
        return -1;
    }
    if (PyModule_AddType(module, (PyTypeObject *)lru_cache_type) < 0) {
        Py_DECREF(lru_cache_type);
        return -1;
    }
    Py_DECREF(lru_cache_type);

    state->keyobject_type = (PyTypeObject *)PyType_FromModuleAndSpec(module,
                                                                     &keyobject_type_spec, NULL);
    if (state->keyobject_type == NULL) {
        return -1;
    }
    // keyobject_type is used only internally.
    // So we don't expose it in module namespace.

    state->lru_list_elem_type = (PyTypeObject *)PyType_FromModuleAndSpec(
            module, &lru_list_elem_type_spec, NULL);
    if (state->lru_list_elem_type == NULL) {
        return -1;
    }
    // lru_list_elem is used only in _lru_cache_wrapper.
    // So we don't expose it in module namespace.

    return 0;
     */

    if (PyType_Ready(&CustomType) < 0) {
        return NULL;
    }

    PyObject *abc_module = PyImport_ImportModule("abc");
    if (abc_module == NULL) {
        return NULL;
    }
    if ((abc_get_cache_token = PyObject_GetAttrString(abc_module, "get_cache_token")) == NULL) {
        Py_DECREF(abc_module);
        return NULL;
    }
    Py_DECREF(abc_module);

    PyObject *m;

    m = PyModule_Create(&module_def);
    if (m == NULL) {
        Py_DECREF(abc_get_cache_token);
        return NULL;
    }

    Py_INCREF(&CustomType);
    if (PyModule_AddObject(m, "Custom", (PyObject *) &CustomType) < 0) {
        Py_DECREF(abc_get_cache_token);
        Py_DECREF(&CustomType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}

static int _junk_traverse(PyObject *module, visitproc visit, void *arg)
{
    _junk_state *state = get_junk_state(module);
    // Py_VISIT(state->kwd_mark);
    return 0;
}

static int
_junk_clear(PyObject *module)
{
    _junk_state *state = get_junk_state(module);
    // Py_CLEAR(state->kwd_mark);
    return 0;
}

static void
_junk_free(void *module)
{
    _junk_clear((PyObject *)module);
}

static PyMethodDef module_methods[] = {
    {"junk", junk, METH_NOARGS, "junk"},
    {"abctok", abctok, METH_NOARGS, "abctok"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _junk_slots[] = {
        {Py_mod_exec, _junk_exec},
        {0, NULL}
};

static struct PyModuleDef _junk_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "junk",
    .m_doc = _junk_doc,
    .m_size = sizeof(_junk_state),
    .m_methods = module_methods,
    .m_slots = _junk_slots,
    .m_traverse = _junk_traverse,
    .m_clear = _junk_clear,
    .m_free = _junk_free,
};


extern "C" {

PyMODINIT_FUNC PyInit_junk(void)
{
    return PyModuleDef_Init(&_junk_module);
}

}
