__version__ = '1.4.0'
import os
from glob import glob

from setuptools import setup, find_packages, Extension

# README read-in
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
# END README read-in


def get_resources(file_exts):
    directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'skytemple_files', '_resources')
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(file_ext) for file_ext in file_exts):
                paths.append(os.path.join('_resources', os.path.relpath(os.path.join('..', path, filename), directory)))
    return paths


sf2_cute = Extension('skytemple_dse.sf2._sf2cute',
    include_dirs=['swig/src/include'],
    sources=list(glob('swig/src/src/sf2cute/*.cpp')) + ['swig/sf2cute_wrap.cxx'],
    language='c++',
    extra_compile_args=['-fPIC', '-std=c++14'],
)


ppmdu_adpcm = Extension('skytemple_dse._ppmdu_adpcm',
    sources=list(glob('swig/src_ppmdu_adpcm/*.cpp')) + ['swig/ppmdu_adpcm_wrap.cxx'],
    language='c++',
    extra_compile_args=['-fPIC', '-std=c++20'],
)


setup(
    name='skytemple-dse',
    version=__version__,
    packages=find_packages(),
    package_data={'skytemple_dse': get_resources(['.csv'])},
    description='Python library for working with a specific version of compiled DSE sound engine files',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/SkyTemple/skytemple-dse/',
    install_requires=[
        'mido >= 1.2.10',
        'sf2utils >= 0.9.0'
    ],
    ext_modules=[
        sf2_cute, ppmdu_adpcm
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
    ],
)
