# Overview

Infrastructure and cloud code.

# Notable packages

- **[clouds.aws](clouds/aws)** - boto-less aws tools, including authentication and a generated dataclasses.

- **[journald2aws](clouds/aws/journald2aws)** ([amalg](scripts/journald2aws.py)) - a self-contained little tool that
  forwards journald to cloudwatch.

- **[pyremote](pyremote.py)** - does the [mitogen trick](https://mitogen.networkgenomics.com/howitworks.html) to
  facilitate remote execution of python code. due to amalgamation, import shenanigans aren't required to do useful work.

- **[manage](manage)** ([amalg](scripts/manage.py)) - a remote system management tool, including a code deployment
  system. inspired by things like [mitogen](https://mitogen.networkgenomics.com/),
  [pyinfra](https://github.com/pyinfra-dev/pyinfra), [piku](https://github.com/piku/piku). uses pyremote.

- **[supervisor](supervisor)** ([amalg](scripts/supervisor.py)) - an overhauled, [amalgamated](https://github.com/wrmsr/omlish/tree/master/omdev#amalgamation)
  fork of [supervisor](https://github.com/Supervisor/supervisor)
