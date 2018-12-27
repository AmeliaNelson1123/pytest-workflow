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

import textwrap
from typing import List, Tuple  # noqa: F401  # Used in comments

import pytest

# message tests. Form: a tuple of a yaml file and expected messages.
MESSAGE_TESTS = [
    ("""\
    - name: fail_test
      command: grep
    """,
     ["The workflow exited with exit code '2' instead of '0'"]),
    ("""\
    - name: create file
      command: echo moo
      files:
        - path: moo
    """,
     ["moo' does not exist while it should"]),
    ("""\
    - name: echo something
      command: touch moo
      files:
        - path: moo
          should_exist: false
    """,
     ["moo' does exist while it should not"]),
    ("""\
    - name: moo file
      command: bash -c 'echo moo > moo.txt'
      files:
        - path: moo.txt
          md5sum: e583af1f8b00b53cda87ae9ead880225
    """,
     ["Observed md5sum 'e583af1f8b00b53cda87ae9ead880224' not equal to "
      "expected md5sum 'e583af1f8b00b53cda87ae9ead880225' for file",
      "moo.txt'"])
]  # type: List[Tuple[str,List[str]]]


@pytest.mark.parametrize(["test", "messages"], MESSAGE_TESTS)
def test_messages(test: str, messages: List[str], testdir):
    testdir.makefile(".yml", textwrap.dedent(test))
    result = testdir.runpytest()
    for message in messages:
        assert message in result.stdout.str()
