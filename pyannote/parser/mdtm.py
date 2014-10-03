#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2012-2014 CNRS (Hervé BREDIN - http://herve.niderb.fr)

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

from __future__ import unicode_literals

"""
Support for MDTM file format

MDTM (Meta Data Time-Mark) is a file format used to specify label
for time regions within a recorded waveform.
"""

from pyannote.core import Segment, \
    PYANNOTE_URI, PYANNOTE_MODALITY, PYANNOTE_LABEL
from base import BaseTextualFormat, BaseTextualAnnotationParser


class MDTMMixin(BaseTextualFormat):

    CHANNEL = 'channel'
    START = 'start'
    DURATION = 'duration'
    CONFIDENCE = 'confidence'
    GENDER = 'gender'

    def get_comment(self):
        return ';'

    def get_fields(self):
        return [PYANNOTE_URI,
                self.CHANNEL,
                self.START,
                self.DURATION,
                PYANNOTE_MODALITY,
                self.CONFIDENCE,
                self.GENDER,
                PYANNOTE_LABEL]

    def get_segment(self, row):
        return Segment(row[self.START], row[self.START] + row[self.DURATION])

    def _append(self, annotation, f, uri, modality):

        try:
            format = '%s 1 %%g %%g %s NA %%s %%s\n' % (uri, modality)
            for segment, track, label in annotation.itertracks(label=True):
                f.write(format % (segment.start, segment.duration,
                                  track, label))
        except Exception, e:
            print "Error @ %s%s %s %s" % (uri, segment, track, label)
            raise e


class MDTMParser(BaseTextualAnnotationParser, MDTMMixin):
    pass
