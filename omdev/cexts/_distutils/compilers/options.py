import os
import typing as ta

from ..util import always_iterable


##


Macro: ta.TypeAlias = tuple[str, str | None] | tuple[str]


def gen_preprocess_options(
        macros: list[Macro],
        include_dirs: list[str],
) -> list[str]:
    """
    Generate C pre-processor options (-D, -U, -I) as used by at least two types of compilers: the typical Unix compiler
    and Visual C++. 'macros' is the usual thing, a list of 1- or 2-tuples, where (name,) means undefine (-U) macro
    'name', and (name,value) means define (-D) macro 'name' to 'value'.  'include_dirs' is just a list of directory
    names to be added to the header file search path (-I).  Returns a list of command-line options suitable for either
    Unix compilers or Visual C++.
    """
    # it would be nice (mainly aesthetic, and so we don't generate stupid-looking command lines) to go over 'macros' and
    # eliminate redundant definitions/undefinitions (ie. ensure that only the latest mention of a particular macro winds
    # up on the command line).  I don't think it's essential, though, since most (all?) Unix C compilers only pay
    # attention to the latest -D or -U mention of a macro on their command line.  Similar situation for 'include_dirs'.
    # I'm punting on both for now.  Anyways, weeding out redundancies like this should probably be the province of
    # CCompiler, since the data structures used are inherited from it and therefore common to all CCompiler classes.
    pp_opts: list[str] = []
    for macro in macros:
        if not (isinstance(macro, tuple) and 1 <= len(macro) <= 2):
            raise TypeError(f"bad macro definition '{macro}': each element of 'macros' list must be a 1- or 2-tuple")

        if len(macro) == 1:  # undefine this macro
            pp_opts.append(f'-U{macro[0]}')
        elif len(macro) == 2:
            if macro[1] is None:  # define with no explicit value
                pp_opts.append(f'-D{macro[0]}')
            else:
                # *don't* need to be clever about quoting the macro value here, because we're going to avoid the shell
                # at all costs when we spawn the command!
                pp_opts.append('-D{}={}'.format(*macro))

    for dir in include_dirs:  # noqa
        pp_opts.append(f'-I{dir}')
    return pp_opts


def gen_lib_options(
        compiler,
        library_dirs: list[str],
        runtime_library_dirs: list[str],
        libraries: list[str],
) -> list[str]:
    """
    Generate linker options for searching library directories and linking with specific libraries.  'libraries' and
    'library_dirs' are, respectively, lists of library names (not filenames!) and search directories.  Returns a list of
    command-line options suitable for use with some compiler (depending on the two format strings passed in).
    """
    lib_opts = []

    for dir in library_dirs:  # noqa
        lib_opts.append(compiler.library_dir_option(dir))

    for dir in runtime_library_dirs:  # noqa
        lib_opts.extend(always_iterable(compiler.runtime_library_dir_option(dir)))

    # it's important that we *not* remove redundant library mentions! sometimes you really do have to say "-lfoo -lbar
    # -lfoo" in order to resolve all symbols.  I just hope we never have to say "-lfoo obj.o -lbar" to get things to
    # work -- that's certainly a possibility, but a pretty nasty way to arrange your C code.

    for lib in libraries:
        (lib_dir, lib_name) = os.path.split(lib)
        if lib_dir:
            lib_file = compiler.find_library_file([lib_dir], lib_name)
            if lib_file:
                lib_opts.append(lib_file)
            else:
                compiler.warn(f"no library file corresponding to '{lib}' found (skipping)")
        else:
            lib_opts.append(compiler.library_option(lib))
    return lib_opts
