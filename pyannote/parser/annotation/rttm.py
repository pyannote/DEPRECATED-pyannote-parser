# encoding: utf-8
"""Parser for Rich Transcription Time Marked (RTTM) files. """

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
# Neville Ryant  --  nryant@gmail.com
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from functools import wraps

import numpy as np
import six

from pyannote.core import Segment
from pyannote.core import PYANNOTE_URI, PYANNOTE_MODALITY, PYANNOTE_LABEL
from .base import AnnotationParser


def _convert_float(x):
    return np.float64(x) if x != '<NA>' else np.nan


# TODO: DOCSTRING.
class RTTMParser(AnnotationParser):
    """Parser for Rich Transcription Time Marked (RTTM) file format.

    RTTM is a format introduced for the NIST Rich Transcription evaluations (see
    Appendix A of RT-09 evaluation plan for more details) that for storing diarization
    and speech-to-text (STT) output. Primarily, though, it is used to store diarization
    with one speaker turn per line, each line consisting of 10 space-delimited fields:

    - Type – segment type; expected to be ``SPEAKER`` for diarization; rows
      with types other than ``SPEAKER`` will be ignored
    - File ID – file name; basename of the recording minus extension (e.g.,
      ``rec1 a``)
    - Channel ID – channel (1-indexed) that turn is on
    - Turn Onset – onset of turn in seconds from beginning of recording
    - Turn Duration – duration of turn in seconds
    - Orthography Field – orthography rendering of object; irrelelvant for diarization
      and should be ``<NA>``
    - Speaker Type – speaker type; expected to be ``<NA>``
    - Speaker Name – name of speaker of turn
    - Confidence Score – system confidence (probability) that information is
      correct; expected to be ``<NA>``
    - Signal Lookahead Time – signal lookahead time; expected to be ``<NA>``

    For instance:

        SPEAKER CMU 20020319-1400 d01 NONE 1 130.430000 2.350 <NA> <NA> juliet <NA> <NA>
        SPEAKER CMU 20020319-1400 d01 NONE 1 157.610000 3.060 <NA> <NA> tbc <NA> <NA>
        SPEAKER CMU 20020319-1400 d01 NONE 1 130.490000 0.450 <NA> <NA> chek <NA> <NA>


    References
    ----------
    NIST. (2009). The 2009 (RT-09) Rich Transcription Meeting Recognition
    Evaluation Plan. https://web.archive.org/web/20100606041157if_/http://www.itl.nist.gov/iad/mig/tests/rt/2009/docs/rt09-meeting-eval-plan-v2.pdf
    """
    @classmethod
    def file_extensions(cls):
        return ['rttm']

    def fields(self):
        return [PYANNOTE_MODALITY,
                PYANNOTE_URI,
                'channel',
                'start',
                'duration',
                'ortho',
                'subtype',
                PYANNOTE_LABEL,
                'confidence',
                'slat',
               ]

    def comment(self):
        return ';'

    def converters(self):
        return dict(start=_convert_float, duration=_convert_float)

    @wraps(AnnotationParser.read)
    def read(self, path, uri=None, modality=None, **kwargs):
        super(RTTMParser, self).read(path, uri, modality, **kwargs)

        # Eliminate any modality other than SPEAKER as they are irrelevant for
        # scoring segmentations.
        loaded = {}
        for (uri, modality), ann in six.iteritems(self._loaded):
            if modality != 'SPEAKER':
                continue
            loaded[(uri, modality)] = ann
        self._loaded = loaded

        return self

    def get_segment(self, row):
        return Segment(row[4], row[4] + row[5])

    def _append(self, annotation, f, uri, modality):
        try:
            format = ('%s %s 1 %%g %%g <NA> <NA> %%s <NA> <NA>\n' %
                      (modality, uri))
            for segment, track, label in annotation.itertracks(label=True):
                f.write(format % (segment.start, segment.duration, label))
        except Exception as e:
            print("Error @ %s%s %s %s" % (uri, segment, track, label))
            raise e
