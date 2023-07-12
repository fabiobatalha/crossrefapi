#!/usr/bin/env python
from setuptools import setup, find_packages

from crossref import VERSION

install_requires = [
    'requests>=2.31.0',
    'urllib3==1.26.16',
]

tests_require = []

setup(
    name="crossrefapi",
    version=VERSION,
    description="Library that implements the endpoints of the Crossref API",
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    maintainer="Fabio Batalha",
    maintainer_email="fabiobatalha@gmail.com",
    url="http://github.com/fabiobatalha/crossrefapi",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    dependency_links=[],
    tests_require=tests_require,
    test_suite='tests',
    install_requires=install_requires
)
