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
from pyannote.parser import CTMParser
import numpy as np
import tempfile
import os

SAMPLE = """uri1 1 1.410 0.220 So 0.990 lex
uri1 1 1.630 0.040 if 0.100 lex
uri1 1 1.670 0.070 a 0.100 lex
uri1 1 1.830 0.420 photon 0.990 lex
uri1 1 2.250 0.120 is 0.990 lex
uri1 1 2.370 0.370 directed 0.990 lex
uri1 1 2.770 0.120 through 0.990 lex
uri1 1 2.890 0.060 a 0.990 lex
uri1 1 2.950 0.350 plane 0.990 lex
"""


@pytest.fixture
def sample(request):

    _, filename = tempfile.mkstemp()
    with open(filename, 'w') as f:
        f.write(SAMPLE)

    def delete():
        os.remove(filename)
    request.addfinalizer(delete)

    return filename


def test_load(sample):
    parser = CTMParser()
    transcription = parser.read(sample)
    speech1 = transcription(uri="uri1")
    assert list(speech1.ordered_edges_iter(data=True)) == [
        (-np.inf, 1.410, {}),
        (1.410, 1.630, {'speech': 'So', 'confidence': 0.990}),
        (1.630, 1.670, {'speech': 'if', 'confidence': 0.100}),
        (1.670, 1.740, {'speech': 'a', 'confidence': 0.100}),
        (1.740, 1.830, {}),
        (1.830, 2.250, {'speech': 'photon', 'confidence': 0.990}),
        (2.250, 2.370, {'speech': 'is', 'confidence': 0.990}),
        (2.370, 2.740, {'speech': 'directed', 'confidence': 0.990}),
        (2.740, 2.770, {}),
        (2.770, 2.890, {'speech': 'through', 'confidence': 0.990}),
        (2.890, 2.950, {'speech': 'a', 'confidence': 0.990}),
        (2.950, 3.300, {'speech': 'plane', 'confidence': 0.990}),
        (3.300, np.inf, {})
    ]
