#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'girder>=3.0.0a1'
]

setup(
    author="Patrick Avery",
    author_email='patrick.avery@kitware.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    description='Endpoints for STEM operations.',
    install_requires=requirements,
    license='Apache Software License 2.0',
    long_description=readme,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='girder-plugin, stem',
    name='stemserver_plugin',
    packages=find_packages(exclude=['test', 'test.*']),
    url='https://github.com/openchemistry/stemserver',
    version='0.1.0',
    zip_safe=False,
    entry_points={
        'girder.plugin': [
            'stem = stemserver_plugin:StemPlugin'
        ]
    }
)
