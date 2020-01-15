#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014-2015 CNRS

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

from __future__ import print_function

import pytest
from pyannote.core import Segment
from pyannote.parser import REPEREParser
import tempfile
import os

SAMPLE_ANNOTATION = """uri1 1.0 3.5 speech alice
uri1 3.0 7.5 speech barbara
uri1 6.0 9.0 speech chris
"""

@pytest.fixture
def sample_annotation(request):

    _, filename = tempfile.mkstemp()
    with open(filename, 'w') as f:
        f.write(SAMPLE_ANNOTATION)

    def delete():
        os.remove(filename)
    request.addfinalizer(delete)

    return filename


def test_load_annotation(sample_annotation):
    parser = REPEREParser()
    annotations = parser.read(sample_annotation)
    speech1 = annotations(uri="uri1", modality="speech")
    assert list(speech1.itertracks(label=True)) == [
        (Segment(1, 3.5), 0, 'alice'),
        (Segment(3, 7.5), 1, 'barbara'),
        (Segment(6, 9), 2, 'chris')]
