# Copyright (C) 2018 Leiden University Medical Center
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/

"""Tests whether the temporary directories are correctly saved/destroyed"""

import re
import tempfile
from pathlib import Path

from .test_success_messages import SIMPLE_ECHO


def test_log_messages(testdir):
    testdir.makefile(".yml", test=SIMPLE_ECHO)
    result = testdir.runpytest("-v", "--keep-workflow-wd")
    assert "'simple echo' stdout saved in: " in result.stdout.str()
    assert "'simple echo' stderr saved in: " in result.stdout.str()


def test_not_log_messages(testdir):
    testdir.makefile(".yml", test=SIMPLE_ECHO)
    result = testdir.runpytest("-v")
    assert "'simple echo' stdout saved in: " not in result.stdout.str()
    assert "'simple echo' stderr saved in: " not in result.stdout.str()


def test_directory_kept(testdir):
    testdir.makefile(".yml", test=SIMPLE_ECHO)
    result = testdir.runpytest("-v", "--keep-workflow-wd")
    working_dir = re.search(r"with command 'echo moo' in '(.*)'",
                            result.stdout.str()).group(1)
    assert Path(working_dir).exists()
    assert Path(working_dir / Path("log.out")).exists()
    assert Path(working_dir / Path("log.err")).exists()


def test_directory_not_kept(testdir):
    testdir.makefile(".yml", test=SIMPLE_ECHO)
    result = testdir.runpytest("-v")
    working_dir = re.search(r"with command 'echo moo' in '(.*)'",
                            result.stdout.str()).group(1)
    assert not Path(working_dir).exists()


def test_basetemp_correct(testdir):
    testdir.makefile(".yml", test=SIMPLE_ECHO)
    tempdir = tempfile.mkdtemp()
    result = testdir.runpytest("-v", "--basetemp", tempdir)
    assert str(tempdir) in result.stdout.str()


def test_basetemp_can_be_used_twice(testdir):
    testdir.makefile(".yml", test=SIMPLE_ECHO)
    tempdir = tempfile.mkdtemp()
    # First run to fill up tempdir
    testdir.runpytest("-v", "--keep-workflow-wd", "--basetemp", tempdir)
    # Make sure directory is there.
    assert (Path(tempdir) / Path("simple_echo")).exists()
    # Run again with same basetemp.
    result = testdir.runpytest("-v", "--keep-workflow-wd", "--basetemp",
                               tempdir)
    exit_code = result.ret
    assert "'{0}/simple_echo' already exists. Deleting ...".format(
        tempdir) in result.stdout.str()
    assert exit_code == 0
