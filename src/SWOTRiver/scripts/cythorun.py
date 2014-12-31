#!/usr/bin/env python

"""
Compile a Python script into an executable that embeds CPython and run it.
Requires CPython to be built as a shared library ('libpythonX.Y').
Basic usage:
    python cythonrun somefile.py [ARGS]
"""

from Cython.Build.BuildExecutable import build, build_and_run

if __name__ == '__main__':
    import sys
    build_and_run(sys.argv[1:])
