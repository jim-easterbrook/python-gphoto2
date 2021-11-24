# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2021  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict
import os
import re
import shutil
import subprocess
import sys


def main(argv=None):
    # get version to SWIG
    if len(sys.argv) != 2:
        print('Usage: %s version | "system"' % sys.argv[0])
        return 1
    # get python-gphoto2 version
    with open('README.rst') as rst:
        version = rst.readline().split()[-1]
    # get libgphoto2 version to be swigged
    if sys.argv[1] == 'system':
        cmd = ['pkg-config', '--modversion', 'libgphoto2']
        FNULL = open(os.devnull, 'w')
        try:
            gphoto2_version = subprocess.check_output(
                cmd, stderr=FNULL, universal_newlines=True).strip()
        except Exception:
            print('ERROR: command "{}" failed'.format(' '.join(cmd)))
            raise
        gphoto2_version = '.'.join(gphoto2_version.split('.')[:3])
        gphoto2_include = subprocess.check_output(
                ['pkg-config', '--cflags-only-I', 'libgphoto2'],
                universal_newlines=True).strip().split()
        for n in range(len(gphoto2_include)):
            if gphoto2_include[n].endswith('/gphoto2'):
                gphoto2_include[n] = gphoto2_include[n][:-len('/gphoto2')]
    else:
        gphoto2_version = sys.argv[1]
        gphoto2_include = ['-I' + os.path.join(
            'libgphoto2-' + gphoto2_version, 'local_install', 'include')]
    # get list of modules (Python) and extensions (SWIG)
    file_names = os.listdir(os.path.join('src', 'gphoto2'))
    file_names.sort()
    file_names = [os.path.splitext(x) for x in file_names]
    ext_names = [x[0] for x in file_names if x[1] == '.i']
    py_names = [x[0] + x[1] for x in file_names if x[1] == '.py']
    # make options list
    swig_opts = ['-python', '-py3', '-nodefaultctor', '-O',
                 '-Wextra', '-Werror', '-builtin', '-nofastunpack']
    doc_file = os.path.join(
        'src', 'gphoto2', 'common', 'doc-' + gphoto2_version + '.i')
    output_dir = os.path.join('src', 'swig')
    output_dir += '-gp' + gphoto2_version
    os.makedirs(output_dir, exist_ok=True)
    version_opts = ['-outdir', output_dir]
    if os.path.isfile(doc_file):
        version_opts.append(
            '-DDOC_FILE=' + os.path.basename(doc_file))
    version_opts += gphoto2_include
    # do each swig module
    for ext_name in ext_names:
        cmd = ['swig'] + swig_opts + version_opts + ['-o']
        cmd += [os.path.join(output_dir, ext_name + '_wrap.c')]
        cmd += [os.path.join('src', 'gphoto2', ext_name + '.i')]
        print(' '.join(cmd))
        subprocess.check_output(cmd)
    # copy python modules
    for py_name in py_names:
        shutil.copy2(os.path.join('src', 'gphoto2', py_name), output_dir)
    # create init module
    init_file = os.path.join(output_dir, '__init__.py')
    with open(init_file, 'w') as im:
        im.write('__version__ = "{}"\n\n'.format(version))
        im.write('''
import os

_dir = os.path.dirname(__file__)
_camlibs = os.path.join(_dir, 'camlibs')
if os.path.isdir(_camlibs):
    os.environ['CAMLIBS'] = _camlibs
_iolibs = os.path.join(_dir, 'iolibs')
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

''')
        for name in ext_names:
            im.write('from gphoto2.{} import *\n'.format(name))
        im.write('''
__all__ = dir()
''')
    return 0


if __name__ == "__main__":
    sys.exit(main())
