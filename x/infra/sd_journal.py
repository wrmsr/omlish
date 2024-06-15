# -*- coding: utf-8 -*-
#
# TARGET arch is: []
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes


class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                if not hasattr(type_, "as_dict"):
                    value = [v for v in value]
                else:
                    type_ = type_._type_
                    value = [type_.as_dict(v) for v in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass



def string_cast(char_pointer, encoding='utf-8', errors='strict'):
    value = ctypes.cast(char_pointer, ctypes.c_char_p).value
    if value is not None and encoding is not None:
        value = value.decode(encoding, errors=errors)
    return value


def char_pointer_cast(string, encoding='utf-8'):
    if encoding is not None:
        try:
            string = string.encode(encoding)
        except AttributeError:
            # In Python3, bytes has no encode attribute
            pass
    string = ctypes.c_char_p(string)
    return ctypes.cast(string, ctypes.POINTER(ctypes.c_char))



class FunctionFactoryStub:
    def __getattr__(self, _):
      return ctypes.CFUNCTYPE(lambda y:y)

# libraries['FIXME_STUB'] explanation
# As you did not list (-l libraryname.so) a library that exports this function
# This is a non-working stub instead. 
# You can either re-run clan2py with -l /path/to/library.so
# Or manually fix this by comment the ctypes.CDLL loading
_libraries = {}
_libraries['FIXME_STUB'] = FunctionFactoryStub() #  ctypes.CDLL('FIXME_STUB')
c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 16:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*16



class struct__sd_useless_struct_to_allow_trailing_semicolon_(Structure):
    pass

try:
    sd_journal_print = _libraries['FIXME_STUB'].sd_journal_print
    sd_journal_print.restype = ctypes.c_int32
    sd_journal_print.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
class struct___va_list_tag(Structure):
    pass

struct___va_list_tag._pack_ = 1 # source:False
struct___va_list_tag._fields_ = [
    ('gp_offset', ctypes.c_uint32),
    ('fp_offset', ctypes.c_uint32),
    ('overflow_arg_area', ctypes.POINTER(None)),
    ('reg_save_area', ctypes.POINTER(None)),
]

va_list = struct___va_list_tag * 1
try:
    sd_journal_printv = _libraries['FIXME_STUB'].sd_journal_printv
    sd_journal_printv.restype = ctypes.c_int32
    sd_journal_printv.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_char), va_list]
except AttributeError:
    pass
try:
    sd_journal_send = _libraries['FIXME_STUB'].sd_journal_send
    sd_journal_send.restype = ctypes.c_int32
    sd_journal_send.argtypes = [ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
class struct_iovec(Structure):
    pass

struct_iovec._pack_ = 1 # source:False
struct_iovec._fields_ = [
    ('iov_base', ctypes.POINTER(None)),
    ('iov_len', ctypes.c_uint64),
]

try:
    sd_journal_sendv = _libraries['FIXME_STUB'].sd_journal_sendv
    sd_journal_sendv.restype = ctypes.c_int32
    sd_journal_sendv.argtypes = [ctypes.POINTER(struct_iovec), ctypes.c_int32]
except AttributeError:
    pass
try:
    sd_journal_perror = _libraries['FIXME_STUB'].sd_journal_perror
    sd_journal_perror.restype = ctypes.c_int32
    sd_journal_perror.argtypes = [ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    sd_journal_print_with_location = _libraries['FIXME_STUB'].sd_journal_print_with_location
    sd_journal_print_with_location.restype = ctypes.c_int32
    sd_journal_print_with_location.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    sd_journal_printv_with_location = _libraries['FIXME_STUB'].sd_journal_printv_with_location
    sd_journal_printv_with_location.restype = ctypes.c_int32
    sd_journal_printv_with_location.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), va_list]
except AttributeError:
    pass
try:
    sd_journal_send_with_location = _libraries['FIXME_STUB'].sd_journal_send_with_location
    sd_journal_send_with_location.restype = ctypes.c_int32
    sd_journal_send_with_location.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    sd_journal_sendv_with_location = _libraries['FIXME_STUB'].sd_journal_sendv_with_location
    sd_journal_sendv_with_location.restype = ctypes.c_int32
    sd_journal_sendv_with_location.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(struct_iovec), ctypes.c_int32]
except AttributeError:
    pass
try:
    sd_journal_perror_with_location = _libraries['FIXME_STUB'].sd_journal_perror_with_location
    sd_journal_perror_with_location.restype = ctypes.c_int32
    sd_journal_perror_with_location.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    sd_journal_stream_fd = _libraries['FIXME_STUB'].sd_journal_stream_fd
    sd_journal_stream_fd.restype = ctypes.c_int32
    sd_journal_stream_fd.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int32, ctypes.c_int32]
except AttributeError:
    pass
class struct_sd_journal(Structure):
    pass

sd_journal = struct_sd_journal

# values for enumeration 'c__Ea_SD_JOURNAL_LOCAL_ONLY'
c__Ea_SD_JOURNAL_LOCAL_ONLY__enumvalues = {
    1: 'SD_JOURNAL_LOCAL_ONLY',
    2: 'SD_JOURNAL_RUNTIME_ONLY',
    4: 'SD_JOURNAL_SYSTEM',
    8: 'SD_JOURNAL_CURRENT_USER',
    16: 'SD_JOURNAL_OS_ROOT',
    32: 'SD_JOURNAL_ALL_NAMESPACES',
    64: 'SD_JOURNAL_INCLUDE_DEFAULT_NAMESPACE',
    4: 'SD_JOURNAL_SYSTEM_ONLY',
}
SD_JOURNAL_LOCAL_ONLY = 1
SD_JOURNAL_RUNTIME_ONLY = 2
SD_JOURNAL_SYSTEM = 4
SD_JOURNAL_CURRENT_USER = 8
SD_JOURNAL_OS_ROOT = 16
SD_JOURNAL_ALL_NAMESPACES = 32
SD_JOURNAL_INCLUDE_DEFAULT_NAMESPACE = 64
SD_JOURNAL_SYSTEM_ONLY = 4
c__Ea_SD_JOURNAL_LOCAL_ONLY = ctypes.c_uint32 # enum

# values for enumeration 'c__Ea_SD_JOURNAL_NOP'
c__Ea_SD_JOURNAL_NOP__enumvalues = {
    0: 'SD_JOURNAL_NOP',
    1: 'SD_JOURNAL_APPEND',
    2: 'SD_JOURNAL_INVALIDATE',
}
SD_JOURNAL_NOP = 0
SD_JOURNAL_APPEND = 1
SD_JOURNAL_INVALIDATE = 2
c__Ea_SD_JOURNAL_NOP = ctypes.c_uint32 # enum
try:
    sd_journal_open = _libraries['FIXME_STUB'].sd_journal_open
    sd_journal_open.restype = ctypes.c_int32
    sd_journal_open.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_sd_journal)), ctypes.c_int32]
except AttributeError:
    pass
try:
    sd_journal_open_namespace = _libraries['FIXME_STUB'].sd_journal_open_namespace
    sd_journal_open_namespace.restype = ctypes.c_int32
    sd_journal_open_namespace.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_sd_journal)), ctypes.POINTER(ctypes.c_char), ctypes.c_int32]
except AttributeError:
    pass
try:
    sd_journal_open_directory = _libraries['FIXME_STUB'].sd_journal_open_directory
    sd_journal_open_directory.restype = ctypes.c_int32
    sd_journal_open_directory.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_sd_journal)), ctypes.POINTER(ctypes.c_char), ctypes.c_int32]
except AttributeError:
    pass
try:
    sd_journal_open_directory_fd = _libraries['FIXME_STUB'].sd_journal_open_directory_fd
    sd_journal_open_directory_fd.restype = ctypes.c_int32
    sd_journal_open_directory_fd.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_sd_journal)), ctypes.c_int32, ctypes.c_int32]
except AttributeError:
    pass
try:
    sd_journal_open_files = _libraries['FIXME_STUB'].sd_journal_open_files
    sd_journal_open_files.restype = ctypes.c_int32
    sd_journal_open_files.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_sd_journal)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)), ctypes.c_int32]
except AttributeError:
    pass
try:
    sd_journal_open_files_fd = _libraries['FIXME_STUB'].sd_journal_open_files_fd
    sd_journal_open_files_fd.restype = ctypes.c_int32
    sd_journal_open_files_fd.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_sd_journal)), ctypes.c_int32 * 0, ctypes.c_uint32, ctypes.c_int32]
except AttributeError:
    pass
try:
    sd_journal_open_container = _libraries['FIXME_STUB'].sd_journal_open_container
    sd_journal_open_container.restype = ctypes.c_int32
    sd_journal_open_container.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_sd_journal)), ctypes.POINTER(ctypes.c_char), ctypes.c_int32]
except AttributeError:
    pass
try:
    sd_journal_close = _libraries['FIXME_STUB'].sd_journal_close
    sd_journal_close.restype = None
    sd_journal_close.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_previous = _libraries['FIXME_STUB'].sd_journal_previous
    sd_journal_previous.restype = ctypes.c_int32
    sd_journal_previous.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_next = _libraries['FIXME_STUB'].sd_journal_next
    sd_journal_next.restype = ctypes.c_int32
    sd_journal_next.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
uint64_t = ctypes.c_uint64
try:
    sd_journal_previous_skip = _libraries['FIXME_STUB'].sd_journal_previous_skip
    sd_journal_previous_skip.restype = ctypes.c_int32
    sd_journal_previous_skip.argtypes = [ctypes.POINTER(struct_sd_journal), uint64_t]
except AttributeError:
    pass
try:
    sd_journal_next_skip = _libraries['FIXME_STUB'].sd_journal_next_skip
    sd_journal_next_skip.restype = ctypes.c_int32
    sd_journal_next_skip.argtypes = [ctypes.POINTER(struct_sd_journal), uint64_t]
except AttributeError:
    pass
try:
    sd_journal_get_realtime_usec = _libraries['FIXME_STUB'].sd_journal_get_realtime_usec
    sd_journal_get_realtime_usec.restype = ctypes.c_int32
    sd_journal_get_realtime_usec.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
class union_sd_id128(Union):
    pass

union_sd_id128._pack_ = 1 # source:False
union_sd_id128._fields_ = [
    ('bytes', ctypes.c_ubyte * 16),
    ('qwords', ctypes.c_uint64 * 2),
]

try:
    sd_journal_get_monotonic_usec = _libraries['FIXME_STUB'].sd_journal_get_monotonic_usec
    sd_journal_get_monotonic_usec.restype = ctypes.c_int32
    sd_journal_get_monotonic_usec.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(union_sd_id128)]
except AttributeError:
    pass
size_t = ctypes.c_uint64
try:
    sd_journal_set_data_threshold = _libraries['FIXME_STUB'].sd_journal_set_data_threshold
    sd_journal_set_data_threshold.restype = ctypes.c_int32
    sd_journal_set_data_threshold.argtypes = [ctypes.POINTER(struct_sd_journal), size_t]
except AttributeError:
    pass
try:
    sd_journal_get_data_threshold = _libraries['FIXME_STUB'].sd_journal_get_data_threshold
    sd_journal_get_data_threshold.restype = ctypes.c_int32
    sd_journal_get_data_threshold.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    sd_journal_get_data = _libraries['FIXME_STUB'].sd_journal_get_data
    sd_journal_get_data.restype = ctypes.c_int32
    sd_journal_get_data.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    sd_journal_enumerate_data = _libraries['FIXME_STUB'].sd_journal_enumerate_data
    sd_journal_enumerate_data.restype = ctypes.c_int32
    sd_journal_enumerate_data.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    sd_journal_enumerate_available_data = _libraries['FIXME_STUB'].sd_journal_enumerate_available_data
    sd_journal_enumerate_available_data.restype = ctypes.c_int32
    sd_journal_enumerate_available_data.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    sd_journal_restart_data = _libraries['FIXME_STUB'].sd_journal_restart_data
    sd_journal_restart_data.restype = None
    sd_journal_restart_data.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_add_match = _libraries['FIXME_STUB'].sd_journal_add_match
    sd_journal_add_match.restype = ctypes.c_int32
    sd_journal_add_match.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(None), size_t]
except AttributeError:
    pass
try:
    sd_journal_add_disjunction = _libraries['FIXME_STUB'].sd_journal_add_disjunction
    sd_journal_add_disjunction.restype = ctypes.c_int32
    sd_journal_add_disjunction.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_add_conjunction = _libraries['FIXME_STUB'].sd_journal_add_conjunction
    sd_journal_add_conjunction.restype = ctypes.c_int32
    sd_journal_add_conjunction.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_flush_matches = _libraries['FIXME_STUB'].sd_journal_flush_matches
    sd_journal_flush_matches.restype = None
    sd_journal_flush_matches.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_seek_head = _libraries['FIXME_STUB'].sd_journal_seek_head
    sd_journal_seek_head.restype = ctypes.c_int32
    sd_journal_seek_head.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_seek_tail = _libraries['FIXME_STUB'].sd_journal_seek_tail
    sd_journal_seek_tail.restype = ctypes.c_int32
    sd_journal_seek_tail.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
sd_id128_t = union_sd_id128
try:
    sd_journal_seek_monotonic_usec = _libraries['FIXME_STUB'].sd_journal_seek_monotonic_usec
    sd_journal_seek_monotonic_usec.restype = ctypes.c_int32
    sd_journal_seek_monotonic_usec.argtypes = [ctypes.POINTER(struct_sd_journal), sd_id128_t, uint64_t]
except AttributeError:
    pass
try:
    sd_journal_seek_realtime_usec = _libraries['FIXME_STUB'].sd_journal_seek_realtime_usec
    sd_journal_seek_realtime_usec.restype = ctypes.c_int32
    sd_journal_seek_realtime_usec.argtypes = [ctypes.POINTER(struct_sd_journal), uint64_t]
except AttributeError:
    pass
try:
    sd_journal_seek_cursor = _libraries['FIXME_STUB'].sd_journal_seek_cursor
    sd_journal_seek_cursor.restype = ctypes.c_int32
    sd_journal_seek_cursor.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    sd_journal_get_cursor = _libraries['FIXME_STUB'].sd_journal_get_cursor
    sd_journal_get_cursor.restype = ctypes.c_int32
    sd_journal_get_cursor.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
except AttributeError:
    pass
try:
    sd_journal_test_cursor = _libraries['FIXME_STUB'].sd_journal_test_cursor
    sd_journal_test_cursor.restype = ctypes.c_int32
    sd_journal_test_cursor.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    sd_journal_get_cutoff_realtime_usec = _libraries['FIXME_STUB'].sd_journal_get_cutoff_realtime_usec
    sd_journal_get_cutoff_realtime_usec.restype = ctypes.c_int32
    sd_journal_get_cutoff_realtime_usec.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    sd_journal_get_cutoff_monotonic_usec = _libraries['FIXME_STUB'].sd_journal_get_cutoff_monotonic_usec
    sd_journal_get_cutoff_monotonic_usec.restype = ctypes.c_int32
    sd_journal_get_cutoff_monotonic_usec.argtypes = [ctypes.POINTER(struct_sd_journal), sd_id128_t, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    sd_journal_get_usage = _libraries['FIXME_STUB'].sd_journal_get_usage
    sd_journal_get_usage.restype = ctypes.c_int32
    sd_journal_get_usage.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    sd_journal_query_unique = _libraries['FIXME_STUB'].sd_journal_query_unique
    sd_journal_query_unique.restype = ctypes.c_int32
    sd_journal_query_unique.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    sd_journal_enumerate_unique = _libraries['FIXME_STUB'].sd_journal_enumerate_unique
    sd_journal_enumerate_unique.restype = ctypes.c_int32
    sd_journal_enumerate_unique.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    sd_journal_enumerate_available_unique = _libraries['FIXME_STUB'].sd_journal_enumerate_available_unique
    sd_journal_enumerate_available_unique.restype = ctypes.c_int32
    sd_journal_enumerate_available_unique.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    sd_journal_restart_unique = _libraries['FIXME_STUB'].sd_journal_restart_unique
    sd_journal_restart_unique.restype = None
    sd_journal_restart_unique.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_enumerate_fields = _libraries['FIXME_STUB'].sd_journal_enumerate_fields
    sd_journal_enumerate_fields.restype = ctypes.c_int32
    sd_journal_enumerate_fields.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
except AttributeError:
    pass
try:
    sd_journal_restart_fields = _libraries['FIXME_STUB'].sd_journal_restart_fields
    sd_journal_restart_fields.restype = None
    sd_journal_restart_fields.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_get_fd = _libraries['FIXME_STUB'].sd_journal_get_fd
    sd_journal_get_fd.restype = ctypes.c_int32
    sd_journal_get_fd.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_get_events = _libraries['FIXME_STUB'].sd_journal_get_events
    sd_journal_get_events.restype = ctypes.c_int32
    sd_journal_get_events.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_get_timeout = _libraries['FIXME_STUB'].sd_journal_get_timeout
    sd_journal_get_timeout.restype = ctypes.c_int32
    sd_journal_get_timeout.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    sd_journal_process = _libraries['FIXME_STUB'].sd_journal_process
    sd_journal_process.restype = ctypes.c_int32
    sd_journal_process.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_wait = _libraries['FIXME_STUB'].sd_journal_wait
    sd_journal_wait.restype = ctypes.c_int32
    sd_journal_wait.argtypes = [ctypes.POINTER(struct_sd_journal), uint64_t]
except AttributeError:
    pass
try:
    sd_journal_reliable_fd = _libraries['FIXME_STUB'].sd_journal_reliable_fd
    sd_journal_reliable_fd.restype = ctypes.c_int32
    sd_journal_reliable_fd.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_get_catalog = _libraries['FIXME_STUB'].sd_journal_get_catalog
    sd_journal_get_catalog.restype = ctypes.c_int32
    sd_journal_get_catalog.argtypes = [ctypes.POINTER(struct_sd_journal), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
except AttributeError:
    pass
try:
    sd_journal_get_catalog_for_message_id = _libraries['FIXME_STUB'].sd_journal_get_catalog_for_message_id
    sd_journal_get_catalog_for_message_id.restype = ctypes.c_int32
    sd_journal_get_catalog_for_message_id.argtypes = [sd_id128_t, ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
except AttributeError:
    pass
try:
    sd_journal_has_runtime_files = _libraries['FIXME_STUB'].sd_journal_has_runtime_files
    sd_journal_has_runtime_files.restype = ctypes.c_int32
    sd_journal_has_runtime_files.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_has_persistent_files = _libraries['FIXME_STUB'].sd_journal_has_persistent_files
    sd_journal_has_persistent_files.restype = ctypes.c_int32
    sd_journal_has_persistent_files.argtypes = [ctypes.POINTER(struct_sd_journal)]
except AttributeError:
    pass
try:
    sd_journal_closep = _libraries['FIXME_STUB'].sd_journal_closep
    sd_journal_closep.restype = None
    sd_journal_closep.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_sd_journal))]
except AttributeError:
    pass
__all__ = \
    ['SD_JOURNAL_ALL_NAMESPACES', 'SD_JOURNAL_APPEND',
    'SD_JOURNAL_CURRENT_USER', 'SD_JOURNAL_INCLUDE_DEFAULT_NAMESPACE',
    'SD_JOURNAL_INVALIDATE', 'SD_JOURNAL_LOCAL_ONLY',
    'SD_JOURNAL_NOP', 'SD_JOURNAL_OS_ROOT', 'SD_JOURNAL_RUNTIME_ONLY',
    'SD_JOURNAL_SYSTEM', 'SD_JOURNAL_SYSTEM_ONLY',
    'c__Ea_SD_JOURNAL_LOCAL_ONLY', 'c__Ea_SD_JOURNAL_NOP',
    'sd_id128_t', 'sd_journal', 'sd_journal_add_conjunction',
    'sd_journal_add_disjunction', 'sd_journal_add_match',
    'sd_journal_close', 'sd_journal_closep',
    'sd_journal_enumerate_available_data',
    'sd_journal_enumerate_available_unique',
    'sd_journal_enumerate_data', 'sd_journal_enumerate_fields',
    'sd_journal_enumerate_unique', 'sd_journal_flush_matches',
    'sd_journal_get_catalog', 'sd_journal_get_catalog_for_message_id',
    'sd_journal_get_cursor', 'sd_journal_get_cutoff_monotonic_usec',
    'sd_journal_get_cutoff_realtime_usec', 'sd_journal_get_data',
    'sd_journal_get_data_threshold', 'sd_journal_get_events',
    'sd_journal_get_fd', 'sd_journal_get_monotonic_usec',
    'sd_journal_get_realtime_usec', 'sd_journal_get_timeout',
    'sd_journal_get_usage', 'sd_journal_has_persistent_files',
    'sd_journal_has_runtime_files', 'sd_journal_next',
    'sd_journal_next_skip', 'sd_journal_open',
    'sd_journal_open_container', 'sd_journal_open_directory',
    'sd_journal_open_directory_fd', 'sd_journal_open_files',
    'sd_journal_open_files_fd', 'sd_journal_open_namespace',
    'sd_journal_perror', 'sd_journal_perror_with_location',
    'sd_journal_previous', 'sd_journal_previous_skip',
    'sd_journal_print', 'sd_journal_print_with_location',
    'sd_journal_printv', 'sd_journal_printv_with_location',
    'sd_journal_process', 'sd_journal_query_unique',
    'sd_journal_reliable_fd', 'sd_journal_restart_data',
    'sd_journal_restart_fields', 'sd_journal_restart_unique',
    'sd_journal_seek_cursor', 'sd_journal_seek_head',
    'sd_journal_seek_monotonic_usec', 'sd_journal_seek_realtime_usec',
    'sd_journal_seek_tail', 'sd_journal_send',
    'sd_journal_send_with_location', 'sd_journal_sendv',
    'sd_journal_sendv_with_location', 'sd_journal_set_data_threshold',
    'sd_journal_stream_fd', 'sd_journal_test_cursor',
    'sd_journal_wait', 'size_t', 'struct___va_list_tag',
    'struct__sd_useless_struct_to_allow_trailing_semicolon_',
    'struct_iovec', 'struct_sd_journal', 'uint64_t', 'union_sd_id128',
    'va_list']
