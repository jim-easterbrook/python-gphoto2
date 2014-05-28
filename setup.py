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

mod_names = map(lambda x: x[0],
                filter(lambda x: x[1] == '.i',
                       map(os.path.splitext, os.listdir('source'))))
mod_names.sort()

ext_modules = []
init_module = ''
for mod_name in mod_names:
    ext_modules.append(Extension(
        '_%s' % mod_name,
        sources = ['source/%s.i' % mod_name],
        swig_opts = ['-I/usr/include', '-builtin', '-O', '-Wall'],
        libraries = ['gphoto2', 'gphoto2_port'],
        extra_compile_args = ['-O3', '-Wno-unused-variable'],
        ))
    init_module += 'from .%s import *\n' % mod_name

old_init_module = open('source/__init__.py', 'r').read()
if init_module != old_init_module:
    open('source/__init__.py', 'w').write(init_module)

version = '0.1'

setup(name = 'gphoto2',
      version = version,
      description = 'Python interface to libgphoto2',
      author = 'Jim Easterbrook',
      author_email = 'jim@jim-easterbrook.me.uk',
      url = 'http://jim-easterbrook.github.com/python-gphoto2/',
      ext_package = 'gphoto2',
      ext_modules = ext_modules,
      packages = ['gphoto2'],
      package_dir = {'gphoto2' : 'source'},
      )
