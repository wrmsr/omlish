# ruff: noqa: UP006 UP007
# @omlish-lite
# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from .core import _CoreBlueletApi
from .files import _FilesBlueletApi
from .runner import _RunnerBlueletApi
from .sockets import _SocketsBlueletApi


class BlueletApi(
    _RunnerBlueletApi,
    _SocketsBlueletApi,
    _FilesBlueletApi,
    _CoreBlueletApi,
):
    pass


bluelet = BlueletApi()
