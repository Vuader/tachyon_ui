import os
import sys
from setuptools import find_packages

config = {
        "name": "tachyon-ui",
        "author": "Christiaan F Rademan, Dave Kruger",
        "author_email": "tachyon@fwiw.co.za",
        "description": "Tachyon - UI Framework",
        "license": "BSD 3-Clause",
        "keywords": "tachyon ui interface portal",
        "url": "https://github.com/vision1983/tachyon_ui",
        "packages": find_packages(),
        "namespace_packages": [
            'tachyon'
            ],
        "classifiers": [
            "Topic :: Software Development :: Libraries :: Application Frameworks",
            "Environment :: Other Environment",
            "Intended Audience :: Information Technology",
            "Intended Audience :: System Administrators",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7"
            ]
        }

