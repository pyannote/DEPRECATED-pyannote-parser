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

import itertools
import six
import six.moves
from pyannote.parser import LSTParser
from pyannote.parser import MagicParser


class CoParser(object):
    """Utility class to uri-iterate over several file in sync.

    Parameters
    ----------
    uris : list or str, optional
        If `list`, `uris` provides list of uris to iterate over.
        If `str` and


    Example
    -------
    >>> coParser = CoParser(uris='/path/to/uris.lst',
    ...                     reference='/path/to/reference.mdtm',
    ...                     features = '/path/to/features/{uri}.pkl')
    >>> for uri, ref in coParser.iter('uris', 'reference'):
    ...     pass

    """

    def _make_load(self, value, key=None, uris=None):

        parser = MagicParser.guess_parser(value)

        # mono-uri file
        if '{uri' in value:

            def loadOne(uri):
                path = value.format(uri=uri)
                return parser().read(path)(uri=uri)

            return loadOne

        # multi-uris file
        else:

            # load the whole file
            path = value
            p = parser().read(path)

            # update list of uris when conditions are met
            # (i.e. multi-uris file + specific request)
            if uris == key:
                self.uris = list(p.uris)

            return lambda uri: p(uri=uri)

    def __init__(self, uris=None, **kwargs):

        super(CoParser, self).__init__()

        self.uris = None
        self.loadFunc = {}

        # go over all **kwarg
        for key, value in six.iteritems(kwargs):
            self.loadFunc[key] = self._make_load(value, key=key, uris=uris)

        # if uris is None, use 'uris' kwargs with no {uri} in it
        if uris is None:
            if self.uris is None:
                raise ValueError('where are my uris?')

        # if uris is a list, use it
        elif isinstance(uris, list):
            self.uris = list(uris)

        # if uris is a string, 2 options:
        # option 2: it does match any of the provided kwargs
        # indicating that it should be considered as the path
        # to a file itself containing a list of uris.
        elif isinstance(uris, str) and uris not in kwargs:

            try:
                path = uris
                self.uris = LSTParser().read(path)

            except Exception:
                msg = 'cannot load uris from file {path}'
                raise ValueError(msg.format(path=path))

    def generators(self, *args):

        G = []
        for key in args:
            if key == 'uris':
                g = iter(self.uris)
            elif key in self.loadFunc:
                g = six.moves.map(self.loadFunc[key], self.uris)
            else:
                g = itertools.repeat(None)

            G.append(g)

        return G

    def iter(self, *args):
        for _ in six.moves.zip(*self.generators(*args)):
            yield _
