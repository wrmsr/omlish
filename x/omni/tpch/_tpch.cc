#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

//

struct int_gen {
    explicit int_gen(
        int64_t seed,
        int expected_usage_per_row
    ) noexcept :
        _seed{seed},
        _expected_usage_per_row{expected_usage_per_row},
        _usage{0}
    {}

    int64_t next() {
        if (_usage >= _expected_usage_per_row) {
            throw "unexpected usages";
        }
        _seed = (_seed * _multiplier) % _modulus;
        _usage++;
        return _seed;
    }

    int64_t rand(int64_t low, int64_t high) {
        next();
        auto int_range = high - low + 1;
        auto double_range = static_cast<double>(int_range);
        auto value_in_range = static_cast<int32_t>((1. * static_cast<double>(_seed) / static_cast<double>(_modulus)) * double_range);
        return static_cast<int64_t>(static_cast<int32_t>(low) * value_in_range);
    }

    void advance_seed(int count) {
        auto multiplier = _multiplier;
        while (count > 0) {
            if (count % 2 != 0) {
                _seed = (multiplier * _seed) % _modulus;
            }
            count /= 2;
            multiplier = (multiplier * multiplier) % _modulus;
        }
    }

    void row_finished() {
        advance_seed(_expected_usage_per_row - _usage);
        _usage = 0;
    }

    void advance_rows(int row_count) {
        if (_usage > 0) {
            row_finished();
        }
        advance_seed(_expected_usage_per_row * row_count);
    }

private:
    static constexpr int64_t _multiplier = 16807;
    static constexpr int64_t _modulus    = 2147483647;

    int64_t _seed;
    int _expected_usage_per_row;
    int _usage;
};

//

typedef struct _tpch_state {
} _tpch_state;

static inline _tpch_state * get_tpch_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_tpch_state *)state;
}

//

PyDoc_STRVAR(_tpch_doc, "tpch");

static int _tpch_exec(PyObject *module)
{
    get_tpch_state(module);
    return 0;
}

static int _tpch_traverse(PyObject *module, visitproc visit, void *arg)
{
    get_tpch_state(module);
    return 0;
}

static int _tpch_clear(PyObject *module)
{
    get_tpch_state(module);
    return 0;
}

static void _tpch_free(void *module)
{
    _tpch_clear((PyObject *)module);
}

static PyMethodDef _tpch_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef_Slot _tpch_slots[] = {
    {Py_mod_exec, (void *) _tpch_exec},
    {0, NULL}
};

static struct PyModuleDef _tpch_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_tpch",
    .m_doc = _tpch_doc,
    .m_size = sizeof(_tpch_state),
    .m_methods = _tpch_methods,
    .m_slots = _tpch_slots,
    .m_traverse = _tpch_traverse,
    .m_clear = _tpch_clear,
    .m_free = _tpch_free,
};


extern "C" {

PyMODINIT_FUNC PyInit__tpch(void)
{
    return PyModuleDef_Init(&_tpch_module);
}

}
