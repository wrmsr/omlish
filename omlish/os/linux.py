# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
➜  ~ cat /etc/os-release
NAME="Amazon Linux"
VERSION="2"
ID="amzn"
ID_LIKE="centos rhel fedora"
VERSION_ID="2"
PRETTY_NAME="Amazon Linux 2"

➜  ~ cat /etc/os-release
PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.5 LTS (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu
ID_LIKE=debian
UBUNTU_CODENAME=jammy

➜  omlish git:(master) docker run -i python:3.13 cat /etc/os-release
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
NAME="Debian GNU/Linux"
VERSION_ID="12"
VERSION="12 (bookworm)"
VERSION_CODENAME=bookworm
ID=debian
"""
import dataclasses as dc
import os.path
import typing as ta


##


@dc.dataclass(frozen=True)
class LinuxOsRelease:
    """
    https://man7.org/linux/man-pages/man5/os-release.5.html
    """

    raw: ta.Mapping[str, str]

    # General information identifying the operating system

    @property
    def name(self) -> str:
        """
        A string identifying the operating system, without a version component, and suitable for presentation to the
        user. If not set, a default of "NAME=Linux" may be used.

        Examples: "NAME=Fedora", "NAME="Debian GNU/Linux"".
        """

        return self.raw['NAME']

    @property
    def id(self) -> str:
        """
        A lower-case string (no spaces or other characters outside of 0-9, a-z, ".", "_" and "-") identifying the
        operating system, excluding any version information and suitable for processing by scripts or usage in generated
        filenames. If not set, a default of "ID=linux" may be used. Note that even though this string may not include
        characters that require shell quoting, quoting may nevertheless be used.

        Examples: "ID=fedora", "ID=debian".
        """

        return self.raw['ID']

    @property
    def id_like(self) -> str:
        """
        A space-separated list of operating system identifiers in the same syntax as the ID= setting. It should list
        identifiers of operating systems that are closely related to the local operating system in regards to packaging
        and programming interfaces, for example listing one or more OS identifiers the local OS is a derivative from. An
        OS should generally only list other OS identifiers it itself is a derivative of, and not any OSes that are
        derived from it, though symmetric relationships are possible. Build scripts and similar should check this
        variable if they need to identify the local operating system and the value of ID= is not recognized. Operating
        systems should be listed in order of how closely the local operating system relates to the listed ones, starting
        with the closest. This field is optional.

        Examples: for an operating system with "ID=centos", an assignment of "ID_LIKE="rhel fedora"" would be
        appropriate. For an operating system with "ID=ubuntu", an assignment of "ID_LIKE=debian" is appropriate.
        """

        return self.raw['ID_LIKE']

    @property
    def pretty_name(self) -> str:
        """
        A pretty operating system name in a format suitable for presentation to the user. May or may not contain a
        release code name or OS version of some kind, as suitable. If not set, a default of "PRETTY_NAME="Linux"" may be
        used

        Example: "PRETTY_NAME="Fedora 17 (Beefy Miracle)"".
        """

        return self.raw['PRETTY_NAME']

    @property
    def cpe_name(self) -> str:
        """
        A CPE name for the operating system, in URI binding syntax, following the Common Platform Enumeration
        Specification[4] as proposed by the NIST. This field is optional.

        Example: "CPE_NAME="cpe:/o:fedoraproject:fedora:17""
        """

        return self.raw['CPE_NAME']

    @property
    def variant(self) -> str:
        """
        A string identifying a specific variant or edition of the operating system suitable for presentation to the
        user. This field may be used to inform the user that the configuration of this system is subject to a specific
        divergent set of rules or default configuration settings. This field is optional and may not be implemented on
        all systems.

        Examples: "VARIANT="Server Edition"", "VARIANT="Smart Refrigerator Edition"".

        Note: this field is for display purposes only. The VARIANT_ID field should be used for making programmatic
        decisions.

        Added in version 220.
        """

        return self.raw['VARIANT']

    @property
    def variant_id(self) -> str:
        """
        A lower-case string (no spaces or other characters outside of 0-9, a-z, ".", "_" and "-"), identifying a
        specific variant or edition of the operating system. This may be interpreted by other packages in order to
        determine a divergent default configuration. This field is optional and may not be implemented on all systems.

        Examples: "VARIANT_ID=server", "VARIANT_ID=embedded".

        Added in version 220.
        """

        return self.raw['variant_id']

    # Information about the version of the operating system

    @property
    def version(self) -> str:
        """
        A string identifying the operating system version, excluding any OS name information, possibly including a
        release code name, and suitable for presentation to the user. This field is optional.

        Examples: "VERSION=17", "VERSION="17 (Beefy Miracle)"".
        """

        return self.raw['VERSION']

    @property
    def version_id(self) -> str:
        """
        A lower-case string (mostly numeric, no spaces or other characters outside of 0-9, a-z, ".", "_" and "-")
        identifying the operating system version, excluding any OS name information or release code name, and suitable
        for processing by scripts or usage in generated filenames. This field is optional.

        Examples: "VERSION_ID=17", "VERSION_ID=11.04".
        """

        return self.raw['VERSION_ID']

    @property
    def version_codename(self) -> str:
        """
        A lower-case string (no spaces or other characters outside of 0-9, a-z, ".", "_" and "-") identifying the
        operating system release code name, excluding any OS name information or release version, and suitable for
        processing by scripts or usage in generated filenames. This field is optional and may not be implemented on all
        systems.

        Examples: "VERSION_CODENAME=buster", "VERSION_CODENAME=xenial".

        Added in version 231.
        """

        return self.raw['VERSION_CODENAME']

    @property
    def build_id(self) -> str:
        """
        A string uniquely identifying the system image originally used as the installation base. In most cases,
        VERSION_ID or IMAGE_ID+IMAGE_VERSION are updated when the entire system image is replaced during an update.
        BUILD_ID may be used in distributions where the original installation image version is important: VERSION_ID
        would change during incremental system updates, but BUILD_ID would not. This field is optional.

        Examples: "BUILD_ID="2013-03-20.3"", "BUILD_ID=201303203".

        Added in version 200.
        """

        return self.raw['BUILD_ID']

    @property
    def image_id(self) -> str:
        """
        A lower-case string (no spaces or other characters outside of 0-9, a-z, ".", "_" and "-"), identifying a
        specific image of the operating system. This is supposed to be used for environments where OS images are
        prepared, built, shipped and updated as comprehensive, consistent OS images. This field is optional and may not
        be implemented on all systems, in particularly not on those that are not managed via images but put together and
        updated from individual packages and on the local system.

        Examples: "IMAGE_ID=vendorx-cashier-system", "IMAGE_ID=netbook-image".

        Added in version 249.
        """

        return self.raw['IMAGE_ID']

    @property
    def image_version(self) -> str:
        """
        A lower-case string (mostly numeric, no spaces or other characters outside of 0-9, a-z, ".", "_" and "-")
        identifying the OS image version. This is supposed to be used together with IMAGE_ID described above, to discern
        different versions of the same image.

        Examples: "IMAGE_VERSION=33", "IMAGE_VERSION=47.1rc1".

        Added in version 249.
        """

        return self.raw['IMAGE_VERSION']

    # To summarize: if the image updates are built and shipped as comprehensive units, IMAGE_ID+IMAGE_VERSION is the
    # best fit. Otherwise, if updates eventually completely replace previously installed contents, as in a typical
    # binary distribution, VERSION_ID should be used to identify major releases of the operating system.  BUILD_ID may
    # be used instead or in addition to VERSION_ID when the original system image version is important.

    #

    # Presentation information and links

    # Links to resources on the Internet related to the operating system.  HOME_URL= should refer to the homepage of the
    # operating system, or alternatively some homepage of the specific version of the operating system.
    # DOCUMENTATION_URL= should refer to the main documentation page for this operating system.  SUPPORT_URL= should
    # refer to the main support page for the operating system, if there is any. This is primarily intended for operating
    # systems which vendors provide support for.  BUG_REPORT_URL= should refer to the main bug reporting page for the
    # operating system, if there is any. This is primarily intended for operating systems that rely on community QA.
    # PRIVACY_POLICY_URL= should refer to the main privacy policy page for the operating system, if there is any. These
    # settings are optional, and providing only some of these settings is common. These URLs are intended to be exposed
    # in "About this system" UIs behind links with captions such as "About this Operating System", "Obtain Support",
    # "Report a Bug", or "Privacy Policy". The values should be in RFC3986 format[5], and should be "http:" or "https:"
    # URLs, and possibly "mailto:" or "tel:". Only one URL shall be listed in each setting. If multiple resources need
    # to be referenced, it is recommended to provide an online landing page linking all available resources.

    # Examples: "HOME_URL="https://fedoraproject.org/"", "BUG_REPORT_URL="https://bugzilla.redhat.com/"".

    @property
    def home_url(self) -> str:
        return self.raw['HOME_URL']

    @property
    def documentation_url(self) -> str:
        return self.raw['DOCUMENTATION_URL']

    @property
    def support_url(self) -> str:
        return self.raw['SUPPORT_URL']

    @property
    def bug_report_url(self) -> str:
        return self.raw['BUG_REPORT_URL']

    @property
    def privacy_policy_url(self) -> str:
        return self.raw['PRIVACY_POLICY_URL']

    @property
    def support_end(self) -> str:
        """
        The date at which support for this version of the OS ends. (What exactly "lack of support" means varies between
        vendors, but generally users should assume that updates, including security fixes, will not be provided.) The
        value is a date in the ISO 8601 format "YYYY-MM-DD", and specifies the first day on which support is not
        provided.

        For example, "SUPPORT_END=2001-01-01" means that the system was supported until the end of the last day of the
        previous millennium.

        Added in version 252.
        """

        return self.raw['SUPPORT_END']

    @property
    def logo(self) -> str:
        """
        A string, specifying the name of an icon as defined by freedesktop.org Icon Theme Specification[6]. This can be
        used by graphical applications to display an operating system's or distributor's logo. This field is optional
        and may not necessarily be implemented on all systems.

        Examples: "LOGO=fedora-logo", "LOGO=distributor-logo-opensuse"

        Added in version 240.
        """

        return self.raw['LOGO']

    @property
    def ansi_color(self) -> str:
        """
        A suggested presentation color when showing the OS name on the console. This should be specified as string
        suitable for inclusion in the ESC [ m ANSI/ECMA-48 escape code for setting graphical rendition. This field is
        optional.

        Examples: "ANSI_COLOR="0;31"" for red, "ANSI_COLOR="1;34"" for light blue, or "ANSI_COLOR="0;38;2;60;110;180""
        for Fedora blue.
        """

        return self.raw['ANSI_COLOR']

    @property
    def vendor_name(self) -> str:
        """
        The name of the OS vendor. This is the name of the organization or company which produces the OS. This field is
        optional.

        This name is intended to be exposed in "About this system" UIs or software update UIs when needed to distinguish
        the OS vendor from the OS itself. It is intended to be human readable.

        Examples: "VENDOR_NAME="Fedora Project"" for Fedora Linux, "VENDOR_NAME="Canonical"" for Ubuntu.

        Added in version 254.
        """

        return self.raw['VENDOR_NAME']

    @property
    def vendor_url(self) -> str:
        """
        The homepage of the OS vendor. This field is optional. The VENDOR_NAME= field should be set if this one is,
        although clients must be robust against either field not being set.

        The value should be in RFC3986 format[5], and should be "http:" or "https:" URLs. Only one URL shall be listed
        in the setting.

        Examples: "VENDOR_URL="https://fedoraproject.org/"", "VENDOR_URL="https://canonical.com/"".

        Added in version 254.
        """

        return self.raw['VENDOR_URL']

    # Distribution-level defaults and metadata

    @property
    def default_hostname(self) -> str:
        """
        A string specifying the hostname if hostname(5) is not present and no other configuration source specifies the
        hostname. Must be either a single DNS label (a string composed of 7-bit ASCII lower-case characters and no
        spaces or dots, limited to the format allowed for DNS domain name labels), or a sequence of such labels
        separated by single dots that forms a valid DNS FQDN. The hostname must be at most 64 characters, which is a
        Linux limitation (DNS allows longer names).

        See org.freedesktop.hostname1(5) for a description of how systemd-hostnamed.service(8) determines the fallback
        hostname.

        Added in version 248.
        """

        return self.raw['DEFAULT_HOSTNAME']

    @property
    def architecture(self) -> str:
        """
        A string that specifies which CPU architecture the userspace binaries require. The architecture identifiers are
        the same as for ConditionArchitecture= described in systemd.unit(5). The field is optional and should only be
        used when just single architecture is supported. It may provide redundant information when used in a GPT
        partition with a GUID type that already encodes the architecture. If this is not the case, the architecture
        should be specified in e.g., an extension image, to prevent an incompatible host from loading it.

        Added in version 252.
        """

        return self.raw['ARCHITECTURE']

    @property
    def sysext_level(self) -> str:
        """
        A lower-case string (mostly numeric, no spaces or other characters outside of 0-9, a-z, ".", "_" and "-")
        identifying the operating system extensions support level, to indicate which extension images are supported. See
        /usr/lib/extension-release.d/extension-release.IMAGE, initrd[2] and systemd-sysext(8)) for more information.

        Examples: "SYSEXT_LEVEL=2", "SYSEXT_LEVEL=15.14".

        Added in version 248.
        """

        return self.raw['SYSEXT_LEVEL']

    @property
    def confext_level(self) -> str:
        """
        Semantically the same as SYSEXT_LEVEL= but for confext images. See
        /etc/extension-release.d/extension-release.IMAGE for more information.

        Examples: "CONFEXT_LEVEL=2", "CONFEXT_LEVEL=15.14".

        Added in version 254.
        """

        return self.raw['CONFEXT_LEVEL']

    @property
    def sysext_scope(self) -> str:
        """
        Takes a space-separated list of one or more of the strings "system", "initrd" and "portable". This field is only
        supported in extension-release.d/ files and indicates what environments the system extension is applicable to:
        i.e. to regular systems, to initrds, or to portable service images. If unspecified, "SYSEXT_SCOPE=system
        portable" is implied, i.e. any system extension without this field is applicable to regular systems and to
        portable service environments, but not to initrd environments.

        Added in version 250.
        """

        return self.raw['SYSEXT_SCOPE']

    @property
    def confext_scope(self) -> str:
        """
        Semantically the same as SYSEXT_SCOPE= but for confext images.

        Added in version 254.
        """

        return self.raw['CONFEXT_SCOPE']

    @property
    def portable_prefixes(self) -> str:
        """
        Takes a space-separated list of one or more valid prefix match strings for the Portable Services[3] logic. This
        field serves two purposes: it is informational, identifying portable service images as such (and thus allowing
        them to be distinguished from other OS images, such as bootable system images). It is also used when a portable
        service image is attached: the specified or implied portable service prefix is checked against the list
        specified here, to enforce restrictions how images may be attached to a system.

        Added in version 250.
        """

        return self.raw['PORTABLE_PREFIXES']

    #

    DEFAULT_PATHS: ta.ClassVar[ta.Sequence[str]] = [
        '/etc/os-release',
        '/usr/lib/os-release',
    ]

    @classmethod
    def read(cls, *paths: str) -> ta.Optional['LinuxOsRelease']:
        for fp in (paths or cls.DEFAULT_PATHS):
            if not os.path.isfile(fp):
                continue
            with open(fp) as f:
                src = f.read()
            break
        else:
            return None

        raw = cls._parse_os_release(src)

        return cls(raw)

    @classmethod
    def _parse_os_release(cls, src: str) -> ta.Mapping[str, str]:
        dct: ta.Dict[str, str] = {}

        for l in src.splitlines():
            if not (l := l.strip()):
                continue
            if l.startswith('#') or '=' not in l:
                continue

            k, _, v = l.partition('=')
            if k.startswith('"'):
                k = k[1:-1]
            if v.startswith('"'):
                v = v[1:-1]

            dct[k] = v

        return dct
