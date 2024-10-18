# https://github.com/asweigart/pyperclip/blob/e16fa9c336454be8e73378f50498780b777a4247/src/pyperclip/__init__.py
# Copyright (c) 2014, Al Sweigart
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
#
# * Neither the name of the {organization} nor the names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Pyperclip

A cross-platform clipboard module for Python, with copy & paste functions for plain text.
By Al Sweigart al@inventwithpython.com
BSD License

Usage:
  import pyperclip
  pyperclip.copy('The text to be copied to the clipboard.')
  spam = pyperclip.paste()

  if not pyperclip.is_available():
    print("Copy functionality unavailable!")

On Mac, the pyobjc module is used, falling back to the pbcopy and pbpaste cli
    commands. (These commands should come with OS X.).
On Linux, install xclip, xsel, or wl-clipboard (for "wayland" sessions) via package manager.
For example, in Debian:
    sudo apt-get install xclip
    sudo apt-get install xsel
    sudo apt-get install wl-clipboard

Otherwise on Linux, you will need the qtpy or PyQt5 modules installed.

This module does not work with PyGObject yet.

Cygwin is currently not supported.

Security Note: This module runs programs with these names:
    - which
    - pbcopy
    - pbpaste
    - xclip
    - xsel
    - wl-copy/wl-paste
    - klipper
    - qdbus
A malicious user could rename or add programs with these names, tricking
Pyperclip into running them with whatever permissions the Python process has.

"""
__version__ = '1.9.0'

import base64
import contextlib
import ctypes
import os
import platform
import subprocess
import sys
import time
import warnings
from ctypes import c_size_t
from ctypes import c_wchar
from ctypes import c_wchar_p
from ctypes import get_errno
from ctypes import sizeof


_IS_RUNNING_PYTHON_2 = sys.version_info[0] == 2  # type: bool

# For paste(): Python 3 uses str, Python 2 uses unicode.
if _IS_RUNNING_PYTHON_2:
    # mypy complains about `unicode` for Python 2, so we ignore the type error:
    _PYTHON_STR_TYPE = unicode  # type: ignore
else:
    _PYTHON_STR_TYPE = str

ENCODING = 'utf-8'  # type: str

try:
    # Use shutil.which() for Python 3+
    from shutil import which

    def _py3_executable_exists(name):  # type: (str) -> bool
        return bool(which(name))

    _executable_exists = _py3_executable_exists
except ImportError:
    # Use the "which" unix command for Python 2.7 and prior.
    def _py2_executable_exists(name):  # type: (str) -> bool
        return (
            subprocess.call(
                ['which', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            == 0
        )

    _executable_exists = _py2_executable_exists


# Exceptions
class PyperclipException(RuntimeError):
    pass


class PyperclipTimeoutException(PyperclipException):
    pass


def init_osx_pbcopy_clipboard():
    def copy_osx_pbcopy(text):
        text = _PYTHON_STR_TYPE(text)  # Converts non-str values to str.
        p = subprocess.Popen(['pbcopy', 'w'], stdin=subprocess.PIPE, close_fds=True)
        p.communicate(input=text.encode(ENCODING))

    def paste_osx_pbcopy():
        p = subprocess.Popen(['pbpaste', 'r'], stdout=subprocess.PIPE, close_fds=True)
        stdout, stderr = p.communicate()
        return stdout.decode(ENCODING)

    return copy_osx_pbcopy, paste_osx_pbcopy


def init_osx_pyobjc_clipboard():
    def copy_osx_pyobjc(text):
        """Copy string argument to clipboard"""
        text = _PYTHON_STR_TYPE(text)  # Converts non-str values to str.
        newStr = Foundation.NSString.stringWithString_(text).nsstring()
        newData = newStr.dataUsingEncoding_(Foundation.NSUTF8StringEncoding)
        board = AppKit.NSPasteboard.generalPasteboard()
        board.declareTypes_owner_([AppKit.NSStringPboardType], None)
        board.setData_forType_(newData, AppKit.NSStringPboardType)

    def paste_osx_pyobjc():
        "Returns contents of clipboard"
        board = AppKit.NSPasteboard.generalPasteboard()
        content = board.stringForType_(AppKit.NSStringPboardType)
        return content

    return copy_osx_pyobjc, paste_osx_pyobjc


def init_qt_clipboard():
    global QApplication
    # $DISPLAY should exist

    # Try to import from qtpy, but if that fails try PyQt5
    try:
        from qtpy.QtWidgets import QApplication
    except:
        from PyQt5.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    def copy_qt(text):
        text = _PYTHON_STR_TYPE(text)  # Converts non-str values to str.
        cb = app.clipboard()
        cb.setText(text)

    def paste_qt():
        cb = app.clipboard()
        return _PYTHON_STR_TYPE(cb.text())

    return copy_qt, paste_qt


def init_xclip_clipboard():
    DEFAULT_SELECTION = 'c'
    PRIMARY_SELECTION = 'p'

    def copy_xclip(text, primary=False):
        text = _PYTHON_STR_TYPE(text)  # Converts non-str values to str.
        selection = DEFAULT_SELECTION
        if primary:
            selection = PRIMARY_SELECTION
        p = subprocess.Popen(
            ['xclip', '-selection', selection], stdin=subprocess.PIPE, close_fds=True,
        )
        p.communicate(input=text.encode(ENCODING))

    def paste_xclip(primary=False):
        selection = DEFAULT_SELECTION
        if primary:
            selection = PRIMARY_SELECTION
        p = subprocess.Popen(
            ['xclip', '-selection', selection, '-o'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
        )
        stdout, stderr = p.communicate()
        # Intentionally ignore extraneous output on stderr when clipboard is empty
        return stdout.decode(ENCODING)

    return copy_xclip, paste_xclip


def init_xsel_clipboard():
    DEFAULT_SELECTION = '-b'
    PRIMARY_SELECTION = '-p'

    def copy_xsel(text, primary=False):
        text = _PYTHON_STR_TYPE(text)  # Converts non-str values to str.
        selection_flag = DEFAULT_SELECTION
        if primary:
            selection_flag = PRIMARY_SELECTION
        p = subprocess.Popen(
            ['xsel', selection_flag, '-i'], stdin=subprocess.PIPE, close_fds=True,
        )
        p.communicate(input=text.encode(ENCODING))

    def paste_xsel(primary=False):
        selection_flag = DEFAULT_SELECTION
        if primary:
            selection_flag = PRIMARY_SELECTION
        p = subprocess.Popen(
            ['xsel', selection_flag, '-o'], stdout=subprocess.PIPE, close_fds=True,
        )
        stdout, stderr = p.communicate()
        return stdout.decode(ENCODING)

    return copy_xsel, paste_xsel


def init_wl_clipboard():
    PRIMARY_SELECTION = '-p'

    def copy_wl(text, primary=False):
        text = _PYTHON_STR_TYPE(text)  # Converts non-str values to str.
        args = ['wl-copy']
        if primary:
            args.append(PRIMARY_SELECTION)
        if not text:
            args.append('--clear')
            subprocess.check_call(args, close_fds=True)
        else:
            p = subprocess.Popen(args, stdin=subprocess.PIPE, close_fds=True)
            p.communicate(input=text.encode(ENCODING))

    def paste_wl(primary=False):
        args = ['wl-paste', '-n', '-t', 'text']
        if primary:
            args.append(PRIMARY_SELECTION)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, close_fds=True)
        stdout, _stderr = p.communicate()
        return stdout.decode(ENCODING)

    return copy_wl, paste_wl


def init_klipper_clipboard():
    def copy_klipper(text):
        text = _PYTHON_STR_TYPE(text)  # Converts non-str values to str.
        p = subprocess.Popen(
            [
                'qdbus',
                'org.kde.klipper',
                '/klipper',
                'setClipboardContents',
                text.encode(ENCODING),
            ],
            stdin=subprocess.PIPE,
            close_fds=True,
        )
        p.communicate(input=None)

    def paste_klipper():
        p = subprocess.Popen(
            ['qdbus', 'org.kde.klipper', '/klipper', 'getClipboardContents'],
            stdout=subprocess.PIPE,
            close_fds=True,
        )
        stdout, stderr = p.communicate()

        # Workaround for https://bugs.kde.org/show_bug.cgi?id=342874
        # TODO: https://github.com/asweigart/pyperclip/issues/43
        clipboardContents = stdout.decode(ENCODING)
        # even if blank, Klipper will append a newline at the end
        assert len(clipboardContents) > 0
        # make sure that newline is there
        assert clipboardContents.endswith('\n')
        if clipboardContents.endswith('\n'):
            clipboardContents = clipboardContents[:-1]
        return clipboardContents

    return copy_klipper, paste_klipper


def init_dev_clipboard_clipboard():
    def copy_dev_clipboard(text):
        text = _PYTHON_STR_TYPE(text)  # Converts non-str values to str.
        if text == '':
            warnings.warn(
                'Pyperclip cannot copy a blank string to the clipboard on Cygwin. This is effectively a no-op.',
            )
        if '\r' in text:
            warnings.warn('Pyperclip cannot handle \\r characters on Cygwin.')

        fo = open('/dev/clipboard', 'w')
        fo.write(text)
        fo.close()

    def paste_dev_clipboard():
        fo = open('/dev/clipboard')
        content = fo.read()
        fo.close()
        return content

    return copy_dev_clipboard, paste_dev_clipboard


def init_no_clipboard():
    class ClipboardUnavailable:
        def __call__(self, *args, **kwargs):
            additionalInfo = ''
            if sys.platform == 'linux':
                additionalInfo = '\nOn Linux, you can run `sudo apt-get install xclip` or `sudo apt-get install xselect` to install a copy/paste mechanism.'
            raise PyperclipException(
                'Pyperclip could not find a copy/paste mechanism for your system. For more information, please visit https://pyperclip.readthedocs.io/en/latest/index.html#not-implemented-error'
                + additionalInfo,
            )

        if _IS_RUNNING_PYTHON_2:

            def __nonzero__(self):
                return False

        else:

            def __bool__(self):
                return False

    return ClipboardUnavailable(), ClipboardUnavailable()


def init_wsl_clipboard():
    def copy_wsl(text):
        text = _PYTHON_STR_TYPE(text)  # Converts non-str values to str.
        p = subprocess.Popen(['clip.exe'], stdin=subprocess.PIPE, close_fds=True)
        p.communicate(input=text.encode('utf-16le'))

    def paste_wsl():
        ps_script = '[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((Get-Clipboard -Raw)))'

        # '-noprofile' speeds up load time
        p = subprocess.Popen(
            ['powershell.exe', '-noprofile', '-command', ps_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
        )
        stdout, stderr = p.communicate()

        if stderr:
            raise Exception(f'Error pasting from clipboard: {stderr}')

        try:
            base64_encoded = stdout.decode('utf-8').strip()
            decoded_bytes = base64.b64decode(base64_encoded)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            raise RuntimeError(f'Decoding error: {e}')

    return copy_wsl, paste_wsl


# Automatic detection of clipboard mechanisms and importing is done in determine_clipboard():
def determine_clipboard():
    """
    Determine the OS/platform and set the copy() and paste() functions
    accordingly.
    """

    global Foundation, AppKit, qtpy, PyQt5

    # Setup for the CYGWIN platform:
    if (
        'cygwin' in platform.system().lower()
    ):  # Cygwin has a variety of values returned by platform.system(), such as 'CYGWIN_NT-6.1'
        # FIXME: pyperclip currently does not support Cygwin,
        # see https://github.com/asweigart/pyperclip/issues/55
        if os.path.exists('/dev/clipboard'):
            warnings.warn(
                "Pyperclip's support for Cygwin is not perfect, see https://github.com/asweigart/pyperclip/issues/55",
            )
            return init_dev_clipboard_clipboard()

    if platform.system() == 'Linux' and os.path.isfile('/proc/version'):
        with open('/proc/version') as f:
            if 'microsoft' in f.read().lower():
                return init_wsl_clipboard()

    # Setup for the MAC OS X platform:
    if os.name == 'mac' or platform.system() == 'Darwin':
        try:
            import AppKit
            import Foundation  # check if pyobjc is installed
        except ImportError:
            return init_osx_pbcopy_clipboard()
        else:
            return init_osx_pyobjc_clipboard()

    # Setup for the LINUX platform:

    if (
        os.getenv('WAYLAND_DISPLAY')
        and _executable_exists('wl-copy')
        and _executable_exists('wl-paste')
    ):
        return init_wl_clipboard()

    # `import PyQt4` sys.exit()s if DISPLAY is not in the environment.
    # Thus, we need to detect the presence of $DISPLAY manually
    # and not load PyQt4 if it is absent.
    elif os.getenv('DISPLAY'):
        if _executable_exists('xclip'):
            # Note: 2024/06/18 Google Trends shows xclip as more popular than xsel.
            return init_xclip_clipboard()
        if _executable_exists('xsel'):
            return init_xsel_clipboard()
        if _executable_exists('klipper') and _executable_exists('qdbus'):
            return init_klipper_clipboard()

        try:
            # qtpy is a small abstraction layer that lets you write
            # applications using a single api call to either PyQt or PySide.
            # https://pypi.python.org/pypi/QtPy
            import qtpy  # check if qtpy is installed

            return init_qt_clipboard()
        except ImportError:
            pass

        # If qtpy isn't installed, fall back on importing PyQt5
        try:
            import PyQt5  # check if PyQt5 is installed

            return init_qt_clipboard()
        except ImportError:
            pass

    return init_no_clipboard()


def set_clipboard(clipboard):
    """
    Explicitly sets the clipboard mechanism. The "clipboard mechanism" is how
    the copy() and paste() functions interact with the operating system to
    implement the copy/paste feature. The clipboard parameter must be one of:
        - pbcopy
        - pbobjc (default on Mac OS X)
        - qt
        - xclip
        - xsel
        - klipper
        - no (this is what is set when no clipboard mechanism can be found)
    """
    global copy, paste

    clipboard_types = {
        'pbcopy': init_osx_pbcopy_clipboard,
        'pyobjc': init_osx_pyobjc_clipboard,
        'qt': init_qt_clipboard,  # TODO - split this into 'qtpy' and 'pyqt5'
        'xclip': init_xclip_clipboard,
        'xsel': init_xsel_clipboard,
        'wl-clipboard': init_wl_clipboard,
        'klipper': init_klipper_clipboard,
        'no': init_no_clipboard,
    }

    if clipboard not in clipboard_types:
        raise ValueError(
            'Argument must be one of %s'
            % (', '.join([repr(_) for _ in clipboard_types])),
        )

    # Sets pyperclip's copy() and paste() functions:
    copy, paste = clipboard_types[clipboard]()


def lazy_load_stub_copy(text):
    """
    A stub function for copy(), which will load the real copy() function when
    called so that the real copy() function is used for later calls.

    This allows users to import pyperclip without having determine_clipboard()
    automatically run, which will automatically select a clipboard mechanism.
    This could be a problem if it selects, say, the memory-heavy PyQt5 module
    but the user was just going to immediately call set_clipboard() to use a
    different clipboard mechanism.

    The lazy loading this stub function implements gives the user a chance to
    call set_clipboard() to pick another clipboard mechanism. Or, if the user
    simply calls copy() or paste() without calling set_clipboard() first,
    will fall back on whatever clipboard mechanism that determine_clipboard()
    automatically chooses.
    """
    global copy, paste
    copy, paste = determine_clipboard()
    return copy(text)


def lazy_load_stub_paste():
    """
    A stub function for paste(), which will load the real paste() function when
    called so that the real paste() function is used for later calls.

    This allows users to import pyperclip without having determine_clipboard()
    automatically run, which will automatically select a clipboard mechanism.
    This could be a problem if it selects, say, the memory-heavy PyQt5 module
    but the user was just going to immediately call set_clipboard() to use a
    different clipboard mechanism.

    The lazy loading this stub function implements gives the user a chance to
    call set_clipboard() to pick another clipboard mechanism. Or, if the user
    simply calls copy() or paste() without calling set_clipboard() first,
    will fall back on whatever clipboard mechanism that determine_clipboard()
    automatically chooses.
    """
    global copy, paste
    copy, paste = determine_clipboard()
    return paste()


def is_available():
    return copy != lazy_load_stub_copy and paste != lazy_load_stub_paste


# Initially, copy() and paste() are set to lazy loading wrappers which will
# set `copy` and `paste` to real functions the first time they're used, unless
# set_clipboard() or determine_clipboard() is called first.
copy, paste = lazy_load_stub_copy, lazy_load_stub_paste


def _main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in ('-c', '--copy'):
        if len(sys.argv) > 2:
            copy(sys.argv[2])
        else:
            copy(sys.stdin.read())
    elif len(sys.argv) > 1 and sys.argv[1] in ('-p', '--paste'):
        sys.stdout.write(paste())
    else:
        print(
            'Usage: python -m pyperclip [-c | --copy] [text_to_copy] | [-p | --paste]',
        )
        print()
        print('If a text_to_copy argument is provided, it is copied to the')
        print('clipboard. Otherwise, the stdin stream is copied to the')
        print('clipboard. (If reading this in from the keyboard, press')
        print('CTRL-Z on Windows or CTRL-D on Linux/macOS to stop.')
        print('When pasting, the clipboard will be written to stdout.')


if __name__ == '__main__':
    _main()
