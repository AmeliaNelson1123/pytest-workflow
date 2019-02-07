# Copyright (C) 2018 Leiden University Medical Center
# This file is part of pytest-workflow
#
# pytest-workflow is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# pytest-workflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with pytest-workflow.  If not, see <https://www.gnu.org/licenses/

"""This tests the marker functionality that was added"""

import textwrap

from .test_success_messages import SIMPLE_ECHO

TEST_HOOK = textwrap.dedent("""\
import pytest


@pytest.mark.workflow(name="simple echo")
def test_hook_impl(workflow_dir):
    print("This runs!")
    assert workflow_dir
""")


def test_hook_worked(testdir):
    testdir.makefile(".yml", test_simple=SIMPLE_ECHO)
    testdir.makefile(".py", test_hook=TEST_HOOK)
    result = testdir.runpytest()
    assert "This runs!" in result.stdout.str()