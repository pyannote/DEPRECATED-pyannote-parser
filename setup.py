#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014-2017 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr

import versioneer
versioneer.versionfile_source = 'pyannote/parser/_version.py'
versioneer.versionfile_build = versioneer.versionfile_source
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'pyannote-parser-'

from setuptools import setup, find_packages

setup(

    # package
    namespace_packages=['pyannote'],
    packages=find_packages(),
    install_requires=[
        'pyannote.core >= 0.12.1',
        'pysrt >= 1.0.1',
        'six >= 1.10.0'
    ],
    # versioneer
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

    # PyPI
    name='pyannote.parser',
    description=('PyAnnote parsers'),
    author='Hervé Bredin',
    author_email='bredin@limsi.fr',
    url='http://herve.niderb.fr/',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Scientific/Engineering"
    ],
    entry_points="""
        [pyannote.parser.plugin]
        LSTParser=pyannote.parser.generic.lst:LSTParser
        JSONParser=pyannote.parser.generic.json:JSONParser
        PKLParser=pyannote.parser.generic.pkl:PKLParser
        MDTMParser=pyannote.parser.annotation.mdtm:MDTMParser
        SEGParser=pyannote.parser.annotation.seg:SEGParser
        REPEREParser=pyannote.parser.annotation.repere:REPEREParser
        REPEREScoresParser=pyannote.parser.scores.repere:REPEREScoresParser
        UEMParser=pyannote.parser.timeline.uem:UEMParser
        SRTParser=pyannote.parser.transcription.srt:SRTParser
        CTMParser=pyannote.parser.transcription.ctm:CTMParser
    """
)
