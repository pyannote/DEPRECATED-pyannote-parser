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

from __future__ import unicode_literals


import warnings
import six.moves
import pysrt
import numpy as np
from pyannote.core import Transcription, T, TStart, TEnd

from pyannote.parser.base import Parser


class SRTParser(Parser):
    """
    SRT (SubRip Text) is a subtitles file format

    References
    ----------
    http://en.wikipedia.org/wiki/SubRip

    Parameters
    ----------
    split : bool, optional
        Try to detect and split multiple speaker subtitles. Defaults to False.
    duration : bool, optional
        Estimate duration of multiple lines based on string length.
        Defaults to False.
    """

    @classmethod
    def file_extensions(cls):
        return ['srt']

    def __init__(self, split=False, duration=False):
        super(SRTParser, self).__init__()
        self.split = split
        self.duration = duration

    def _timeInSeconds(self, t):
        h = t.hours
        m = t.minutes
        s = t.seconds
        u = t.milliseconds
        return 3600. * h + 60. * m + s + 1e-3 * u

    def _split(self, raw):
        """Return list of dialogue lines"""

        # split multiple speaker subtitles
        # "-hello!\n-hi!"  >>> ["-hello!", "hi!"]
        # "how do you do?" >>> ["how do you do?"]
        if self.split:
            lines = raw.split('\n-')

        # don't...
        # "-hello!\n-hi!"  >>> ["-hello!\n-hi!"]
        # "how do you do?" >>> ["how do you do?"]
        else:
            lines = [raw]

        # merge same speaker lines
        # "[do you think\nI'm dumb?"] >>> ["do you think I'm dumb?"]
        lines = [' '.join(line.split('\n')) for line in lines]

        return lines

    def _duration(self, lines, start, end):
        """Iterate dialogue lines + (estimated) timeranges"""

        if self.duration:
            length = np.array([len(line)+1 for line in lines])
            ratio = 1. * np.cumsum(length) / np.sum(length)
            end_times = start + (end - start) * ratio
        else:
            end_times = [T() for line in lines[:-1]] + [end]

        start_time = start
        for line, end_time in six.moves.zip(lines, end_times):
            yield line, start_time, end_time
            start_time = end_time

    def read(self, path, uri=None, **kwargs):
        """Load .srt file as transcription

        Parameters
        ----------
        path : str
            Path to .srt file

        Returns
        -------
        subtitle : Transcription
        """

        # load .srt file using pysrt
        subtitles = pysrt.open(path)

        # initial empty transcription
        transcription = Transcription(uri=uri)

        # keep track of end of previous subtitle
        prev_end = TStart

        # loop on each subtitle in chronological order
        for subtitle in subtitles:

            # convert start/end time into seconds
            start = self._timeInSeconds(subtitle.start)
            end = self._timeInSeconds(subtitle.end)

            # connect current subtitle with previous one
            # if there is a gap between them
            if start > prev_end:
                transcription.add_edge(prev_end, start)
            # warning in case current subtitle starts
            # before previous subtitle ends
            elif start < prev_end:
                warnings.warn('Non-chronological subtitles')

            # split subtitle in multiple speaker lines (only if needed)
            lines = self._split(subtitle.text)

            # loop on subtitle lines
            for line, start_t, end_t in self._duration(lines, start, end):
                transcription.add_edge(start_t, end_t, subtitle=line)

            prev_end = end

        transcription.add_edge(end, TEnd)

        self._loaded = {(uri, 'subtitle'): transcription}

        return self

    def empty(self, uri=None, modality=None, **kwargs):
        return Transcription(uri=uri, modality='subtitle')
