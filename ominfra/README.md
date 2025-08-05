# Overview

Infrastructure and cloud code.

# Notable packages

- **[clouds.aws](https://github.com/wrmsr/omlish/blob/master/ominfra/clouds/aws)** - boto-less aws tools, including
  authentication and generated service dataclasses.

- **[journald2aws](https://github.com/wrmsr/omlish/blob/master/ominfra/clouds/aws/journald2aws)**
  ([amalg](https://github.com/wrmsr/omlish/blob/master/ominfra/scripts/journald2aws.py)) - a self-contained little tool
  that forwards journald to cloudwatch.

- **[pyremote](https://github.com/wrmsr/omlish/blob/master/ominfra/pyremote.py)** - does the
  [mitogen trick](https://mitogen.networkgenomics.com/howitworks.html) to facilitate remote execution of python code.
  due to amalgamation, import shenanigans aren't required to do useful work.

- **[manage](https://github.com/wrmsr/omlish/blob/master/ominfra/manage)**
  ([amalg](https://github.com/wrmsr/omlish/blob/master/ominfra/scripts/manage.py)) - a remote system management tool,
  including a code deployment system. inspired by things like [mitogen](https://mitogen.networkgenomics.com/),
  [pyinfra](https://github.com/pyinfra-dev/pyinfra), [piku](https://github.com/piku/piku). uses pyremote.

- **[supervisor](https://github.com/wrmsr/omlish/blob/master/ominfra/supervisor)**
  ([amalg](https://github.com/wrmsr/omlish/blob/master/ominfra/scripts/supervisor.py)) - an overhauled,
  [amalgamated](https://github.com/wrmsr/omlish/blob/master/omdev#amalgamation) fork of
  [supervisor](https://github.com/Supervisor/supervisor)
