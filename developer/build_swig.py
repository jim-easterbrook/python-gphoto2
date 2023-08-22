# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2021-23  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This file is part of python-gphoto2.
#
# python-gphoto2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# python-gphoto2 is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with python-gphoto2.  If not, see
# <https://www.gnu.org/licenses/>.

import os
import shutil
import subprocess
import sys


def main(argv=None):
    # system or local libexiv2?
    if len(sys.argv) > 2:
        print('Usage: %s [prefix]' % sys.argv[0])
        return 1
    if len(sys.argv) > 1:
        for root, dirs, files in os.walk(sys.argv[1]):
            if 'libgphoto2.pc' in files:
                os.environ['PKG_CONFIG_PATH'] = root
                break
        else:
            print('No package config file found')
            return 2
    # get python-gphoto2 version
    with open('README.rst') as rst:
        version = rst.readline().split()[-1]
    # get libgphoto2 version to be swigged
    cmd = ['pkg-config', '--modversion', 'libgphoto2']
    FNULL = open(os.devnull, 'w')
    try:
        gphoto2_version_str = subprocess.check_output(
            cmd, stderr=FNULL, universal_newlines=True).strip()
    except Exception:
        print('ERROR: command "{}" failed'.format(' '.join(cmd)))
        raise
    gphoto2_include = subprocess.check_output(
            ['pkg-config', '--cflags-only-I', 'libgphoto2'],
            universal_newlines=True).strip().split()
    for n in range(len(gphoto2_include)):
        if gphoto2_include[n].endswith('/gphoto2'):
            gphoto2_include[n] = gphoto2_include[n][:-len('/gphoto2')]
    # get list of modules (Python) and extensions (SWIG)
    file_names = os.listdir(os.path.join('src', 'gphoto2'))
    file_names.sort()
    file_names = [os.path.splitext(x) for x in file_names]
    ext_names = [x[0] for x in file_names if x[1] == '.i']
    py_names = [x[0] + x[1] for x in file_names if x[1] == '.py']
    # get SWIG version
    cmd = ['swig', '-version']
    try:
        swig_version = str(subprocess.Popen(
            cmd, stdout=subprocess.PIPE,
            universal_newlines=True).communicate()[0])
    except Exception:
        print('ERROR: command "%s" failed' % ' '.join(cmd))
        raise
    for line in swig_version.splitlines():
        if 'Version' in line:
            swig_version = tuple(map(int, line.split()[-1].split('.')))
            break
    # make options list
    swig_opts = ['-python', '-nodefaultctor', '-O',
                 '-Wextra', '-Werror', '-builtin', '-nofastunpack']
    if swig_version < (4, 1, 0):
        swig_opts.append('-py3')
    doc_file = os.path.join('src', 'gphoto2', 'common', 'doc.i')
    output_dir = os.path.join('src', 'swig')
    output_dir += '-gp' + gphoto2_version_str.replace('.', '_')
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

''')
        for name in ext_names:
            im.write('from gphoto2.{} import *\n'.format(name))
        im.write('''
_locale = os.path.join(_dir, 'libgphoto2', 'locale')
if os.path.isdir(_locale):
    gphoto2.abilities_list.gp_init_localedir(_locale)

__all__ = dir()
''')
    return 0


if __name__ == "__main__":
    sys.exit(main())
