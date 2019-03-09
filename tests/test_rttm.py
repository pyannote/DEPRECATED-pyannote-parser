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
# Neville Ryant  --  nryant@gmail.com
from __future__ import print_function
import os
import tempfile

import pytest
from pyannote.core import Segment
from pyannote.parser import RTTMParser


SAMPLE = """SPKR-INFO fn1 1 <NA> <NA> <NA> adult_male jon <NA>
            SPKR-INFO fn1 1 <NA> <NA> <NA> adult_male bill <NA>
            SPKR-INFO fn1 1 <NA> <NA> <NA> adult_male carl <NA>
            SPEAKER fn1 1 235.50 0.60 <NA> <NA> jon <NA>
            SPEAKER fn1 1 237.0 1.7 <NA> <NA> bill <NA> <NA>
            SPEAKER fn1 1 240.0 2.8 <NA> <NA> bill <NA>
         """


@pytest.fixture
def sample(request):
    _, fn = tempfile.mkstemp()
    with open(fn, 'wb') as f:
        f.write(SAMPLE.encode('utf-8'))
    def delete():
        os.remove(fn)
    request.addfinalizer(delete)
    return fn


def test_load(sample):
    parser = RTTMParser()
    annotations = parser.read(sample)
    speech1 = annotations(uri='fn1', modality='SPEAKER')
    assert list(speech1.itertracks(label=True)) == [
        (Segment(235.5, 236.1), 3, 'jon'),
        (Segment(237, 238.7), 4, 'bill'),
        (Segment(240, 242.8), 5, 'bill')]
