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

import os
import re
import subprocess
import sys

sys.path.append('doxy2swig')
from doxy2swig import Doxy2SWIG


member_methods = (
    ('gp_abilities_list_', '_CameraAbilitiesList', 'CameraAbilitiesList'),
    ('gp_camera_',         '_Camera',              'Camera'),
    ('gp_context_',        '_GPContext',           'Context'),
    ('gp_file_',           '_CameraFile',          'CameraFile'),
    ('gp_list_',           '_CameraList',          'CameraList'),
    ('gp_port_info_list_', '_GPPortInfoList',      'PortInfoList'),
    ('gp_port_info_',      '_GPPortInfo',          'PortInfo'),
    ('gp_widget_',         '_CameraWidget',        'CameraWidget'),
    )

def add_member_doc(symbol, value):
    for key, c_type, py_type in member_methods:
        if symbol.startswith(key):
            method = symbol.replace(key, '')
            if method == 'new':
                return ('%feature("docstring") {} "{}\n\n' +
                        'See also gphoto2.{}"\n\n').format(
                            symbol, value, py_type)
            return ('%feature("docstring") {} "{}\n\n' +
                    'See also gphoto2.{}.{}"\n\n' +
                    '%feature("docstring") {}::{} "{}\n\n' +
                    'See also gphoto2.{}"\n\n').format(
                        symbol, value, py_type, method,
                        c_type, method, value, symbol)
    return '%feature("docstring") {} "{}"\n\n'.format(symbol, value)

def main(argv=None):
    # get gphoto2 version to be processed
    if len(sys.argv) != 2:
        print('Usage: %s version' % sys.argv[0])
        return 1
    gp_version = sys.argv[1]
    src_dir = os.path.join('libgphoto2-' + gp_version)
    os.chdir(src_dir)
    print('doxygen', src_dir)
    subprocess.check_output(['doxygen', '../developer/Doxyfile'])
    os.chdir('..')
    index_file = os.path.join(src_dir, 'doc', 'xml', 'index.xml')
    print('Doxy2SWIG ' + index_file)
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
    with open(os.path.join('src', 'gphoto2', 'common',
                           'doc-' + gp_version + '.i'), 'w') as of:
        for match in re.finditer('%feature\("docstring"\) (\w+) \"(.+?)\";',
                                 text, re.DOTALL):
            symbol = match.group(1)
            value = match.group(2).strip()
            if not value:
                continue
            of.write(add_member_doc(symbol, value))
    return 0

if __name__ == "__main__":
    sys.exit(main())
