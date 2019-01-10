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
import queue
import shlex
import subprocess  # nosec: security implications have been considered
import threading
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
        self.lock = threading.Lock()

    def start(self):
        """Runs the workflow in a subprocess in the background.
        To make sure the workflow is finished use the `.wait()` method"""
        sub_procces_args = shlex.split(self.command)
        self._popen = subprocess.Popen(  # nosec: Shell is not enabled.
            sub_procces_args, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=str(self.cwd))

    def run(self):
        """Runs the workflow and blocks until it is finished"""
        self.start()
        self.wait()

    def stdout_to_file(self) -> Path:
        self.wait()
        return bytes_to_file(self.stdout, self.cwd / Path("log.out"))

    def stderr_to_file(self) -> Path:
        self.wait()
        return bytes_to_file(self.stdout, self.cwd / Path("log.err"))

    def wait(self):
        """Waits for the workflow to complete"""
        # Lock the wait step. Only one waiter is allowed here to wait for
        # the workflow to complete and write the stderr.
        # A popen.stderr is a buffered reader and can only be read once.
        # Once self._stderr and self._stdout are written the lock can be
        # released
        self.lock.acquire()
        self._popen.wait()
        if self._stderr is None:
            self._stderr = self._popen.stderr.read()
        if self._stdout is None:
            self._stdout = self._popen.stdout.read()
        self.lock.release()

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


class WorkflowQueue(queue.Queue):
    """A Queue object that will keep running 'n' numbers of workflows
    simultaneously until the queue is empty."""
    def __init__(self):
        # No argument for maxsize. This queue is infinite.
        super().__init__()

    def put(self, item, block=True, timeout=None):
        """Like Queue.put() but tests if item is a Workflow"""
        if isinstance(item, Workflow):
            super().put(item, block, timeout)
        else:
            raise ValueError("Only Workflow type objects can be submitted to "
                             "this queue.")

    # Queue processing with workers example taken from
    # https://docs.python.org/3.5/library/queue.html?highlight=queue#queue.Queue.join  # noqa
    def process(self, number_of_threads: int = 1):
        """
        Processes the workflow queue with a number of threads
        :param number_of_threads: The number of threads
        """
        threads = [threading.Thread(target=self.worker)
                   for _ in range(number_of_threads)]
        for thread in threads:
            thread.start()
        self.join()
        for thread in threads:
            thread.join()

    def worker(self):
        """Run workflows until the queue is empty"""
        while True:
            try:
                workflow = self.get_nowait()
            except queue.Empty:
                break
            # Some reporting
            print("run command: '{0}' in '{1}'".format(
                workflow.command, workflow.cwd))
            workflow.run()
            self.task_done()
