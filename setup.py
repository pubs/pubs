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
    #packages     = find_packages(), #['pubs', 'pubs.commands', 'pubs.templates', 'pubs.plugs'],
    packages     = ['pubs', 'pubs.commands', 'pubs.templates', 'pubs.plugs'],
    scripts      = ['pubs/pubs'],

    install_requires = ['pyyaml', 'bibtexparser', 'python-dateutil', 'requests'],

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
