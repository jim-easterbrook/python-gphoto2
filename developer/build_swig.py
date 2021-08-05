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
import subprocess
import sys


def main(argv=None):
    # get root dir
    root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    # get python-gphoto2 version
    with open(os.path.join(root, 'README.rst')) as rst:
        version = rst.readline().split()[-1]
    # get gphoto2 library config
    cmd = ['pkg-config', '--modversion', 'libgphoto2']
    FNULL = open(os.devnull, 'w')
    try:
        gphoto2_version = subprocess.check_output(
            cmd, stderr=FNULL, universal_newlines=True).split('.')[:3]
        gphoto2_version = tuple(map(int, gphoto2_version))
    except Exception:
        print('ERROR: command "{}" failed'.format(' '.join(cmd)))
        raise
    gphoto2_flags = defaultdict(list)
    for flag in subprocess.check_output(
            ['pkg-config', '--cflags', '--libs', 'libgphoto2'],
            universal_newlines=True).split():
        gphoto2_flags[flag[:2]].append(flag)
    gphoto2_include  = gphoto2_flags['-I']
    gphoto2_libs     = gphoto2_flags['-l']
    gphoto2_lib_dirs = gphoto2_flags['-L']
    for n in range(len(gphoto2_include)):
        if gphoto2_include[n].endswith('/gphoto2'):
            gphoto2_include[n] = gphoto2_include[n][:-len('/gphoto2')]
    # get list of modules (Python) and extensions (SWIG)
    file_names = os.listdir(os.path.join(root, 'src', 'gphoto2'))
    file_names.sort()
    file_names = [os.path.splitext(x) for x in file_names]
    ext_names = [x[0] for x in file_names if x[1] == '.i']
    # get gphoto2 versions to be swigged
    gp_versions = []
    for name in os.listdir(root):
        match = re.match('libgphoto2-(.*)', name)
        if match:
            gp_versions.append(match.group(1))
    gp_versions.sort()
    if not gp_versions:
        gp_versions = ['.'.join(map(str, gphoto2_version[:2]))]
    print('swigging gphoto2 versions', str(gp_versions))
    # do -builtin and not -builtin
    swig_bis = [False]
    cmd = ['swig', '-version']
    try:
        swig_version = str(
            subprocess.check_output(cmd, universal_newlines=True))
    except Exception:
        print('ERROR: command "{}" failed'.format(' '.join(cmd)))
        raise
    for line in swig_version.split('\n'):
        if 'Version' in line:
            swig_version = tuple(map(int, line.split()[-1].split('.')))
            if swig_version != (2, 0, 11):
                swig_bis.append(True)
            break
    for use_builtin in swig_bis:
        # make options list
        swig_opts = ['-python', '-py3', '-nodefaultctor', '-O',
                     '-Wextra', '-Werror']
        if use_builtin:
            swig_opts += ['-builtin', '-nofastunpack']
        # do each gphoto2 version
        for gp_version in gp_versions:
            doc_file = os.path.join(
                root, 'src', 'gphoto2', 'common', 'doc-' + gp_version + '.i')
            output_dir = os.path.join(root, 'src', 'swig')
            if use_builtin:
                output_dir += '-bi'
            output_dir += '-gp' + gp_version
            os.makedirs(output_dir, exist_ok=True)
            version_opts = ['-outdir', output_dir]
            if os.path.isfile(doc_file):
                version_opts.append(
                    '-DDOC_FILE=' + os.path.basename(doc_file))
            inc_dir = os.path.join(root, 'libgphoto2-' + gp_version)
            if os.path.isdir(inc_dir):
                version_opts.append('-I' + inc_dir)
                version_opts.append(
                    '-I' + os.path.join(inc_dir, 'libgphoto2_port'))
            else:
                version_opts += gphoto2_include
            # do each swig module
            for ext_name in ext_names:
                cmd = ['swig'] + swig_opts + version_opts + ['-o']
                cmd += [os.path.join(root, output_dir, ext_name + '_wrap.c')]
                cmd += [os.path.join(root, 'src', 'gphoto2', ext_name + '.i')]
                print(' '.join(cmd))
                subprocess.check_output(cmd)
            # create init module
            init_file = os.path.join(root, output_dir, '__init__.py')
            with open(init_file, 'w') as im:
                im.write('__version__ = "{}"\n\n'.format(version))
                im.write('''
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
    # store SWIG version
    info_file = os.path.join(root, 'src', 'info.txt')
    with open(info_file, 'w') as info:
        info.write('swig_version = {}\n'.format(repr(swig_version)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
