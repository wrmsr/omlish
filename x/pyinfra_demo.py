import re
import sys
from pyinfra_cli.__main__ import execute_pyinfra  # noqa
sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
sys.exit(execute_pyinfra())
