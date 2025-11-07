// @omlish-cext
#include <atomic>

#define PY_SSIZE_T_CLEAN
#define Py_BUILD_CORE 1
#include "Python.h"
#include "internal/pycore_frame.h"
#if PY_VERSION_HEX >= 0x030E0000
#include "internal/pycore_interpframe.h"
#endif
#undef Py_BUILD_CORE

#if PY_VERSION_HEX < 0x030D0000
#error "This extension requires CPython 3.13+"
#endif

//

#define _MODULE_NAME "_capture"
#define _PACKAGE_NAME "omlish.lang.imports"
#define _MODULE_FULL_NAME _PACKAGE_NAME "." _MODULE_NAME

//

static PyObject *
_set_frame_builtins(PyObject *self, PyObject *args)
{
    PyObject *frame_obj;
    PyObject *old_builtins;
    PyObject *new_builtins;

    if (!PyArg_ParseTuple(
        args, "OO!O!",
        &frame_obj,
        &PyDict_Type, &old_builtins,
        &PyDict_Type, &new_builtins
    )) {
        return NULL;
    }

    if (!PyFrame_Check(frame_obj)) {
        PyErr_SetString(PyExc_TypeError, "first argument must be a frame object");
        return NULL;
    }

    PyFrameObject *frame = (PyFrameObject *)frame_obj;
    _PyInterpreterFrame *iframe = frame->f_frame;

    if (!iframe) {
        PyErr_SetString(PyExc_ValueError, "frame has no underlying interpreter frame");
        return NULL;
    }

    std::atomic_ref<PyObject*> builtins_ref(iframe->f_builtins);
    PyObject* expected = old_builtins;
    if (builtins_ref.compare_exchange_strong(
        expected,
        new_builtins,
        std::memory_order_acq_rel,
        std::memory_order_acquire
    )) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

//

PyDoc_STRVAR(capture_doc, _MODULE_NAME);

static PyMethodDef capture_methods[] = {
    {"_set_frame_builtins", _set_frame_builtins, METH_VARARGS, "_set_frame_builtins"},
    {NULL, NULL, 0, NULL}
};

static PyModuleDef_Slot capture_slots[] = {
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {0, NULL}
};

static PyModuleDef capture_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = _MODULE_NAME,
    .m_doc = capture_doc,
    .m_size = 0,
    .m_methods = capture_methods,
    .m_slots = capture_slots,
    .m_traverse = NULL,
    .m_clear = NULL,
    .m_free = NULL,
};

extern "C" {

PyMODINIT_FUNC
PyInit__capture(void)
{
    return PyModuleDef_Init(&capture_module);
}

}
