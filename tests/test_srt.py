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
from pyannote.parser import SRTParser
import numpy as np
import tempfile
import os

SAMPLE = """1
00:00:01,240 --> 00:00:03,834
If a photon is directed through a plane
with two slits in it...



2
00:00:04,000 --> 00:00:05,149
...and either is observed...



3
00:00:05,319 --> 00:00:07,549
...it will not go through both.
If unobserved. it will.
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
    parser = SRTParser()
    transcriptions = parser.read(sample)
    subtitles = transcriptions()
    assert list(subtitles.ordered_edges_iter(data=True)) == [
        (-np.inf, 1.240, {}),
        (1.240, 3.834, {'subtitle': 'If a photon is directed through a plane with two slits in it...'}),
        (3.834, 4.000, {}, ),
        (4.000, 5.149, {'subtitle': '...and either is observed...'}),
        (5.149, 5.319, {}),
        (5.319, 7.549, {'subtitle': '...it will not go through both. If unobserved. it will.'}),
        (7.549, np.inf, {})
    ]
