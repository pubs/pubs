#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.7.0'

setup(
    name         = 'pubs',
    version      = VERSION,
    author       = 'Fabien Benureau, Olivier Mangin, Jonathan Grizou',
    author_email = 'fabien.benureau@gmail.com',
    maintainer   = 'Olivier Mangin',
    url          = 'https://github.com/pubs/pubs',

    description  = 'command-line scientific bibliography manager',
    packages     = ['pubs', 'pubs.config',
                            'pubs.commands',
                            'pubs.templates',
                            'pubs.plugs', 'pubs.plugs.alias'],
    scripts      = ['pubs/pubs'],

    install_requires = ['pyyaml', 'bibtexparser', 'python-dateutil', 'requests',
                        'configobj',
                        'beautifulsoup4'], # to be made optional?
    tests_require = ['pyfakefs>=2.7'],
    extra_require = {'autocompletion': ['argcomplete'],
                     },

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
    ],

    # in order to avoid 'zipimport.ZipImportError: bad local file header'
    zip_safe=False,

)
