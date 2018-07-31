#!/usr/bin/env python

from setuptools import setup


setup(
    name='eve-arango',
    version='0.1.0',
    description='Eve ArangoDB data layer',
    long_description=open('README.rst').read(),
    author='Eirik Krogstad',
    author_email='eirikkr@gmail.com',
    url='https://github.com/tangram/eve-arango',
    license='MIT',
    packages=['eve_arango'],
    include_package_data=True,
    install_requires=['Eve', 'python-arango'],
    tests_require=['pylint', 'pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
