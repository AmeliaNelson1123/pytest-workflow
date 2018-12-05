#!/usr/bin/env/python3

from setuptools import setup


with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="pytest-workflow",
    version="0.1.0dev",
    description="A pytest plugin for configuring workflow/pipeline tests using YAML files",
    author="Leiden University Medical Center, various departments",
    author_email="sasc@lumc.nl",  # A placeholder for now
    long_description=long_description,
    license="AGPL-3.0",
    keywords=["pytest", "workflow", "pipeline", "yaml"],
    zip_safe=False,
    packages=["src/pytest-workflow"],
    url="https://github.com/LUMC/pytest-workflow",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Framework :: Pytest",
    ],
)
