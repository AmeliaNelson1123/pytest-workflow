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

"""
Contains all functionality regarding the running of workflows and reporting
on stdout, stderr and exit code.
This file was created by A.H.B. Bollen
"""

import shlex
import subprocess  # nosec: security implications have been considered
from pathlib import Path


class Workflow(object):

    def __init__(self, command: str, cwd: Path = Path()):
        """
        Initiates a workflow object
        :param command: The string that represents the command to be run
        :param cwd: The current working directory in which the command will
        be executed.
        """

        self.command = command
        self._popen = None
        self._stderr = None
        self._stdout = None
        self.cwd = cwd

    def run(self):
        sub_procces_args = shlex.split(self.command)
        self._popen = subprocess.Popen(  # nosec: Shell is not enabled.
            sub_procces_args, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=str(self.cwd))

    def stdout_to_file(self) -> Path:
        self.wait()
        return bytes_to_file(self.stdout, self.cwd / Path("log.out"))

    def stderr_to_file(self) -> Path:
        self.wait()
        return bytes_to_file(self.stdout, self.cwd / Path("log.err"))

    def wait(self):
        self._popen.wait()
        if self._stderr is None:
            self._stderr = self._popen.stderr.read()
        if self._stdout is None:
            self._stdout = self._popen.stdout.read()

    @property
    def stdout(self) -> bytes:
        return self._stdout  # for testing log

    @property
    def stderr(self) -> bytes:
        return self._stderr  # for testing log

    @property
    def exit_code(self) -> int:
        self.wait()
        return self._popen.returncode

    def stdout_lines(self):
        self.wait()
        return self._stdout.decode().splitlines()

    def stderr_lines(self):
        self.wait()
        return self._stderr.decode().splitlines()


def bytes_to_file(bytestring: bytes, output_file: Path) -> Path:
    with output_file.open('wb') as file_handler:
        file_handler.write(bytestring)
    return output_file
