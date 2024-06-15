"""
TODO:
 - https://github.com/kolypto/j2cli/blob/master/j2cli
"""
import logging
import sys

from omlish import argparse as oap
from omlish import logs
import jinja2


log = logging.getLogger(__name__)


class Cli(oap.Cli):

    @oap.command(
        oap.arg('file'),
    )
    def render(self) -> None:
        if self.args.file == '-':
            buf = sys.stdin.read()
        elif self.args.file:
            with open(self.args.file, 'r') as f:
                buf = f.read()
        else:
            raise ValueError('Specify file')

        from jinja2 import (
            __version__ as jinja_version,
            Environment,
            FileSystemLoader,
            StrictUndefined,
        )

        # Starting with jinja2 3.1, `with_` and `autoescape` are no longer
        # able to be imported, but since they were default, let's stub them back
        # in implicitly for older versions.
        # We also don't track any lower bounds on jinja2 as a dependency, so
        # it's not easily safe to know it's included by default either.
        if tuple(jinja_version.split(".", 2)) < ("3", "1"):
            for ext in "with_", "autoescape":
                ext = "jinja2.ext." + ext
                if ext not in extensions:
                    extensions.append(ext)

        env = Environment(
            loader=FileSystemLoader(os.path.dirname(template_path)),
            extensions=extensions,
            keep_trailing_newline=True,
        )
        if strict:
            env.undefined = StrictUndefined

        # Add environ global
        env.globals["environ"] = lambda key: force_text(os.environ.get(key))
        env.globals["get_context"] = lambda: data

        tmpl = jinja2.Template(buf)
        out = tmpl.render()
        print(out)


def main():
    logs.configure_standard_logging(logging.INFO)
    Cli()()


if __name__ == '__main__':
    main()
