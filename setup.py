#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-15  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

from distutils.core import setup, Extension
from distutils.command.build import build
from distutils.command.upload import upload
import os
import shlex
import subprocess
import sys

# python-gphoto2 version
version = '0.10.3'

# get gphoto2 library config
gphoto2_version = str(subprocess.check_output(
    ['pkg-config', '--modversion', 'libgphoto2'],
    universal_newlines=True)).strip().split('.')
gphoto2_include = subprocess.check_output(
    ['pkg-config', '--cflags-only-I', 'libgphoto2'],
    universal_newlines=True).strip().split()
gphoto2_libs = str(subprocess.check_output(
    ['pkg-config', '--libs-only-l', 'libgphoto2'],
    universal_newlines=True)).strip().split()
for n in range(len(gphoto2_include)):
    if gphoto2_include[n].endswith('/gphoto2'):
        gphoto2_include[n] = gphoto2_include[n][:-len('/gphoto2')]

# get SWIG version
swig_version = str(subprocess.check_output(
    ['swig', '-version'], universal_newlines=True))
for line in swig_version.split('\n'):
    if 'Version' in line:
        swig_version = line.split()[-1]
        break
else:
    swig_version = 'unknown'

# get list of modules
mod_names = filter(lambda x: x[0].startswith('gphoto2') and x[1] == '.i',
                   map(os.path.splitext, os.listdir('src/gphoto2')))
mod_names = list(map(lambda x: x[0], mod_names))
mod_names.sort()

# create extension modules list
ext_modules = []
version_macro = 'GPHOTO2_' + ''.join(gphoto2_version[:2])
swig_opts = ['-nodefaultctor', '-O', '-Wextra', '-Werror', '-MMD',
             '-D' + version_macro]
if swig_version != '2.0.11':
    swig_opts.append('-builtin')
extra_compile_args = [
    '-O3', '-Wno-unused-variable', '-Wno-strict-prototypes', '-Werror']
if sys.version_info[0] >= 3:
    swig_opts.append('-py3')
swig_opts = swig_opts + gphoto2_include
libraries = list(map(lambda x: x[2:], gphoto2_libs))
for mod_name in mod_names:
    depends = []
    dep_file = 'src/gphoto2/{}_wrap.d'.format(mod_name)
    if os.path.exists(dep_file):
        with open(dep_file) as df:
            for token in shlex.split(df.read()):
                token = token.strip()
                if token and not token.endswith(':'):
                    depends.append(token)
    ext_modules.append(Extension(
        '_' + mod_name,
        sources = ['src/gphoto2/{}.i'.format(mod_name)],
        swig_opts = swig_opts,
        libraries = libraries,
        extra_compile_args = extra_compile_args,
        define_macros = [(version_macro, None)],
        depends = depends,
        ))

# rewrite init module, if needed
init_file = 'src/gphoto2/__init__.py'
init_module = '__version__ = "{}"\n\n'.format(version)
for mod_name in mod_names:
    init_module += 'from gphoto2.{} import *\n'.format(mod_name)
if os.path.isfile(init_file):
    with open(init_file) as im:
        old_init_module = im.read()
else:
    old_init_module = None
if init_module != old_init_module:
    with open(init_file, 'w') as im:
        im.write(init_module)

cmdclass = {}
command_options = {}

# redefine 'build' command so SWIG extensions get compiled first, as
# they create .py files that then need to be installed
class SWIG_build(build):
    sub_commands = list(build.sub_commands)
    _build_ext = list(filter(lambda x: x[0]=='build_ext', sub_commands))[0]
    sub_commands.remove(_build_ext)
    sub_commands.insert(0, _build_ext)
cmdclass['build'] = SWIG_build

# modify upload class to add appropriate git tag
# requires GitPython - 'sudo pip install gitpython --pre'
try:
    import git
    class upload_and_tag(upload):
        def run(self):
            message = ''
            with open('CHANGELOG.txt') as cl:
                while not cl.readline().startswith('Changes'):
                    pass
                while True:
                    line = cl.readline().strip()
                    if not line:
                        break
                    message += line + '\n'
            repo = git.Repo()
            tag = repo.create_tag('gphoto2-' + version, message=message)
            remote = repo.remotes.origin
            remote.push(tags=True)
            return upload.run(self)
    cmdclass['upload'] = upload_and_tag
except ImportError:
    pass

# set options for building distributions
command_options['sdist'] = {
    'formats' : ('setup.py', 'gztar zip'),
    }

# list example scripts
examples = map(
    lambda x: os.path.join('examples', x),
    filter(lambda x: os.path.splitext(x)[1] == '.py', os.listdir('examples')))

with open('README.rst') as ldf:
    long_description = ldf.read()
url = 'https://github.com/jim-easterbrook/python-gphoto2'

setup(name = 'gphoto2',
      version = version,
      description = 'Python interface to libgphoto2',
      long_description = long_description,
      author = 'Jim Easterbrook',
      author_email = 'jim@jim-easterbrook.me.uk',
      url = url,
      download_url = url + '/archive/gphoto2-' + version + '.tar.gz',
      classifiers = [
          'Development Status :: 4 - Beta',
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
      package_dir = {'' : 'src'},
      data_files = [
          ('share/python-gphoto2/examples', examples),
          ('share/python-gphoto2', [
              'CHANGELOG.txt', 'LICENSE.txt', 'README.rst']),
          ],
      )
