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

"""core functionality of pytest-workflow plugin"""

# Disable pylint here because of false positive
from distutils.dir_util import copy_tree  # pylint: disable=E0611,E0401

import pytest

import yaml

from .content_tests import ContentTestCollector
from .file_tests import FileTestCollector
from .schema import WorkflowTest, workflow_tests_from_schema
from .workflow import Workflow


def pytest_collect_file(path, parent):
    """Collection hook
    This collects the yaml files that start with "test" and end with
    .yaml or .yml"""
    if path.ext in [".yml", ".yaml"] and path.basename.startswith("test"):
        return YamlFile(path, parent)
    return None


class YamlFile(pytest.File):
    """
    This class collects YAML files and turns them into test items.
    """

    def __init__(self, path: str, parent: pytest.Collector):
        # This super statement is important for pytest reasons. It should
        # be in any collector!
        super().__init__(path, parent=parent)

    def collect(self):
        """This function collects all the workflow tests from a single
        YAML file."""
        with self.fspath.open() as yaml_file:
            schema = yaml.safe_load(yaml_file)

        return [WorkflowTestsCollector(test, self)
                for test in workflow_tests_from_schema(schema)]


class WorkflowTestsCollector(pytest.Collector):
    """This class starts all the tests collectors per workflow"""

    def __init__(self, workflow_test: WorkflowTest, parent: pytest.Collector):
        self.workflow_test = workflow_test
        super().__init__(workflow_test.name, parent=parent)

    def collect(self):
        """This runs the workflow and starts all the associated tests
        The idea is that isolated parts of the yaml get their own collector or
        item."""

        # Create a temporary directory where the workflow is run.
        # This will prevent the project repository from getting filled up with
        # test workflow output.
        # The temporary directory is produced from self.config._tmpdirhandler
        # which  does the same as using a `tmpdir` fixture.
        tempdir = str(
            self.config._tmpdirhandler.mktemp(  # noqa # pylint: disable=protected-access
                self.name, numbered=False)
        )
        # Copy the project directory to the temporary directory using pytest's
        # rootdir.
        copy_tree(str(self.config.rootdir), tempdir)

        # Create a workflow and make sure it runs in the tempdir
        workflow = Workflow(self.workflow_test.command, tempdir)
        name = self.workflow_test.name
        # Use print statements here. Using pytests internal logwriter has no
        # added value. If there are wishes to do so in the future, the pytest
        # terminal writer can be acquired with:
        # self.config.pluginmanager.get_plugin("terminalreporter")
        # Name is included explicitly in each print command to avoid confusion
        # between workflows
        print("run '{name}' with command '{command}' in '{dir}'".format(
            name=name,
            command=self.workflow_test.command,
            dir=tempdir))
        workflow.run()
        print("run '{name}': done".format(name=name))
        log_err = workflow.stderr_to_file()
        log_out = workflow.stdout_to_file()
        print("'{0}' stdout saved in: {1}".format(name, str(log_out)))
        print("'{0}' stderr saved in: {1}".format(name, str(log_err)))

        # Below structure makes it easy to append tests
        tests = []

        tests += [FileTestCollector(self, filetest, tempdir) for filetest in
                  self.workflow_test.files]

        tests += [ExitCodeTest(self, workflow.exit_code,
                               self.workflow_test.exit_code)]

        tests += [ContentTestCollector(
            name="stdout", parent=self,
            content=workflow.stdout.decode().splitlines(),
            content_test=self.workflow_test.stdout)]

        tests += [ContentTestCollector(
            name="stderr", parent=self,
            content=workflow.stderr.decode().splitlines(),
            content_test=self.workflow_test.stderr)]

        return tests
        # TODO: Figure out proper cleanup.
        # If tempdir is removed here, all tests will fail.
        # After yielding the tests this object is no longer needed, so
        # deleting the tempdir here does not work.
        # There is probably some fixture that can handle this.


class ExitCodeTest(pytest.Item):
    def __init__(self, parent: pytest.Collector, exit_code: int,
                 desired_exit_code: int):
        name = "exit code should be {0}".format(desired_exit_code)
        super().__init__(name, parent=parent)
        self.exit_code = exit_code
        self.desired_exit_code = desired_exit_code

    def runtest(self):
        assert self.exit_code == self.desired_exit_code

    def repr_failure(self, excinfo):
        # pylint: disable=unused-argument
        # excinfo needed for pytest.
        message = ("The workflow exited with exit code " +
                   "'{0}' instead of '{1}'.".format(self.exit_code,
                                                    self.desired_exit_code))
        return message
