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

from typing import List

import pytest
import yaml

from .schema import validate_schema
from .workflow import Workflow


def pytest_collect_file(path, parent):
    """Collection hook
    This collects the yaml files where the tests are defined."""
    if path.ext == ".yml":
        return YamlFile(path, parent)


class YamlFile(pytest.File):
    """This class collects YAML files and turns them into test items."""

    def collect(self):
        yaml_content = yaml.load(self.fspath.open())
        validate_schema(yaml_content)
        yield WorkflowItem(yaml_content.get("name"), self, yaml_content)


class WorkflowItem(pytest.Item):
    """This class defines a pytest item. That has methods for running tests."""

    def __init__(self, name, parent, yaml_content):
        validate_schema(yaml_content)
        self.yaml_content = yaml_content

        super(WorkflowItem, self).__init__(name, parent)

    def runtest(self):
        pass

    def repr_failure(self, excinfo):
        pass

    def reportinfo(self):
        return self.fspath, 0, "usecase: {0}".format(self.name)


def pytest_addoption(parser):
    """This adds extra options to the pytest executable"""
    parser.addoption(
        "--workflow-executable",
        dest="workflow_executable",
        help="The executable used to run the workflow."
    )


@pytest.fixture(scope="module")  # scope=module so that it only executes once.
def workflow_run(args: List[str], request):
    workflow = Workflow(executable=request.config.getoption("executable"), arguments=args)
    workflow.run()
    yield workflow
    # everything after 'yield' in a pytest fixture
    #  is performed after test completion.
    workflow.cleanup()
