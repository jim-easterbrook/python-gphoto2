# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-24  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

from collections import defaultdict
from setuptools import setup, Extension
from setuptools import __version__ as setuptools_version
import os
import subprocess
import sys

packages = ['gphoto2', 'gphoto2.examples']
package_dir = {'gphoto2.examples': 'examples'}
package_data = {'gphoto2.examples': ['*']}
exclude_package_data = {'': ['*.c']}
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
    # get gphoto2 libs
    lib_dir = subprocess.check_output(
        ['pkg-config', '--variable=libdir', 'libgphoto2'],
        universal_newlines=True).strip()
    packages.append('gphoto2.libgphoto2')
    package_dir['gphoto2.libgphoto2'] = os.path.relpath(lib_dir)
    package_data['gphoto2.libgphoto2'] = []
    # choose the libx.so.n versions of all the .so files and links
    for name in os.listdir(lib_dir):
        if (name.startswith('libgphoto') and '.so.' in name
                and len(name.split('.')) == 3):
            package_data['gphoto2.libgphoto2'].append(name)
    # get cam libs
    packages.append('gphoto2.libgphoto2.camlibs')
    lib_dir = subprocess.check_output(
        ['pkg-config', '--variable=driverdir', 'libgphoto2'],
        universal_newlines=True).strip()
    package_dir['gphoto2.libgphoto2.camlibs'] = os.path.relpath(lib_dir)
    package_data['gphoto2.libgphoto2.camlibs'] = ['*.so']
    # get io libs
    packages.append('gphoto2.libgphoto2.iolibs')
    lib_dir = subprocess.check_output(
        ['pkg-config', '--variable=driverdir', 'libgphoto2_port'],
        universal_newlines=True).strip()
    package_dir['gphoto2.libgphoto2.iolibs'] = os.path.relpath(lib_dir)
    package_data['gphoto2.libgphoto2.iolibs'] = []
    for name in os.listdir(lib_dir):
        if name == 'vusb.so':
            packages.append('gphoto2.libgphoto2.vusb')
            package_dir['gphoto2.libgphoto2.vusb'] = os.path.relpath(lib_dir)
            package_data['gphoto2.libgphoto2.vusb'] = [name]
        elif name.endswith('.so'):
            package_data['gphoto2.libgphoto2.iolibs'].append(name)
    # get localisation files
    prefix = subprocess.check_output(
        ['pkg-config', '--variable=prefix', 'libgphoto2'],
        universal_newlines=True).strip()
    locale_dir = os.path.join(prefix, 'share', 'locale')
    if os.path.isdir(locale_dir):
        packages.append('gphoto2.libgphoto2.locale')
        package_dir['gphoto2.libgphoto2.locale'] = os.path.relpath(locale_dir)
        package_data['gphoto2.libgphoto2.locale'] = [
            '*/LC_MESSAGES/libgphoto2*.mo']
        for name in os.listdir(locale_dir):
            packages.append(
                'gphoto2.libgphoto2.locale.' + name + '.LC_MESSAGES')
    # module compile options
    extra_link_args = ['-Wl,-rpath,$ORIGIN/libgphoto2']
    if sys.platform == 'linux':
        extra_link_args += ['-Wl,--disable-new-dtags']

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
    swigged_version = name.replace('swig-gp', '').split('_')
    swigged_versions.append(tuple(map(int, swigged_version)))
swigged_versions.sort()

# choose best match from swigged versions
gphoto2_version = tuple(map(int, gphoto2_version_str.split('.')))
if gphoto2_version < (2, 5, 10):
    raise RuntimeError('libgphoto2 version 2.5.10 or later is required')
while len(swigged_versions) > 1 and swigged_versions[0] < gphoto2_version:
    swigged_versions = swigged_versions[1:]
swigged_version = swigged_versions[0]

# create extension modules list
ext_modules = []
mod_src_dir = 'swig-gp' + '_'.join(map(str, swigged_version))
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
        include_dirs = include_dirs,
        extra_compile_args = extra_compile_args,
        define_macros = define_macros,
        extra_link_args = extra_link_args,
        ))

setup_kwds = {
    'ext_package': 'gphoto2',
    'ext_modules': ext_modules,
    'packages': packages,
    'package_dir': package_dir,
    'package_data': package_data,
    'exclude_package_data': exclude_package_data,
    'include_package_data': False,
    }

if tuple(map(int, setuptools_version.split('.')[:2])) < (61, 0):
    # get metadata from pyproject.toml
    import toml
    metadata = toml.load('pyproject.toml')

    with open(metadata['project']['readme']) as ldf:
        long_description = ldf.read()
        # python-gphoto2 version
        version = long_description.split('\n')[0].split()[-1]

    setup_kwds.update(
        name = metadata['project']['name'],
        version = version,
        description = metadata['project']['description'],
        long_description = long_description,
        author = metadata['project']['authors'][0]['name'],
        author_email = metadata['project']['authors'][0]['email'],
        url = metadata['project']['urls']['homepage'],
        classifiers = metadata['project']['classifiers'],
        platforms = metadata['tool']['setuptools']['platforms'],
        license = metadata['project']['license']['text'],
        zip_safe = metadata['tool']['setuptools']['zip-safe'],
        )

setup(**setup_kwds)
