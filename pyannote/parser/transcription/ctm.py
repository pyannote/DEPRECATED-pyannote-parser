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
# Antoine LAURENT - http://antoine-laurent.fr


from __future__ import unicode_literals

import codecs
import gzip
import re

from pyannote.core import T, TStart, TEnd, Transcription
from pyannote.parser.base import Parser


class IterLinesMixin:

    def _is_gzip(self, path2file):
        return path2file[-3:] == '.gz'

    def iterlines(self, path2file, encoding='utf8'):

        if self._is_gzip(path2file):
            return self.gzip_iterlines(path2file, encoding=encoding)

        return self.default_iterlines(path2file, encoding=encoding)

    def default_iterlines(self, path2txt, encoding='utf-8'):
        with open(path2txt, 'rt') as t:
            for line in t:
                yield line

    def gzip_iterlines(self, path2gzip, encoding='utf-8'):
        with gzip.open(path2gzip) as z:
            reader = codecs.getreader(encoding)
            for line in reader(z):
                yield line


class CTMParser(Parser, IterLinesMixin):
    """
    Parameters
    ----------
    punctuation : bool, optional
        When False
    """

    @classmethod
    def file_extensions(cls):
        return ['ctm']

    def __init__(self, punctuation=True):
        super(CTMParser, self).__init__()
        self.punctuation = punctuation

    def read(self, path, **kwargs):

        T.reset()
        transcription = Transcription()

        previousNode = TStart

        arc = []

        for line in self.iterlines(path, encoding='utf-8'):

            # skip comments
            if re.search(r'^;;', line):
                continue

            fields = line.strip().split()

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            word = fields[4]

            # remove punctuations
            if not self.punctuation:
                word = re.sub(r'[\.!,;?":]+', ' ', word)
                word = re.sub(r' +', ' ', word)

            word = word.strip()
            if not word:
                continue

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            confidence = float(fields[5])

            start_time = round(float(fields[2]), 3)
            duration = round(float(fields[3]), 3)
            end_time = float(start_time)+float(duration)
            end_time = round(end_time, 3)

            if duration == 0:
                node_start = previousNode
                node_end = T()

                if len(arc) == 2:

                    transcription.remove_edge(arc[0], arc[1])
                    transcription.add_edge(arc[0], node_end, **arc_data)
                    node_inter = T()
                    transcription.add_edge(node_end, node_inter, speech=word, confidence=confidence)
                    transcription.add_edge(node_inter, arc[1])
                    arc.append(node_end)
                    arc.append(node_inter)
                    node_end=arc[1]

                elif len(arc) > 2:
                    node_anc_start = arc[0]
                    node_anc_end = arc[1]
                    transcription.remove_edge(arc[len(arc)-1], node_anc_end)
                    transcription.add_edge(arc[len(arc)-1], node_end, speech=word, confidence=confidence)
                    transcription.add_edge(node_end, node_anc_end)
                    arc.append(node_end)
                    node_end=arc[1]

            else:
                addEdge = True
                node_start = T(start_time)
                node_end = T(end_time)
                if previousNode.drifting:
                    if not transcription.has_edge(previousNode, node_start):
                        transcription.add_edge(previousNode, node_start)
                else:
                    if node_start < previousNode:
                        node_start = previousNode
                    elif node_start > previousNode:
                        transcription.add_edge(previousNode, node_start)
                if node_start.anchored and node_end.anchored:
                    if node_start == node_end:
                        addEdge = False
                        node_start = previousNode
                        node_end = T()
                        if len(arc) == 2:
                            transcription.remove_edge(arc[0], arc[1])
                            transcription.add_edge(arc[0], node_end, **arc_data)
                            node_inter = T()
                            transcription.add_edge(node_end, node_inter,
                                                   speech=word,
                                                   confidence=confidence)
                            transcription.add_edge(node_inter, arc[1])
                            arc.append(node_end)
                            arc.append(node_inter)
                            node_end = arc[1]
                        elif len(arc) > 2:
                            node_anc_start = arc[0]
                            node_anc_end = arc[1]
                            transcription.remove_edge(arc[len(arc) - 1],
                                                      node_anc_end)
                            transcription.add_edge(arc[len(arc) - 1], node_end, speech=word, confidence=confidence)
                            transcription.add_edge(node_end, node_anc_end)
                            arc.append(node_end)
                            node_end = arc[1]
                    else:
                        arc = [node_start, node_end]
                        arc_data = {'speech': word, 'confidence': confidence}
                if addEdge:
                    transcription.add_edge(node_start, node_end,
                                           speech=word, confidence=confidence)
            previousNode = node_end

        transcription.add_edge(previousNode, TEnd)

        self._loaded = transcription

        return self

    def empty(self, uri=None, modality=None, **kwargs):
        return Transcription(uri=uri, modality=modality)

    def __call__(self, **kwargs):
        return self._loaded
