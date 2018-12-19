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

"""This contains all the classes and methods for content testing of files
and logs."""

from pathlib import Path
from typing import Dict, Iterable, List

import pytest

from .schema import ContentTest


def check_content(strings: List[str],
                  text_lines: Iterable[str]) -> Dict[str, bool]:
    """
    Checks whether any of the strings is present in the text lines
    This function is optimized for big texts, it stops searching when
    everything is found.
    :param strings: A list of strings for which the present is checked
    :param text_lines: The lines of text that need to be searched.
    :return:
    """
    # Make a copy of the list here to prevent aliasing.
    not_found_strings = list(strings)
    # By default all strings are not found.
    found_dictionary = {key: False for key in not_found_strings}

    for line in text_lines:
        # Break the loop if the list of not found strings is empty.
        if not not_found_strings:
            break
        for string in not_found_strings:
            if string in line:
                found_dictionary[string] = True
                not_found_strings.remove(string)

    return found_dictionary


def file_to_string_generator(filepath: Path) -> Iterable[str]:
    """
    Turns a file into a line generator.
    :param filepath: the file path
    :return: yields lines of the file
    """
    with filepath.open("r") as f:  # Use 'r' here explicitly as opposed to 'rb'
        for line in f:
            yield line


def generate_content_tests(
        parent: pytest.Collector,
        text_lines: Iterable[str],
        contains: List[str],
        must_not_contain: List[str],
        test_name_prefix: str = "") -> List[pytest.Item]:
    """
    Checks text lines for content. Spawns test items that indicate whether
    certain strings have been found or not.
    :param parent: The parent for the test items.
    :param text_lines: The lines of text to search.
    :param contains: The strings that should be in the text lines
    :param must_not_contain: The strings that should not be in the text lines
    :param test_name_prefix: a text prefix for the test name.
    :return: 
    """
    found_dictionary = check_content(contains + must_not_contain, text_lines)

    test_items = []

    # Check whether `contains` strings have been found
    test_items += [
        GenericTest(
            name=test_name_prefix + "contains '{0}'".format(string),
            parent=parent,
            result=found_dictionary[string]
        )
        for string in contains]

    # Check whether `must_not_contain` strings have been found
    test_items += [
        GenericTest(
            name=test_name_prefix + "does not contain '{0}".format(string),
            parent=parent,
            result=not found_dictionary[string]  # If not found, result should
            # be True, so the test succeeds.
        )
        for string in must_not_contain]

    return test_items


def generate_log_tests(
        parent: pytest.Collector,
        log: bytes,
        log_test: ContentTest,
        prefix: str) -> List[pytest.Item]:
    """A helper function that calls generate_content_tests and does
    the necessary conversions for workflow log testing."""
    return generate_content_tests(
        parent=parent,
        # Convert log bytestring to unicode strings
        text_lines=[str(line) for line in log.splitlines(keepends=True)],
        contains=log_test.contains,
        must_not_contain=log_test.must_not_contain,
        test_name_prefix=prefix)


class GenericTest(pytest.Item):
    """Test that can be used to report a failing or succeeding test
    in the log"""

    def __init__(self, name: str, parent: pytest.Collector, result: bool):
        """
        Create a GenericTest item
        :param name: The name of the test
        :param parent: A pytest Collector from which the test originates
        :param result: Whether the test has succeeded.
        """
        super().__init__(name, parent=parent)
        self.result = result

    def runtest(self):
        assert self.result
