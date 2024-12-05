from __future__ import annotations

import re
import shlex

from pyinfra.api import FactBase

from .util.packaging import parse_packages

rpm_regex = r"^(\S+)\ (\S+)$"
rpm_query_format = "%{NAME} %{VERSION}-%{RELEASE}\\n"


class RpmPackages(FactBase):
    """
    Returns a dict of installed rpm packages:

    .. code:: python

        {
            "package_name": ["version"],
        }
    """

    def command(self) -> str:
        return "rpm --queryformat {0} -qa".format(shlex.quote(rpm_query_format))

    def requires_command(self) -> str:
        return "rpm"

    default = dict

    def process(self, output):
        return parse_packages(rpm_regex, output)


class RpmPackage(FactBase):
    """
    Returns information on a .rpm file:

    .. code:: python

        {
            "name": "my_package",
            "version": "1.0.0",
        }
    """

    def requires_command(self, package) -> str:
        return "rpm"

    def command(self, package) -> str:
        return (
            "rpm --queryformat {0} -q {1} || "
            "! test -e {1} || "
            "rpm --queryformat {0} -qp {1} 2> /dev/null"
        ).format(shlex.quote(rpm_query_format), shlex.quote(package))

    def process(self, output):
        for line in output:
            matches = re.match(rpm_regex, line)
            if matches:
                return {
                    "name": matches.group(1),
                    "version": matches.group(2),
                }


class RpmPackageProvides(FactBase):
    """
    Returns a list of packages that provide the specified capability (command, file, etc).
    """

    default = list

    def requires_command(self, *args, **kwargs) -> str:
        return "repoquery"

    def command(self, package):
        # Accept failure here (|| true) for invalid/unknown packages
        return "repoquery --queryformat {0} --whatprovides {1} || true".format(
            shlex.quote(rpm_query_format),
            shlex.quote(package),
        )

    def process(self, output):
        packages = []

        for line in output:
            matches = re.match(rpm_regex, line)
            if matches:
                packages.append(list(matches.groups()))

        return packages
