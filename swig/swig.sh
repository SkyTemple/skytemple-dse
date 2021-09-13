#!/bin/sh
mv sf2cute_headers sf2cute
swig -python -c++ -features autodoc=3 sf2cute.i
mv sf2cute sf2cute_headers
mv sf2cute.py ../skytemple_dse/sf2/
