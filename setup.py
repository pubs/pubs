#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name         = 'pubs',
    version      = '0.5.0',
    author       = 'Fabien Benureau, Olivier Mangin, Jonathan Grizou',
    author_email = 'fabien.benureau+inria@gmail.com',
    maintainer   = 'Olivier Mangin',
    url          = '',

    description  = 'command-line scientific bibliography manager',
    requires     = ['pyyaml', 'bibtexparser', 'dateutil'],
    packages     = find_packages(),
    scripts      = ['pubs/pubs'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
    ]
)
