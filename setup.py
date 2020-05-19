#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2020 by Jussi Vatjus-Anttila
:license: MIT, see LICENSE for more details.
"""
from setuptools import setup


setup(
    name="pytest-opentmi",
    use_scm_version=True,
    description="pytest plugin for publish results to opentmi",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author="Jussi Vatjus-Anttila",
    author_email="jussiva@gmail.com",
    url="https://github.com/opentmi/pytest-opentmi",
    packages=["pytest_opentmi"],
    # package_data={"pytest_opentmi": ["resources/*"]},
    # entry_points={"pytest11": ["html = pytest_opentmi.plugin"]},
    setup_requires=["setuptools_scm"],
    install_requires=["pytest>=5.0", "pytest-metadata", "opentmi-client>=0.7.0", "joblib"],
    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install .[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        'dev': ['coverage', 'coveralls', 'mock', 'pylint', 'nose', 'pyinstaller']
    },
    license="Mozilla Public License 2.0 (MPL 2.0)",
    keywords="py.test pytest opentmi report",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
