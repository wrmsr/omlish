import os

from .._itertools import always_iterable


def gen_preprocess_options(macros, include_dirs):
    """Generate C pre-processor options (-D, -U, -I) as used by at least
    two types of compilers: the typical Unix compiler and Visual C++.
    'macros' is the usual thing, a list of 1- or 2-tuples, where (name,)
    means undefine (-U) macro 'name', and (name,value) means define (-D)
    macro 'name' to 'value'.  'include_dirs' is just a list of directory
    names to be added to the header file search path (-I).  Returns a list
    of command-line options suitable for either Unix compilers or Visual
    C++.
    """
    # XXX it would be nice (mainly aesthetic, and so we don't generate
    # stupid-looking command lines) to go over 'macros' and eliminate
    # redundant definitions/undefinitions (ie. ensure that only the
    # latest mention of a particular macro winds up on the command
    # line).  I don't think it's essential, though, since most (all?)
    # Unix C compilers only pay attention to the latest -D or -U
    # mention of a macro on their command line.  Similar situation for
    # 'include_dirs'.  I'm punting on both for now.  Anyways, weeding out
    # redundancies like this should probably be the province of
    # CCompiler, since the data structures used are inherited from it
    # and therefore common to all CCompiler classes.
    pp_opts = []
    for macro in macros:
        if not (isinstance(macro, tuple) and 1 <= len(macro) <= 2):
            raise TypeError(
                "bad macro definition '%s': "
                "each element of 'macros' list must be a 1- or 2-tuple" % macro
            )

        if len(macro) == 1:  # undefine this macro
            pp_opts.append("-U%s" % macro[0])
        elif len(macro) == 2:
            if macro[1] is None:  # define with no explicit value
                pp_opts.append("-D%s" % macro[0])
            else:
                # XXX *don't* need to be clever about quoting the
                # macro value here, because we're going to avoid the
                # shell at all costs when we spawn the command!
                pp_opts.append("-D{}={}".format(*macro))

    for dir in include_dirs:
        pp_opts.append("-I%s" % dir)
    return pp_opts


def gen_lib_options(compiler, library_dirs, runtime_library_dirs, libraries):
    """Generate linker options for searching library directories and
    linking with specific libraries.  'libraries' and 'library_dirs' are,
    respectively, lists of library names (not filenames!) and search
    directories.  Returns a list of command-line options suitable for use
    with some compiler (depending on the two format strings passed in).
    """
    lib_opts = []

    for dir in library_dirs:
        lib_opts.append(compiler.library_dir_option(dir))

    for dir in runtime_library_dirs:
        lib_opts.extend(always_iterable(compiler.runtime_library_dir_option(dir)))

    # XXX it's important that we *not* remove redundant library mentions!
    # sometimes you really do have to say "-lfoo -lbar -lfoo" in order to
    # resolve all symbols.  I just hope we never have to say "-lfoo obj.o
    # -lbar" to get things to work -- that's certainly a possibility, but a
    # pretty nasty way to arrange your C code.

    for lib in libraries:
        (lib_dir, lib_name) = os.path.split(lib)
        if lib_dir:
            lib_file = compiler.find_library_file([lib_dir], lib_name)
            if lib_file:
                lib_opts.append(lib_file)
            else:
                compiler.warn(
                    "no library file corresponding to '%s' found (skipping)" % lib
                )
        else:
            lib_opts.append(compiler.library_option(lib))
    return lib_opts
