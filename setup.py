#!/usr/bin/env python3
# MIT License
# Copyright (c) 2025 Ahrii Kim.
# You may not use this file except in compliance with the License.

"""
A setuptools based setup module.

"""

import os
import re
from io import open
from setuptools import find_packages, setup

ROOT = os.path.dirname(__file__)

def get_version():
    """
    Reads the version from Rubric-MQM's __init__.py file.
    """
    VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')
    init = open(os.path.join(ROOT, 'rubric_mqm', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


def get_long_description():
    with open('README.md') as f:
        long_description = f.read()

    with open('CHANGELOG.md') as f:
        release_notes = f.read()

    # Plug release notes into the long description
    long_description = long_description.replace(
        '# Release Notes\n\nPlease see [CHANGELOG.md](CHANGELOG.md) for release logs.',
        release_notes)

    return long_description


setup(
    name="rubric_mqm",
    version=get_version(),
    author="Ahrii Kim",
    author_email="ahriikim@gmail.com",
    description="Rubric-based MQM score",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    keywords='llm metric machine translation',
    license='MIT',
    url="https://github.com/trotacodigos/Rubric-MQM",
    packages=find_packages(exclude=["*.tests", "*.tests.*",
                                    "tests.*", "tests"]),
    install_requires=['openai>1.0',
                      'numpy',
                      'packaging>=20.9',
                      'pandas>=1.0',
                      'tenacity',
                      'python-dotenv'
                      ],
    entry_points={
        'console_scripts': [
            "rubric_mqm=rubric_mqm.worker:main"
        ]
    },
    include_package_data=True,
    python_requires='>=3.8',
    tests_require=['pytest'],
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

)