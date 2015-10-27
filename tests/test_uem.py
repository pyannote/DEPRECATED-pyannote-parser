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
from pyannote.parser import UEMParser
import tempfile
import os

SAMPLE = """uri1 1 1.0 3.5
uri1 1 3.0 7.5
uri1 1 6.0 9.0
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
    parser = UEMParser()
    timelines = parser.read(sample)
    timeline1 = timelines(uri="uri1")
    assert list(timeline1) == [Segment(1, 3.5),
                               Segment(3, 7.5),
                               Segment(6, 9)]
