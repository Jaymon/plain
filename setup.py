#!/usr/bin/env python
# http://docs.python.org/distutils/setupscript.html
# http://docs.python.org/2/distutils/examples.html

from setuptools import setup, find_packages
import re
import os
from codecs import open


name = "plain"
with open(os.path.join(name, "__init__.py", encoding="utf-8")) as f:
    version = re.search(r"^__version__\s*=\s*[\'\"]([^\'\"]+)", f.read(), flags=re.I | re.M).group(1)

long_description = ""
if os.path.isfile('README.rst'):
    with open('README.rst', encoding='utf-8') as f:
        long_description = f.read()


setup(
    name=name,
    version=version,
    description='Makes shiny things plain so they are easy to digest programmatically',
    long_description=long_description,
    author='Jay Marcyes',
    author_email='jay@marcyes.com',
    url='http://github.com/jaymon/{}'.format(name),
    packages=find_packages(),
    license='GPLv2+',
    install_requires=["captain", "beautifulsoup4", "requests"],
    tests_require=['testdata'],
    classifiers=[ # https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
        'Topic :: Text Processing :: Markup :: HTML',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
#     entry_points = {
#         'console_scripts': [
#             '{} = {}.__main__:console'.format(name, name),
#         ],
#     },
)
