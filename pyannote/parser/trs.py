#!/usr/bin/env python
# encoding: utf-8

# Copyright 2012 Herve BREDIN (bredin@limsi.fr)

# This file is part of PyAnnote.
#
#     PyAnnote is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     PyAnnote is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with PyAnnote.  If not, see <http://www.gnu.org/licenses/>.

"""
Support for TRS file format

TRS (TRanScriber) is a file format used by TranScriber audio annotation tool.

References
----------
http://transag.sourceforge.net/
"""

import re

try:
    from lxml import objectify
except:
    pass

from pyannote.core import Segment
from base import BaseAnnotationParser


class TRSParser(BaseAnnotationParser):

    def __init__(self):
        super(TRSParser, self).__init__()

    def _complete(self):
        for segment in self._incomplete:
            segment.end = self._sync
        self._incomplete = []

    def _parse_speakers(self, turn):
        string = turn.get('speaker')
        if string:
            return string.strip().split()
        else:
            return []

    def _parse_spoken(self, element):
        string = element.tail
        if not string:
            return []

        labels = []
        p = re.compile('.*?<pers=(.*?)>.*?</pers>', re.DOTALL)
        m = p.match(string)
        while(m):
            # split Jean-Marie_LEPEN,Marine_LEPEN ("les LEPEN")
            for label in m.group(1).split(','):
                try:
                    labels.append(str(label))
                except Exception, e:
                    print "label = %s" % label
                    raise e
            string = string[m.end():]
            m = p.match(string)
        return labels

    def read(self, path, uri=None, **kwargs):

        # objectify xml file and get root
        root = objectify.parse(path).getroot()

        # if uri is not provided, infer (part of) it from .trs file
        if uri is None:
            uri = root.get('audio_filename')

        # speaker names and genders
        name = {}
        gender = {}
        for speaker in root.Speakers.iterchildren():
            name[speaker.get('id')] = speaker.get('name')
            gender[speaker.get('id')] = speaker.get('type')

        # # incomplete segments
        # # ie without an actual end time
        # self._incomplete = []

        # speech turn number
        track = 0

        for section in root.Episode.iterchildren():

            # transcription status (report or nontrans)
            section_start = float(section.get('startTime'))
            section_end = float(section.get('endTime'))
            section_segment = Segment(start=section_start, end=section_end)
            label = section.get('type')
            self._add(section_segment, None, label, uri, 'status')

            # # sync
            # self._sync = section_start
            # self._complete()

            for turn in section.iterchildren():

                # get speech turn start/end time
                turn_start = float(turn.get('startTime'))
                turn_end = float(turn.get('endTime'))
                turn_segment = Segment(start=turn_start, end=turn_end)

                labels = self._parse_speakers(turn)
                for label in labels:
                    self._add(turn_segment, track, name[label], uri, 'speaker')
                    track = track + 1

                # self._sync = turn_start
                # self._complete()

                # for element in turn.iterchildren():

                #     if element.tag == 'Sync':
                #         self._sync = float(element.get('time'))
                #         self._complete()

                #     element_segment = Segment(
                #         start=self._sync,
                #         end=self._sync+2*SEGMENT_PRECISION)
                #     self._incomplete.append(element_segment)
                #     labels = self._parse_spoken(element)
                #     for label in labels:
                #         self._add(element_segment, None, label, uri, 'spoken')

                # self._sync = turn_end
                # self._complete()

            # self._sync = section_end
            # self._complete()

        return self

if __name__ == "__main__":
    import doctest
    doctest.testmod()
