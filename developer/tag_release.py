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
import sys

# requires GitPython - 'sudo pip install gitpython'
import git


def main(argv=None):
    # get root dir
    root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    # get python-gphoto2 version
    with open(os.path.join(root, 'README.rst')) as rst:
        version = rst.readline().split()[-1]
    message = 'v' + version + '\n\n'
    with open(os.path.join(root, 'CHANGELOG.txt')) as cl:
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
    return 0

if __name__ == "__main__":
    sys.exit(main())
