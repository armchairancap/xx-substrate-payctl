#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup

NAME = 'payctl'
DESCRIPTION = 'Simple command line application to control the payouts of xx Network validators.'
URL = 'https://github.com/armchairancap/xx-substrate-payctl'
EMAIL = 'armchairancap@users.noreply.github.com'
AUTHOR = 'AA'
REQUIRES_PYTHON = '>=3.9.0'
VERSION = None
LICENSE = 'MIT License'
REQUIRED = [
    'substrate-interface>=1.6.4'
]

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['payctl'],
    entry_points={
        'console_scripts': ['payctl=payctl:main'],
    },
    data_files=[('etc/payctl', ['default.conf'])],
    install_requires=REQUIRED,
    license=LICENSE,
    project_urls={ 
        'Bug Reports': 'https://github.com/armchairancap/xx-substrate-payctl/issues',
        'Source': 'https://github.com/armchairancap/xx-substrate-payctl',
    },
)
