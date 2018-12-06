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

import pytest
import yaml

from .schema import validate_schema


class YamlFile(pytest.File):
    def collect(self):
        yaml_content = yaml.load(self.fspath.open())
        validate_schema(yaml_content)
        yield WorkflowItem(yaml_content.get("name"),self, yaml_content)

class WorkflowItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super(WorkflowItem, self).__init__(name, parent)
