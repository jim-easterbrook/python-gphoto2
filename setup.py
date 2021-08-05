# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-21  Jim Easterbrook  jim@jim-easterbrook.me.uk
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
import subprocess
import sys

# python-gphoto2 version
with open('README.rst') as rst:
    version = rst.readline().split()[-1]

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
            runtime_library_dirs = library_dirs,
            include_dirs = include_dirs,
            extra_compile_args = extra_compile_args,
            ))

cmdclass = {}
command_options = {}

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
