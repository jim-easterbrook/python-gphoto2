# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-23  Jim Easterbrook  jim@jim-easterbrook.me.uk
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
from setuptools import setup, Extension
import os
import subprocess
import sys

# python-gphoto2 version
with open('README.rst') as rst:
    version = rst.readline().split()[-1]

packages = ['gphoto2', 'gphoto2.examples']
package_dir = {'gphoto2.examples': 'examples'}
package_data = {'gphoto2.examples': ['*']}
extra_link_args = []

if 'GPHOTO2_ROOT' in os.environ:
    # using a local build of libgphoto2
    gphoto2_dir = os.environ['GPHOTO2_ROOT']
    gphoto2_dir = os.path.expanduser(gphoto2_dir)
    if not os.path.isabs(gphoto2_dir):
        raise RuntimeError('GPHOTO2_ROOT is not an absolute path')
    print('Using libgphoto2 from {}'.format(gphoto2_dir))
    for root, dirs, files in os.walk(gphoto2_dir):
        if 'libgphoto2.pc' in files:
            os.environ['PKG_CONFIG_PATH'] = root
            break
    else:
        raise RuntimeError('No package config file found')
    lib_dir = subprocess.check_output(
        ['pkg-config', '--variable=libdir', 'libgphoto2'],
        universal_newlines=True).strip()
    packages.append('gphoto2.libs')
    package_dir['gphoto2.libs'] = lib_dir
    package_data['gphoto2.libs'] = []
    # choose the libx.so.n versions of all the .so files and links
    for name in os.listdir(lib_dir):
        if '.so.' in name and len(name.split('.')) == 3:
            package_data['gphoto2.libs'].append(name)
    # get cam libs and io libs
    packages.append('gphoto2.camlibs')
    package_dir['gphoto2.camlibs'] = subprocess.check_output(
        ['pkg-config', '--variable=driverdir', 'libgphoto2'],
        universal_newlines=True).strip()
    package_data['gphoto2.camlibs'] = ['*.so']
    packages.append('gphoto2.iolibs')
    package_dir['gphoto2.iolibs'] = subprocess.check_output(
        ['pkg-config', '--variable=driverdir', 'libgphoto2_port'],
        universal_newlines=True).strip()
    package_data['gphoto2.iolibs'] = ['*.so']
    # add localisation files
    prefix = subprocess.check_output(
        ['pkg-config', '--variable=prefix', 'libgphoto2'],
        universal_newlines=True).strip()
    locale_dir = os.path.join(prefix, 'share', 'locale')
    if os.path.isdir(locale_dir):
        packages.append('gphoto2.locale')
        package_dir['gphoto2.locale'] = locale_dir
        package_data['gphoto2.locale'] = ['*/LC_MESSAGES/libgphoto2*.mo']
    # module compile options
    extra_link_args = ['-Wl,-rpath,$ORIGIN/libs']

cmd = ['pkg-config', '--modversion', 'libgphoto2']
FNULL = open(os.devnull, 'w')
try:
    gphoto2_version_str = subprocess.check_output(
        cmd, stderr=FNULL, universal_newlines=True).strip()
except Exception:
    raise RuntimeError('ERROR: command "%s" failed' % ' '.join(cmd))
print('Using libgphoto2 v{}'.format(gphoto2_version_str))
# get libgphoto2 config
gphoto2_flags = defaultdict(list)
for flag in subprocess.check_output(
        ['pkg-config', '--cflags', '--libs', 'libgphoto2'],
        universal_newlines=True).split():
    gphoto2_flags[flag[:2]].append(flag)
gphoto2_include  = gphoto2_flags['-I']
for n in range(len(gphoto2_include)):
    if gphoto2_include[n].endswith('/gphoto2'):
        gphoto2_include[n] = gphoto2_include[n][:-len('/gphoto2')]
libraries = [x.replace('-l', '') for x in gphoto2_flags['-l']]
library_dirs = [x.replace('-L', '') for x in gphoto2_flags['-L']]
include_dirs = [x.replace('-I', '') for x in gphoto2_include]

# get list of available swigged versions
swigged_versions = []
for name in os.listdir('src'):
    if not name.startswith('swig-gp'):
        continue
    swigged_version = name.replace('swig-gp','').split('.')
    swigged_versions.append(tuple(map(int, swigged_version)))
swigged_versions.sort()

# choose best match from swigged versions
gphoto2_version = tuple(map(int, gphoto2_version_str.split('.')))
while len(swigged_versions) > 1 and swigged_versions[0] < gphoto2_version:
    swigged_versions = swigged_versions[1:]
swigged_version = swigged_versions[0]

# create extension modules list
ext_modules = []
mod_src_dir = 'swig-gp' + '.'.join(map(str, swigged_version))
mod_src_dir = os.path.join('src', mod_src_dir)
package_dir['gphoto2'] = mod_src_dir

extra_compile_args = [
    '-O3', '-Wno-unused-variable', '-Wno-unused-but-set-variable',
    '-Wno-unused-label', '-Wno-strict-prototypes']
if 'PYTHON_GPHOTO2_STRICT' in os.environ:
    extra_compile_args.append('-Werror')
define_macros = [('GPHOTO2_VERSION',
                  '0x{:02x}{:02x}{:02x}{:02x}'.format(*gphoto2_version, 0, 0)),
                 ('SWIG_TYPE_TABLE', 'gphoto2')]
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
        define_macros = define_macros,
        extra_link_args = extra_link_args,
        ))

command_options = {}

# set options for building distributions
command_options['sdist'] = {
    'formats' : ('setup.py', 'gztar'),
    }

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
      command_options = command_options,
      ext_package = 'gphoto2',
      ext_modules = ext_modules,
      packages = packages,
      package_dir = package_dir,
      package_data = package_data,
      zip_safe = False,
      )
