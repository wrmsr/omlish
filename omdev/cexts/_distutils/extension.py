"""Provides the Extension class, used to describe C/C++ extension modules in setup scripts."""
import warnings


##


class Extension:
    """
    Just a collection of attributes that describes an extension module and everything needed to build it (hopefully in a
    portable way, but there are hooks that let you be as unportable as you need).

    Instance attributes:
      name : string
        the full name of the extension, including any packages -- ie. *not* a filename or pathname, but Python dotted
        name
      sources : [string]
        list of source filenames, relative to the distribution root (where the setup script lives), in Unix form
        (slash-separated) for portability.  Source files may be C, C++, SWIG (.i), platform-specific resource files, or
        whatever else is recognized by the "build_ext" command as source for a Python extension.
      include_dirs : [string]
        list of directories to search for C/C++ header files (in Unix form for portability)
      define_macros : [(name : string, value : string|None)]
        list of macros to define; each macro is defined using a 2-tuple, where 'value' is either the string to define it
        to or None to define it without a particular value (equivalent of "#define FOO" in source or -DFOO on Unix C
        compiler command line)
      undef_macros : [string]
        list of macros to undefine explicitly
      library_dirs : [string]
        list of directories to search for C/C++ libraries at link time
      libraries : [string]
        list of library names (not filenames or paths) to link against
      runtime_library_dirs : [string]
        list of directories to search for C/C++ libraries at run time (for shared extensions, this is when the extension
        is loaded)
      extra_objects : [string]
        list of extra files to link with (eg. object files not implied by 'sources', static library that must be
        explicitly specified, binary resource files, etc.)
      extra_compile_args : [string]
        any extra platform- and compiler-specific information to use when compiling the source files in 'sources'.  For
        platforms and compilers where "command line" makes sense, this is typically a list of command-line arguments,
        but for other platforms it could be anything.
      extra_link_args : [string]
        any extra platform- and compiler-specific information to use when linking object files together to create the
        extension (or to create a new static Python interpreter).  Similar interpretation as for 'extra_compile_args'.
      export_symbols : [string]
        list of symbols to be exported from a shared extension.  Not used on all platforms, and not generally necessary
        for Python extensions, which typically export exactly one symbol: "init" + extension_name.
      swig_opts : [string]
        any extra options to pass to SWIG if a source file has the .i extension.
      depends : [string]
        list of files that the extension depends on
      language : string
        extension language (i.e. "c", "c++", "objc"). Will be detected from the source extensions if not provided.
      optional : boolean
        specifies that a build failure in the extension should not abort the build process, but simply not install the
        failing extension.
    """

    # When adding arguments to this constructor, be sure to update setup_keywords in core.py.
    def __init__(
            self,
            name: str,
            sources: list[str],
            include_dirs: list[str] | None = None,
            define_macros: list[tuple[str, str]] | None = None,
            undef_macros: list[str] | None = None,
            library_dirs: list[str] | None = None,
            libraries: list[str] | None = None,
            runtime_library_dirs: list[str] | None = None,
            extra_objects: list[str] | None = None,
            extra_compile_args: list[str] | None = None,
            extra_link_args: list[str] | None = None,
            export_symbols: list[str] | None = None,
            swig_opts: list[str] | None = None,
            depends: list[str] | None = None,
            language: str | None = None,
            optional: str | None = None,
            **kw,  # To catch unknown keywords
    ):
        if not isinstance(name, str):
            raise TypeError("'name' must be a string")
        if not (isinstance(sources, list) and all(isinstance(v, str) for v in sources)):
            raise TypeError("'sources' must be a list of strings")

        self.name = name
        self.sources = sources
        self.include_dirs = include_dirs or []
        self.define_macros = define_macros or []
        self.undef_macros = undef_macros or []
        self.library_dirs = library_dirs or []
        self.libraries = libraries or []
        self.runtime_library_dirs = runtime_library_dirs or []
        self.extra_objects = extra_objects or []
        self.extra_compile_args = extra_compile_args or []
        self.extra_link_args = extra_link_args or []
        self.export_symbols = export_symbols or []
        self.swig_opts = swig_opts or []
        self.depends = depends or []
        self.language = language
        self.optional = optional

        # If there are unknown keyword options, warn about them
        if len(kw) > 0:
            options = ', '.join(sorted([repr(option) for option in kw]))
            msg = f'Unknown Extension options: {options}'
            warnings.warn(msg)

    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__qualname__}({self.name!r}) at {id(self):#x}>'
