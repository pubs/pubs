#!/usr/bin/env python
import os
import unittest

from setuptools import setup


with open('pubs/version.py') as f:
    exec(f.read())  # defines __version__

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'readme.md'), 'r') as fd:
    long_description = fd.read()


def pubs_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


setup(
    name='pubs',
    version=__version__,
    author='Fabien Benureau, Olivier Mangin, Jonathan Grizou',
    author_email='fabien.benureau@gmail.com',
    maintainer='Olivier Mangin',
    url='https://github.com/pubs/pubs',

    description='command-line scientific bibliography manager',
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=['pubs',
              'pubs.config',
              'pubs.commands',
              'pubs.templates',
              'pubs.plugs',
              'pubs.plugs.alias',
              'pubs.plugs.git'],
    entry_points={
        'console_scripts': [
            'pubs=pubs.pubs_cmd:execute',
            ],
        },

    include_package_data=True,

    install_requires=['pyyaml', 'bibtexparser>=1.0', 'python-dateutil', 'six',
                      'requests', 'configobj', 'beautifulsoup4', 'feedparser'],
    extras_require={'autocompletion': ['argcomplete'],
                    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
    ],

    test_suite='tests',
    tests_require=['pyfakefs>=3.4', 'mock', 'ddt', 'certifi'],

    # in order to avoid 'zipimport.ZipImportError: bad local file header'
    zip_safe=False,

)
