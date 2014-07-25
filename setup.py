# -*- coding: utf-8 -*-

import os

from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'fhnw.office2plone'

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst')
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    read('CONTRIBUTORS.txt'))

setup(
    name=name,
    version='0.1.dev0',
    description='Upload MS-Office documents to Plone',
    long_description = long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Framework :: Plone :: 4.3",
    ],
    author='FHNW',
    author_email='weboffice@fhnw.ch',
    url="http://websvn.fhnw.ch/eggs/" + name,
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    keywords="FHNW Plone",
    test_suite = "fhnw.office2plone.tests",
    install_requires=[
        'setuptools',
        'atreal.massloader',
    ],
    extras_require={
        'test': [
            'plone.app.testing[robot]',
            'flake8',
        ],
        'development': [
            'zest.releaser',
            'check-manifest',
            'i18ndude',
        ],
    },
    entry_points="""
     # -*- Entry points: -*-
       [z3c.autoinclude.plugin]
       target = plone
    """,
    include_package_data=True,
    zip_safe=False,
)
