import setuptools as st
import setuptools_rust as st_rs


def _patch_sdist():
    def _sdist_add_defaults(old, self):
        import os.path

        old(self)

        if self.distribution.rust_extensions and len(self.distribution.rust_extensions) > 0:
            build_rust = self.get_finalized_command('build_rust')  # noqa
            for ext in build_rust.extensions:
                ext_dir = os.path.dirname(ext.path)
                for n in os.listdir(ext_dir):
                    if n.startswith('.') or n == 'target':
                        continue
                    p = os.path.join(ext_dir, n)
                    if os.path.isfile(p):
                        self.filelist.append(p)
                    elif os.path.isdir(p):
                        self.filelist.extend(os.path.join(dp, f) for dp, dn, fn in os.walk(p) for f in fn)

    # Sadly, we can't just subclass sdist and override it via cmdclass because manifest_maker calls
    # `sdist.add_defaults` as an unbound function, not a bound method:
    # https://github.com/pypa/setuptools/blob/9c4d383631d3951fcae0afd73b5d08ff5a262976/setuptools/command/egg_info.py#L581
    from setuptools.command.sdist import sdist  # noqa
    sdist.add_defaults = (lambda old: lambda sdist: _sdist_add_defaults(old, sdist))(sdist.add_defaults)  # noqa

_patch_sdist()


st.setup(
    rust_extensions=[
        st_rs.RustExtension(
            'omdev.rs._boilerplate',
            path='omdev/rs/_boilerplate/Cargo.toml',
        ),
    ],
)
