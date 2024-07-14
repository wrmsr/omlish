"""
TODO:
 - ** include md5 of src file, simp.cython.install('lang') may or may not decide not to patch if src present and !=
  - but src _never required_
 - simp -> cy duh
 - anns? lang.descriptors tuple hit?
 - classpath scan, Makefile gen step
  - attr + replacement
 - lol, can't ref simply from lang..
  - * hot comments lol *
  - *prefer* a proper ann but *support* dumb hot comment scanning:
   - dedicated whole line::
       #@simp.cythonize(_lang)
       def __call__(self, *args, **kwargs):
           flags = self._flags
           if not flags.callable:
               raise TypeError(f'Cannot __call__ {self}')
           return self.__func__(*args, **kwargs)
  - knows how to replace *and* replace, but how..
   - genned cy module replaces on import! all thats necessary is:
     try:
         from .._ext._cy._simp import _lang
     except ImportError:
         pass
   - ** functools.wraps orig
 - pluggable 'profiles', largely affecting annotation handling:
  - numbers (varint, lang.bits, chd) - ints, floats
  - objects - mostly discarded? lol
"""
