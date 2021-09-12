__version__ = '1.4.0'
import os

from setuptools import setup, find_packages

# README read-in
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
# END README read-in


setup(
    name='skytemple-dse',
    version=__version__,
    packages=find_packages(),
    description='Python library for working with a specific version of compiled DSE sound engine files',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/SkyTemple/skytemple-dse/',
    install_requires=[
        'mido >= 1.2.10'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
)
