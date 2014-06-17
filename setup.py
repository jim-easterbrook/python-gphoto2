#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
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
import os
import subprocess
import sys

gphoto2_version = str(subprocess.check_output(['gphoto2-config', '--version']))
gphoto2_version = tuple(gphoto2_version.split()[1].split('.'))

mod_names = list(map(lambda x: x[0],
                     filter(lambda x: x[1] == '.i',
                            map(os.path.splitext, os.listdir('source/lib')))))
mod_names.sort()

ext_modules = []
init_module = ''
swig_opts = ['-I/usr/include', '-builtin', '-O', '-Wall']
if sys.version_info[0] >= 3:
    swig_opts.append('-py3')
if gphoto2_version[0:2] == ('2', '4'):
    swig_opts. append('-DGPHOTO2_24')
elif gphoto2_version[0:2] == ('2', '5'):
    swig_opts. append('-DGPHOTO2_25')
for mod_name in mod_names:
    ext_modules.append(Extension(
        '_%s' % mod_name,
        sources = ['source/lib/%s.i' % mod_name],
        swig_opts = swig_opts,
        libraries = ['gphoto2', 'gphoto2_port'],
        extra_compile_args = ['-O3', '-Wno-unused-variable'],
        ))
    init_module += 'from .%s import *\n' % mod_name

old_init_module = open('source/lib/__init__.py', 'r').read()
if init_module != old_init_module:
    open('source/lib/__init__.py', 'w').write(init_module)

version = '0.2.0'

with open('README.rst') as ldf:
    long_description = ldf.read()

setup(name = 'gphoto2',
      version = version,
      description = 'Python interface to libgphoto2',
      long_description = long_description,
      author = 'Jim Easterbrook',
      author_email = 'jim@jim-easterbrook.me.uk',
      url = 'https://github.com/jim-easterbrook/python-gphoto2',
      download_url = 'https://github.com/jim-easterbrook/python-gphoto2/archive/master.zip#egg=gphoto2-%s' % version,
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
      ext_package = 'gphoto2.lib',
      ext_modules = ext_modules,
      packages = ['gphoto2', 'gphoto2.lib'],
      package_dir = {'gphoto2' : 'source'},
      )
