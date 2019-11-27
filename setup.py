# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-19  Jim Easterbrook  jim@jim-easterbrook.me.uk
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
from distutils.cmd import Command
from distutils.command.upload import upload as _upload
from distutils.core import setup, Extension
from distutils.log import error
import os
import re
import subprocess
import sys

# python-gphoto2 version
version = '2.1.0'

# get gphoto2 library config
cmd = ['pkg-config', '--modversion', 'libgphoto2']
FNULL = open(os.devnull, 'w')
try:
    gphoto2_version = subprocess.check_output(
        cmd, stderr=FNULL, universal_newlines=True).split('.')[:3]
    gphoto2_version = tuple(map(int, gphoto2_version))
except Exception:
    error('ERROR: command "%s" failed', ' '.join(cmd))
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

# create extension modules list
ext_modules = []
info_file = os.path.join('src', 'info.txt')
if os.path.exists(info_file):
    with open(info_file) as src:
        code = compile(src.read(), info_file, 'exec')
        exec(code, globals(), locals())
else:
    swig_version = (0, 0, 0)
use_builtin = (swig_version != (2, 0, 11) and
               (swig_version >= (3, 0, 8) or sys.version_info < (3, 5)))
if 'PYTHON_GPHOTO2_BUILTIN' in os.environ:
    use_builtin = True
if 'PYTHON_GPHOTO2_NO_BUILTIN' in os.environ:
    use_builtin = False
mod_src_dir = 'swig'
if use_builtin:
    mod_src_dir += '-bi'
mod_src_dir += '-py' + str(sys.version_info[0])
mod_src_dir += '-gp' + '.'.join(map(str, gphoto2_version[:2]))
mod_src_dir = os.path.join('src', mod_src_dir)

extra_compile_args = [
    '-O3', '-Wno-unused-variable', '-Wno-unused-but-set-variable',
    '-Wno-unused-label', '-Wno-strict-prototypes',
    '-DGPHOTO2_VERSION=' + '0x{:02x}{:02x}{:02x}'.format(*gphoto2_version)]
if 'PYTHON_GPHOTO2_STRICT' in os.environ:
    extra_compile_args.append('-Werror')
libraries = [x.replace('-l', '') for x in gphoto2_libs]
library_dirs = [x.replace('-L', '') for x in gphoto2_lib_dirs]
include_dirs = [x.replace('-I', '') for x in gphoto2_include]
if os.path.isdir(mod_src_dir):
    for file_name in os.listdir(mod_src_dir):
        if file_name[-7:] != '_wrap.c':
            continue
        ext_name = file_name[:-7]
        ext_modules.append(Extension(
            '_' + ext_name,
            sources = [os.path.join(mod_src_dir, file_name)],
            libraries = libraries,
            library_dirs = library_dirs,
            include_dirs = include_dirs,
            extra_compile_args = extra_compile_args,
            ))

cmdclass = {}
command_options = {}

def get_gp_versions():
    # get gphoto2 versions to be swigged
    gp_versions = []
    for name in os.listdir('.'):
        match = re.match('libgphoto2-(.*)', name)
        if match:
            gp_versions.append(match.group(1))
    gp_versions.sort()
    if not gp_versions:
        gp_versions = ['.'.join(map(str, gphoto2_version[:2]))]
    return gp_versions

# add command to run doxygen and doxy2swig
class build_doc(Command):
    description = 'run doxygen to generate documentation'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        gp_versions = get_gp_versions()
        self.announce('making docs for gphoto2 versions %s' % str(gp_versions), 2)
        sys.path.append('doxy2swig')
        from doxy2swig import Doxy2SWIG
        for gp_version in gp_versions:
            src_dir = 'libgphoto2-' + gp_version
            os.chdir(src_dir)
            self.spawn(['doxygen', '../developer/Doxyfile'])
            os.chdir('..')
            index_file = os.path.join(src_dir, 'doc', 'xml', 'index.xml')
            self.announce('Doxy2SWIG ' + index_file, 2)
            p = Doxy2SWIG(index_file,
                          with_function_signature = False,
                          with_type_info = False,
                          with_constructor_list = False,
                          with_attribute_list = False,
                          with_overloaded_functions = False,
                          textwidth = 72,
                          quiet = True)
            p.generate()
            text = ''.join(p.pieces)
            member_methods = (
                ('gp_abilities_list_', '_CameraAbilitiesList', 'CameraAbilitiesList'),
                ('gp_camera_',         '_Camera',              'Camera'),
                ('gp_file_',           '_CameraFile',          'CameraFile'),
                ('gp_list_',           '_CameraList',          'CameraList'),
                ('gp_port_info_list_', '_GPPortInfoList',      'PortInfoList'),
                ('gp_port_info_',      '_GPPortInfo',          'PortInfo'),
                ('gp_widget_',         '_CameraWidget',        'CameraWidget'),
                )
            with open(os.path.join('src', 'gphoto2', 'common',
                                   'doc-' + gp_version + '.i'), 'w') as of:
                for match in re.finditer('%feature\("docstring"\) (\w+) \"(.+?)\";',
                                         text, re.DOTALL):
                    symbol = match.group(1)
                    value = match.group(2).strip()
                    if not value:
                        continue
                    for key, c_type, py_type in member_methods:
                        if symbol.startswith(key):
                            method = symbol.replace(key, '')
                            of.write(('%feature("docstring") {} "{}\n\n' +
                                      'See also gphoto2.{}.{}"\n\n').format(
                                          symbol, value, py_type, method))
                            of.write(('%feature("docstring") {}::{} "{}\n\n' +
                                      'See also gphoto2.{}"\n\n').format(
                                          c_type, method, value, symbol))
                            break
                    else:
                        of.write('%feature("docstring") {} "{}"\n\n'.format(
                            symbol, value))

cmdclass['build_doc'] = build_doc

# add command to run SWIG
class build_swig(Command):
    description = 'run SWIG to regenerate interface files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # get list of modules (Python) and extensions (SWIG)
        file_names = os.listdir(os.path.join('src', 'gphoto2'))
        file_names.sort()
        file_names = [os.path.splitext(x) for x in file_names]
        ext_names = [x[0] for x in file_names if x[1] == '.i']
        # get gphoto2 versions to be swigged
        gp_versions = get_gp_versions()
        self.announce('swigging gphoto2 versions %s' % str(gp_versions), 2)
        # do -builtin and not -builtin
        swig_bis = [False]
        cmd = ['swig', '-version']
        try:
            swig_version = str(subprocess.check_output(
                cmd, universal_newlines=True))
        except Exception:
            error('ERROR: command "%s" failed', ' '.join(cmd))
            raise
        for line in swig_version.split('\n'):
            if 'Version' in line:
                swig_version = tuple(map(int, line.split()[-1].split('.')))
                if swig_version != (2, 0, 11):
                    swig_bis.append(True)
                break
        for use_builtin in swig_bis:
            # make options list
            swig_opts = ['-python', '-nodefaultctor', '-O', '-Wextra', '-Werror']
            if use_builtin:
                swig_opts += ['-builtin', '-nofastunpack']
            # do each gphoto2 version
            for gp_version in gp_versions:
                doc_file = os.path.join(
                    'src', 'gphoto2', 'common', 'doc-' + gp_version + '.i')
                # do Python 2 and 3
                for py_version in 2, 3:
                    output_dir = os.path.join('src', 'swig')
                    if use_builtin:
                        output_dir += '-bi'
                    output_dir += '-py' + str(py_version)
                    output_dir += '-gp' + gp_version
                    self.mkpath(output_dir)
                    version_opts = ['-outdir', output_dir]
                    if os.path.isfile(doc_file):
                        version_opts.append(
                            '-DDOC_FILE=' + os.path.basename(doc_file))
                    inc_dir = 'libgphoto2-' + gp_version
                    if os.path.isdir(inc_dir):
                        version_opts.append('-I' + inc_dir)
                        version_opts.append(
                            '-I' + os.path.join(inc_dir, 'libgphoto2_port'))
                    else:
                        version_opts += gphoto2_include
                    if py_version >= 3:
                        version_opts.append('-py3')
                    # do each swig module
                    for ext_name in ext_names:
                        in_file = os.path.join('src', 'gphoto2', ext_name + '.i')
                        out_file = os.path.join(output_dir, ext_name + '_wrap.c')
                        self.spawn(['swig'] + swig_opts + version_opts +
                                   ['-o', out_file, in_file])
                    # create init module
                    init_file = os.path.join(output_dir, '__init__.py')
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
        info_file = os.path.join('src', 'info.txt')
        with open(info_file, 'w') as info:
            info.write('swig_version = {}\n'.format(repr(swig_version)))

cmdclass['build_swig'] = build_swig

# modify upload class to add appropriate git tag
# requires GitPython - 'sudo pip install gitpython --pre'
try:
    import git
    class upload(_upload):
        def run(self):
            message = 'v' + version + '\n\n'
            with open('CHANGELOG.txt') as cl:
                while not cl.readline().startswith('Changes'):
                    pass
                while True:
                    line = cl.readline().strip()
                    if not line:
                        break
                    message += line + '\n'
            repo = git.Repo()
            tag = repo.create_tag('v' + version, message=message)
            remote = repo.remotes.origin
            remote.push(tags=True)
            return _upload.run(self)
    cmdclass['upload'] = upload
except ImportError:
    pass

# set options for building distributions
command_options['sdist'] = {
    'formats' : ('setup.py', 'gztar'),
    }

# list example scripts
examples = [os.path.join('examples', x)
            for x in os.listdir('examples') if os.path.splitext(x)[1] == '.py']

with open('README.rst') as ldf:
    long_description = ldf.read()

setup(name = 'gphoto2',
      version = version,
      description = 'Python interface to libgphoto2',
      long_description = long_description,
      author = 'Jim Easterbrook',
      author_email = 'jim@jim-easterbrook.me.uk',
      url = 'https://github.com/jim-easterbrook/python-gphoto2',
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: MacOS',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: BSD :: FreeBSD',
          'Operating System :: POSIX :: BSD :: NetBSD',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Multimedia',
          'Topic :: Multimedia :: Graphics',
          'Topic :: Multimedia :: Graphics :: Capture',
          ],
      platforms = ['POSIX', 'MacOS'],
      license = 'GNU GPL',
      cmdclass = cmdclass,
      command_options = command_options,
      ext_package = 'gphoto2',
      ext_modules = ext_modules,
      packages = ['gphoto2'],
      package_dir = {'gphoto2' : mod_src_dir},
      data_files = [
          ('share/python-gphoto2/examples', examples),
          ('share/python-gphoto2', [
              'CHANGELOG.txt', 'LICENSE.txt', 'README.rst']),
          ],
      )
