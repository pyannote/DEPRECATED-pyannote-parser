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
from pyannote.parser import JSONParser
import tempfile
import os

SAMPLE = '''{
  "pyannote": "Annotation",
  "content": [
    {
      "segment": {
        "start": 1,
        "end": 3.5
      },
      "track": "track1",
      "label": "alice"
    },
    {
      "segment": {
        "start": 3,
        "end": 7.5
      },
      "track": "track2",
      "label": "barbara"
    },
    {
      "segment": {
        "start": 6,
        "end": 9
      },
      "track": "track3",
      "label": "chris"
    }
  ],
  "uri": "uri1",
  "modality": "speech"
}'''


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
    parser = JSONParser()
    annotations = parser.read(sample)
    speech1 = annotations(uri="uri1", modality="speech")
    assert list(speech1.itertracks(label=True)) == [
        (Segment(1, 3.5), 'track1', 'alice'),
        (Segment(3, 7.5), 'track2', 'barbara'),
        (Segment(6, 9), 'track3', 'chris') ]
