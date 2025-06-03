__version__ = "2.6.1"
__version_tuple__ = tuple((2, 6, 1))


import os

_dir = os.path.dirname(__file__)
_camlibs = os.path.join(_dir, 'libgphoto2', 'camlibs')
if os.path.isdir(_camlibs):
    os.environ['CAMLIBS'] = _camlibs
if 'VCAMERADIR' in os.environ:
    _iolibs = os.path.join(_dir, 'libgphoto2', 'vusb')
else:
    _iolibs = os.path.join(_dir, 'libgphoto2', 'iolibs')
if os.path.isdir(_iolibs):
    os.environ['IOLIBS'] = _iolibs

class GPhoto2Error(Exception):
    """Exception raised by gphoto2 library errors

    Attributes:
        code   (int): the gphoto2 error code
        string (str): corresponding error message
    """
    def __init__(self, code):
        string = gp_result_as_string(code)
        Exception.__init__(self, '[%d] %s' % (code, string))
        self.code = code
        self.string = string

from gphoto2.abilities_list import *
from gphoto2.camera import *
from gphoto2.context import *
from gphoto2.file import *
from gphoto2.filesys import *
from gphoto2.list import *
from gphoto2.port import *
from gphoto2.port_info_list import *
from gphoto2.port_log import *
from gphoto2.result import *
from gphoto2.version import *
from gphoto2.widget import *

_locale = os.path.join(_dir, 'libgphoto2', 'locale')
if os.path.isdir(_locale):
    gphoto2.abilities_list.gp_init_localedir(_locale)

__all__ = dir()
