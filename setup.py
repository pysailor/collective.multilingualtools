# -*- coding: utf-8 -*-
"""
This module contains the collective.multilingualtools package
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('README.rst')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs/CHANGES.rst')
    + '\n' +
    read('docs/CONTRIBUTORS.rst')
    + '\n')

install_requires = [
        'setuptools',
        'plone.app.multilingual',
    ]


setup(name='collective.multilingualtools',
    version=version,
    description="A set of tools that simplify handling multilingual "\
    "content in Plone using plone.app.multilingual.",
    long_description=long_description,
    classifiers=[
    "Framework :: Plone",
    "Framework :: Plone :: 4.0",
    "Framework :: Plone :: 4.1",
    "Framework :: Plone :: 4.2",
    "Framework :: Plone :: 4.3",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "License :: OSI Approved :: European Union Public Licence "\
        "1.1 (EUPL 1.1)",
    ],
    keywords='linguatools internationalization pam',
    author='Syslab.com GmbH',
    author_email='thomas@syslab.com',
    url='',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=dict(test=['plone.app.testing']),
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )
