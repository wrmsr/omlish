// @omlish-cext
#define PY_SSIZE_T_CLEAN
#include <Python.h>

//

#define _MODULE_NAME "_asyncs"
#define _PACKAGE_NAME "omlish.lang"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

//

typedef struct {
    PyObject *SyncAwaitCoroutineNotTerminatedError;
    PyObject *str_close;
    PyObject *str___await__;
} module_state;

static module_state *
get_module_state(PyObject *module)
{
    return (module_state *) PyModule_GetState(module);
}

//

static void
suppress_close(PyObject *iter, module_state *state)
{
    PyObject *res = PyObject_CallMethodNoArgs(iter, state->str_close);
    if (!res) {
        PyErr_Clear();
    } else {
        Py_DECREF(res);
    }
}

static PyObject *
sync_await(PyObject *module, PyObject *aw)
{
    module_state *state = get_module_state(module);
    PyObject *await_meth = NULL;
    PyObject *iter = NULL;
    PyObject *result = NULL;
    PySendResult sres;

    await_meth = PyObject_GetAttr(aw, state->str___await__);
    if (await_meth == NULL) {
        if (PyErr_ExceptionMatches(PyExc_AttributeError)) {
            PyErr_SetString(PyExc_TypeError, "object is not awaitable (no __await__)");
        }
        goto error;
    }

    iter = PyObject_CallNoArgs(await_meth);
    Py_DECREF(await_meth);
    await_meth = NULL;

    if (iter == NULL) {
        goto error;
    }

    if (!PyIter_Check(iter)) {
        Py_DECREF(iter);
        PyErr_SetString(PyExc_TypeError, "__await__() must return an iterator");
        goto error;
    }

    sres = PyIter_Send(iter, Py_None, &result);
    if (sres == PYGEN_ERROR) {
        Py_DECREF(iter);
        goto error;
    }
    if (sres == PYGEN_NEXT) {
        Py_XDECREF(result);
        suppress_close(iter, state);
        Py_DECREF(iter);
        PyErr_SetString(state->SyncAwaitCoroutineNotTerminatedError, "Not terminated");
        goto error;
    }

    Py_DECREF(iter);
    return result;

error:
    return NULL;
}

//

static PyMethodDef mod_methods[] = {
    {"sync_await", sync_await, METH_O, "sync_await"},
    {NULL, NULL, 0, NULL}
};

static int
module_traverse(PyObject *module, visitproc visit, void *arg)
{
    module_state *state = get_module_state(module);
    Py_VISIT(state->SyncAwaitCoroutineNotTerminatedError);
    Py_VISIT(state->str_close);
    Py_VISIT(state->str___await__);
    return 0;
}

static int
module_clear(PyObject *module)
{
    module_state *state = get_module_state(module);
    Py_CLEAR(state->SyncAwaitCoroutineNotTerminatedError);
    Py_CLEAR(state->str_close);
    Py_CLEAR(state->str___await__);
    return 0;
}

static void
module_free(void *module)
{
    module_clear((PyObject *) module);
}

static int
module_exec(PyObject *module)
{
    module_state *state = get_module_state(module);

    state->str_close = PyUnicode_InternFromString("close");
    if (!state->str_close) {
        return -1;
    }

    state->str___await__ = PyUnicode_InternFromString("__await__");
    if (!state->str___await__) {
        return -1;
    }

    PyObject *asyncs_module = PyImport_ImportModule("omlish.lite.asyncs");
    if (!asyncs_module) {
        return -1;
    }

    state->SyncAwaitCoroutineNotTerminatedError = PyObject_GetAttrString(
        asyncs_module,
        "SyncAwaitCoroutineNotTerminatedError"
    );
    Py_DECREF(asyncs_module);

    if (!state->SyncAwaitCoroutineNotTerminatedError) {
        return -1;
    }

    return 0;
}

//

PyDoc_STRVAR(module_doc, _MODULE_NAME);

static PyModuleDef_Slot module_slots[] = {
    {Py_mod_exec, (void *) module_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {0, NULL}
};

static PyModuleDef module_def = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = module_doc,
    .m_size = sizeof(module_state),
    .m_methods = mod_methods,
    .m_slots = module_slots,
    .m_traverse = module_traverse,
    .m_clear = module_clear,
    .m_free = module_free,
};

extern "C" {

PyMODINIT_FUNC
PyInit__asyncs(void)
{
    return PyModuleDef_Init(&module_def);
}

}
