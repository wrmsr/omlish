/*
https://github.com/wrmsr/bane/blob/27647abdcfb323b73e6982a5c318c7029496b203/core/tpch/text.go
https://github.com/wrmsr/omnibus/blob/c2ff67b6c5c80aa03fe27a9b6f36212f3212c7ca/omnibus/_ext/cy/tpch.pyx
*/
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#include <unistd.h>

///

static constexpr int64_t int_multiplier = 16807;
static constexpr int64_t int_modulus    = 2147483647;

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
        _seed = (_seed * int_multiplier) % int_modulus;
        _usage++;
        return _seed;
    }

    int64_t rand(int64_t low, int64_t high) {
        next();
        auto int_range = high - low + 1;
        auto double_range = static_cast<double>(int_range);
        auto value_in_range = static_cast<int32_t>((1. * static_cast<double>(_seed) / static_cast<double>(int_modulus)) * double_range);
        return static_cast<int64_t>(static_cast<int32_t>(low) * value_in_range);
    }

    void advance_seed(int count) {
        auto multiplier = int_multiplier;
        while (count > 0) {
            if (count % 2 != 0) {
                _seed = (multiplier * _seed) % int_modulus;
            }
            count /= 2;
            multiplier = (multiplier * multiplier) % int_modulus;
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
    int64_t _seed;
    const int _expected_usage_per_row;

    int _usage;
};

//

static constexpr int64_t long_multiplier    = 6364136223846793005;
static constexpr int64_t long_increment     = 1;

static constexpr int64_t long_multiplier_32 = 16807;
static constexpr int64_t long_modulus_32    = 2147483647;

struct long_gen {
    explicit long_gen(
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
        _seed = (_seed * long_multiplier) + long_increment;
        _usage++;
        return _seed;
    }

    int64_t rand(int64_t low, int64_t high) {
        next();
        auto value_in_range = llabs(_seed) % (high - low + 1);
        return low + value_in_range;
    }

    void advance_seed(int count) {
        auto multiplier = long_multiplier_32;
        while (count > 0) {
            if (count % 2 != 0) {
                _seed = (multiplier * _seed) % long_modulus_32;
            }
            count /= 2;
            multiplier = (multiplier * multiplier) % long_modulus_32;
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
    int64_t _seed;
    const int _expected_usage_per_row;

    int _usage;
};

//

struct text_dist_item {
    const char* item;
    int size;
};

struct text_dist {
    const text_dist_item* items;
    int size;
};

struct text_dists {
    text_dist adjectives;
    text_dist adverbs;
    text_dist articles;
    text_dist auxiliaries;
    text_dist grammars;
    text_dist noun_phrase;
    text_dist nouns;
    text_dist prepositions;
    text_dist terminators;
    text_dist verb_phrase;
    text_dist verbs;
};

struct text_pool_gen {
    explicit text_pool_gen(
        char* buf,
        int size,
        text_dists& dists
    ) :
        _buf{buf},
        _size{size},
        _dists{dists},

        _pos{0},
        _last{0},
        _seed{_initial_seed}
    {
        while (_pos < size) {
            _generate_sentence();
        }
    }

private:
    void _write(const char* p, int sz) {
        if (!sz) {
            return;
        }
        if ((_pos + sz) >= _size) {
            throw "write past end";
        }
        memcpy(_buf + _pos, p, sz);
        _pos += sz;
        _last = _buf[_pos - 1];
    }

    void _erase(int i) {
        if (i > _pos) {
            throw i;
        }
        _pos -= i;
        if (_pos) {
            _last = _buf[_pos - 1];
        } else {
            _last = 0;
        }
    }

    text_dist_item _rand(text_dist dist) {
        _seed = (_seed * int_multiplier) % int_modulus;
        auto double_range = static_cast<double>(dist.size);
        auto idx = static_cast<int>((1. * _seed / int_modulus) * double_range);
        return dist.items[idx];
    }

    void _generate_noun_phrase() {
        auto syntax = _rand(_dists.noun_phrase);
        text_dist source;
        for (int i = 0; i < syntax.size; i++) {
            if (syntax.item[i] == 'A') {
                source = _dists.articles;
            } else if (syntax.item[i] == 'J') {
                source = _dists.adjectives;
            } else if (syntax.item[i] == 'D') {
                source = _dists.adverbs;
            } else if (syntax.item[i] == 'N') {
                source = _dists.nouns;
            } else if (syntax.item[i] == ',') {
                _erase(1);
                _write(", ", 2);
                continue;
            } else if (syntax.item[i] == ' ') {
                continue;
            } else {
                throw "unknown token";
            }
            auto word = _rand(source);
            _write(word.item, word.size);
            _write(" ", 1);
        }
    }

    void _generate_verb_phrase() {
        auto syntax = _rand(_dists.verb_phrase);
        text_dist source;
        for (int i = 0; i < syntax.size; i += 2) {
            if (syntax.item[i] == 'D') {
                source = _dists.adverbs;
            } else if (syntax.item[i] == 'V') {
                source = _dists.verbs;
            } else if (syntax.item[i] == 'X') {
                source = _dists.auxiliaries;
            } else {
                throw "unknown token";
            }
            auto word = _rand(source);
            _write(word.item, word.size);
            _write(" ", 1);
        }
    }

    void _generate_sentence() {
        auto syntax = _rand(_dists.grammars);
        for (int i = 0; i < syntax.size; i += 2) {
            if (syntax.item[i] == 'V') {
                _generate_verb_phrase();
            } else if (syntax.item[i] == 'N') {
                _generate_noun_phrase();
            } else if (syntax.item[i] == 'P') {
                auto preposition = _rand(_dists.prepositions);
                _write(preposition.item, preposition.size);
                _write(" the ", 5);
                _generate_noun_phrase();
            } else if (syntax.item[i] == 'T') {
                _erase(1);
                auto terminator = _rand(_dists.terminators);
                _write(terminator.item, terminator.size);
            } else {
                throw "unknown token";
            }
            if (_last != ' ') {
                _write(" ", 1);
            }
        }
    }

    char * const _buf;
    const int _size;
    const text_dists& _dists;

    static constexpr int64_t _initial_seed = 933588178;

    int _pos;
    char _last;
    int64_t _seed;
};

///

typedef struct _tpch_state {
} _tpch_state;

static inline _tpch_state * get_tpch_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (_tpch_state *)state;
}

//

static PyObject * gen_text_pool(PyObject *self, PyObject *args)
{
    return Py_BuildValue("k", 424);
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
    {"gen_text_pool", gen_text_pool, METH_NOARGS, "gen_text_pool"},
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
