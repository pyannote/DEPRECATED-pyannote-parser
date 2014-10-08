#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014 CNRS (Hervé BREDIN - http://herve.niderb.fr)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import unicode_literals

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

import os
import sys
from pkg_resources import iter_entry_points

__all__ = []

parser_plugins = {}

for o in iter_entry_points(group='pyannote.parser.plugin', name=None):

    parser_name = o.name
    parser_class = o.load()

    for extension in parser_class.file_extensions():

        if extension in parser_plugins:

            raise ValueError('conflict')

        parser_plugins[extension] = parser_class

    setattr(sys.modules[__name__], parser_name, parser_class)
    __all__.append(parser_name)


class MagicParser(object):

    def __init__(self, **kwargs):
        super(MagicParser, self).__init__()
        self.init_kwargs = kwargs

    def read(self, path, **kwargs):

        _, ext = os.path.splitext(path)
        ext = ext[1:]  # .mdtm ==> mdtm

        try:
            parser_class = parser_plugins[ext]
        except:
            raise NotImplementedError('unknown extension {0}'.format(ext))

        parser = parser_class(**self.init_kwargs)
        parser.read(path, **kwargs)

        return parser


__all__.append(MagicParser)
