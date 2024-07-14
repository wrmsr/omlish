from cpython.bytearray cimport PyByteArray_AsString
from cpython.bytes cimport PyBytes_AsString
from cpython.mem cimport PyMem_Free
from cpython.mem cimport PyMem_Malloc
from libc.string cimport memcpy


DEF INT_MULTIPLIER = 16807L
DEF INT_MODULUS = 2147483647L


cdef class IntGen:

    cdef public int _expected_usage_per_row
    cdef public long _seed
    cdef public int _usage

    def __init__(self, long seed, int expected_usage_per_row):
        self._seed = seed
        self._expected_usage_per_row = expected_usage_per_row
        self._usage = 0

    cpdef long next(self):
        if self._usage >= self._expected_usage_per_row:
            raise ValueError('Expected random to be used only %s times per row' % (self._expected_usage_per_row,))
        self._seed = (self._seed * INT_MULTIPLIER) % INT_MODULUS
        self._usage += 1
        return self._seed

    cpdef int rand(self, int low_value, int high_value):
        self.next()
        double_range = <double> (high_value - low_value + 1)
        value_in_range = <int> ((1.0 * self._seed / INT_MODULUS) * double_range)
        return low_value + value_in_range

    cdef void _advance_seed(self, long count):
        multiplier = INT_MULTIPLIER
        while count > 0:
            if count % 2 != 0:
                self._seed = (multiplier * self._seed) % INT_MODULUS
            count = count // 2
            multiplier = (multiplier * multiplier) % INT_MODULUS

    cpdef void row_finished(self):
        self._advance_seed(self._expected_usage_per_row - self._usage)
        self._usage = 0

    cpdef void advance_rows(self, long row_count):
        if self._usage != 0:
            self.row_finished()
        self._advance_seed(self._expected_usage_per_row * row_count)


DEF LONG_MULTIPLIER = 6364136223846793005L
DEF LONG_MULTIPLIER_32 = 16807
DEF LONG_MODULUS_32 = 2147483647


cdef class LongGen:

    cdef public int _expected_usage_per_row
    cdef public long _seed
    cdef public int _usage

    def __init__(self, long seed, int expected_usage_per_row):
        self._seed = seed
        self._expected_usage_per_row = expected_usage_per_row
        self._usage = 0

    cpdef long next(self):
        if self._usage >= self._expected_usage_per_row:
            raise ValueError('Expected random to be used only %s times per row' % (self._expected_usage_per_row,))
        self._seed = (self._seed * LONG_MULTIPLIER) + 1
        self._usage += 1
        return self._seed

    cpdef long rand(self, long low_value, long high_value):
        self.next()
        value_in_range = abs(self._seed) % (high_value - low_value + 1)
        return low_value + value_in_range

    cdef void _advance_seed(self, long count):
        multiplier = LONG_MULTIPLIER_32
        while count > 0:
            if count % 2 != 0:
                seed = (multiplier * seed) % LONG_MODULUS_32
            count = count // 2
            multiplier = (multiplier * multiplier) % LONG_MODULUS_32

    cpdef void row_finished(self):
        self._advance_seed(self._expected_usage_per_row - self._usage)
        usage = 0

    cpdef void advance_rows(self, long row_count):
        if self._usage != 0:
            self.row_finished()
        self._advance_seed(self._expected_usage_per_row * row_count)


cdef struct TextDistItem:
    char* item
    int size


cdef class TextDist:

    cdef public list lst
    cdef public int size
    cdef TextDistItem* items

    def __init__(self, items):
        self.lst = list(items)
        self.size = len(self.lst)

        self.items = <TextDistItem*> PyMem_Malloc(sizeof(TextDistItem) * self.size)
        for i, item in enumerate(self.lst):
            self.items[i].item = PyBytes_AsString(self.lst[i])
            self.items[i].size = len(self.lst[i])

    def __dealloc__(self):
        PyMem_Free(self.items)


cdef class TextDists:

    cpdef public TextDist adjectives
    cpdef public TextDist adverbs
    cpdef public TextDist articles
    cpdef public TextDist auxiliaries
    cpdef public TextDist grammars
    cpdef public TextDist noun_phrase
    cpdef public TextDist nouns
    cpdef public TextDist prepositions
    cpdef public TextDist terminators
    cpdef public TextDist verb_phrase
    cpdef public TextDist verbs


cpdef cppclass TextPoolGen:

    bytearray _buf
    TextDists _dists
    char* _base
    int _pos
    char _last
    long _seed

    __init__(bytearray buf, int size, dists: TextDists):
        this._buf = buf
        this._dists = dists
        this._base = PyByteArray_AsString(this._buf)
        this._pos = 0
        this._last = 0
        this._seed = 933588178

        while this._pos < size:
            this._generate_sentence()

        del this._buf[size:]

    void _write(char* p, int sz):
        if not sz:
            return
        memcpy(this._base + this._pos, p, sz)
        this._pos += sz
        this._last = this._base[this._pos - 1]

    void _erase(int i):
        if i > this._pos:
            raise ValueError(i)
        this._pos -= i
        if this._pos:
            this._last = this._buf[this._pos - 1]
        else:
            this._last = 0

    TextDistItem _rand(TextDist dist):
        this._seed = (this._seed * INT_MULTIPLIER) % INT_MODULUS
        double_range = <double> dist.size
        idx = <int> ((1.0 * this._seed / INT_MODULUS) * double_range)
        return dist.items[idx]

    void _generate_sentence():
        syntax = this._rand(this._dists.grammars)
        for i in range(0, syntax.size, 2):
            if syntax.item[i] == ord('V'):
                this._generate_verb_phrase()
            elif syntax.item[i] == ord('N'):
                this._generate_noun_phrase()
            elif syntax.item[i] == ord('P'):
                preposition = this._rand(this._dists.prepositions)
                this._write(preposition.item, preposition.size)
                this._write(' the ', 5)
                this._generate_noun_phrase()
            elif syntax.item[i] == ord('T'):
                this._erase(1)
                terminator = this._rand(this._dists.terminators)
                this._write(terminator.item, terminator.size)
            else:
                raise ValueError(f'Unknown token "{syntax.item[i]}"')
            if this._last != ord(' '):
                this._write(' ', 1)

    void _generate_verb_phrase():
        syntax = this._rand(this._dists.verb_phrase)
        for i in range(0, syntax.size, 2):
            if syntax.item[i] == ord('D'):
                source = this._dists.adverbs
            elif syntax.item[i] == ord('V'):
                source = this._dists.verbs
            elif syntax.item[i] == ord('X'):
                source = this._dists.auxiliaries
            else:
                raise ValueError(f'Unknown token "{syntax.item[i]}"')
            word = this._rand(source)
            this._write(word.item, word.size)
            this._write(' ', 1)

    void _generate_noun_phrase():
        syntax = this._rand(this._dists.noun_phrase)
        for i in range(0, syntax.size):
            if syntax.item[i] == ord('A'):
                source = this._dists.articles
            elif syntax.item[i] == ord('J'):
                source = this._dists.adjectives
            elif syntax.item[i] == ord('D'):
                source = this._dists.adverbs
            elif syntax.item[i] == ord('N'):
                source = this._dists.nouns
            elif syntax.item[i] == ord(','):
                this._erase(1)
                this._write(', ', 2)
                continue
            elif syntax.item[i] == ord(' '):
                continue
            else:
                raise ValueError(f'Unknown token "{syntax.item[i]}"')
            word = this._rand(source)
            this._write(word.item, word.size)
            this._write(' ', 1)


cpdef bytearray gen_text_pool(int size, int max_sentence_length, TextDists dists):
    buf = bytearray(size + max_sentence_length)
    TextPoolGen(buf, size, dists)
    return buf
