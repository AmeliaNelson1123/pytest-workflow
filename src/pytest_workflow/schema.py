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

"""Schema for the YAML files used by pytest-workflow"""

import json
from pathlib import Path

import jsonschema

SCHEMA = Path(__file__).parent / Path("schema") / Path("schema.json")
with SCHEMA.open() as schema:
    JSON_SCHEMA = json.load(schema)


def validate_schema(instance: dict):
    """
    Validates the pytest-workflow schema
    :param instance: a dictionary that is validated against the schema
    :return: This function rasises a ValidationError
    when the schema is not correct.
    """
    jsonschema.validate(instance, JSON_SCHEMA)
