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

# THE SOFTWARE S PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import unicode_literals

import sys
import pandas
import numpy as np
from pyannote.core import Segment, Timeline, Annotation, Scores
from pyannote.core.feature import SlidingWindowFeature
from pyannote.core import PYANNOTE_URI, PYANNOTE_MODALITY, \
    PYANNOTE_SEGMENT, PYANNOTE_TRACK, PYANNOTE_LABEL, PYANNOTE_SCORE


class BaseTimelineParser(object):
    def __init__(self):
        super(BaseTimelineParser, self).__init__()

        # (uri, modality) ==> timeline
        self.reset()

    def __get_uris(self):
        return sorted(self._loaded)
    uris = property(fget=__get_uris)
    """"""

    def _add(self, segment, uri):
        if uri not in self._loaded:
            self._loaded[uri] = Timeline(uri=uri)
        self._loaded[uri].add(segment)

    def reset(self):
        self._loaded = {}

    def read(self, path, uri=None, **kwargs):
        raise NotImplementedError('')

    def __call__(self, uri=None, **kwargs):
        """

        Parameters
        ----------
        uri : str, optional
            If None and there is more than one resource

        Returns
        -------
        timeline : :class:`pyannote.base.timeline.Timeline`

        """

        match = dict(self._loaded)

        # filter out all timelines
        # but the ones for the requested resource
        if uri is not None:
            match = {v: timeline for v, timeline in match.iteritems()
                     if v == uri}

        if len(match) == 0:
            # empty annotation
            return Timeline(uri=uri)
        elif len(match) == 1:
            return match.values()[0]
        else:
            raise ValueError('')


class BaseTextualTimelineParser(BaseTimelineParser):

    def _comment(self, line):
        raise NotImplementedError('')

    def _parse(self, line):
        raise NotImplementedError('')

    def read(self, path, uri=None, **kwargs):

        # defaults PYANNOTE_URI to path
        if uri is None:
            uri = path

        # open file and loop on each line
        fp = open(path, 'r')
        for line in fp:

            # strip line
            line = line.strip()

            # comment ?
            if self._comment(line):
                continue

            # parse current line
            s, v = self._parse(line)

            # found resource ?
            if v is None:
                v = uri

            # add segment
            self._add(s, v)

        fp.close()

        return self

    def write(self, timeline, f=sys.stdout, uri=None):
        """

        Parameters
        ----------
        timeline : :class:`pyannote.base.timeline.Timeline`
            Timeline
        f : file or str, optional
            Default is stdout.
        uri : str, optional
            When provided, overrides `timeline` uri attribute.
        """

        if uri is None:
            uri = timeline.uri

        if isinstance(f, file):
            self._append(timeline, f, uri)
        else:
            f = open(f, 'w')
            self._append(timeline, f, uri)
            f.close()


class BaseAnnotationParser(object):

    def __init__(self):
        super(BaseAnnotationParser, self).__init__()
        self.reset()

    def __get_uris(self):
        return sorted(set([v for (v, m) in self._loaded]))
    uris = property(fget=__get_uris)
    """"""

    def __get_modalities(self):
        return sorted(set([m for (v, m) in self._loaded]))
    modalities = property(fget=__get_modalities)
    """"""

    def _add(self, segment, track, label, uri, modality):
        key = (uri, modality)
        if key not in self._loaded:
            self._loaded[key] = Annotation(uri=uri, modality=modality)
        if track is None:
            track = self._loaded[key].new_track(segment)
        self._loaded[key][segment, track] = label

    def reset(self):
        self._loaded = {}

    def read(self, path, uri=None, modality=None, **kwargs):
        raise NotImplementedError('')

    def __call__(self, uri=None, modality=None, **kwargs):
        """

        Parameters
        ----------
        uri : str, optional
            If None and there is more than one resource
        modality : str, optional

        Returns
        -------
        annotation : :class:`pyannote.base.annotation.Annotation`

        """

        match = dict(self._loaded)

        # filter out all annotations
        # but the ones for the requested resource
        if uri is not None:
            match = {(v, m): ann for (v, m), ann in match.iteritems()
                     if v == uri}

        # filter out all remaining annotations
        # but the ones for the requested modality
        if modality is not None:
            match = {(v, m): ann for (v, m), ann in match.iteritems()
                     if m == modality}

        if len(match) == 0:
            A = Annotation(uri=uri, modality=modality)

        elif len(match) == 1:
            A = match.values()[0]

        else:
            msg = 'Found more than one matching annotation: %s'
            raise ValueError(msg % match.keys())

        return A


class BaseTextualFormat(object):

    def get_comment(self):
        return None

    def get_fields(self):
        raise NotImplementedError('')

    def get_segment(self, row):
        raise NotImplementedError('')

    def get_converters(self):
        return None

    def get_default_modality(self):
        return None


class BaseTextualParser(object):

    def __init__(self):
        super(BaseTextualParser, self).__init__()

    def __get_uris(self):
        return sorted(set([v for (v, m) in self._loaded]))
    uris = property(fget=__get_uris)
    """"""

    def __get_modalities(self):
        return sorted(set([m for (v, m) in self._loaded]))
    modalities = property(fget=__get_modalities)
    """"""

    def no_match(self, uri=None, modality=None):
        raise NotImplementedError('')

    def __call__(self, uri=None, modality=None, **kwargs):
        """

        Parameters
        ----------
        uri : str, optional
            If None and there is more than one resource
        modality : str, optional

        Returns
        -------
        annotation : :class:`Annotation` or :class:`Scores`

        """

        match = dict(self._loaded)

        # filter out all annotations
        # but the ones for the requested resource
        if uri is not None:
            match = {(v, m): ann for (v, m), ann in match.iteritems()
                     if v == uri}

        # filter out all remaining annotations
        # but the ones for the requested modality
        if modality is not None:
            match = {(v, m): ann for (v, m), ann in match.iteritems()
                     if m == modality}

        if len(match) == 0:
            A = self.no_match(uri=uri, modality=modality)

        elif len(match) == 1:
            A = match.values()[0]

        else:
            msg = 'Found more than one matching annotation: %s'
            raise ValueError(msg % match.keys())

        return A

    def comment(self, text, f=sys.stdout):
        """Add comment to a file

        Comment marker is automatically added in front of the text

        Parameters
        ----------
        text : str
            Actual comment
        f : file or str, optional
            Default is stdout.

        """
        comment_marker = self.get_comment()
        if comment_marker is None:
            raise NotImplementedError('Comments are not supported.')

        if isinstance(f, file):
            f.write('%s %s\n' % (comment_marker, text))
            f.flush()
        else:
            with open(f, 'w') as g:
                g.write('%s %s\n' % (comment_marker, text))

    def write(self, annotation, f=sys.stdout, uri=None, modality=None):
        """

        Parameters
        ----------
        annotation : `Annotation` or `Score`
            Annotation
        f : file or str, optional
            Default is stdout.
        uri, modality : str, optional
            Override `annotation` attributes

        """

        if uri is None:
            uri = annotation.uri
        if modality is None:
            modality = annotation.modality

        if isinstance(f, file):
            self._append(annotation, f, uri, modality)
            f.flush()
        else:
            with open(f, 'w') as g:
                self._append(annotation, g, uri, modality)


class BaseTextualAnnotationParser(BaseTextualParser):

    def read(self, path, uri=None, modality=None, **kwargs):
        """

        Parameters
        ----------
        path : str

        modality : str, optional
            Force all entries to be considered as coming from this modality.
            Only taken into account when file format does not provide
            any field related to modality (e.g. .seg files)

        """

        names = self.get_fields()
        converters = self.get_converters()

        # load whole file
        df = pandas.read_table(path,
                               delim_whitespace=True,
                               header=None, names=names,
                               comment=self.get_comment(),
                               converters=converters,
                               dtype={PYANNOTE_LABEL: object})

        # remove comment lines
        # (i.e. lines for which all fields are either None or NaN)
        keep = [not all([pandas.isnull(r[n]) for n in names]) for _, r in df.iterrows()]
        df = df[keep]

        # add unique track numbers if they are not read from file
        if PYANNOTE_TRACK not in names:
            df[PYANNOTE_TRACK] = range(df.shape[0])

        # add 'segment' column build from start time & duration
        df[PYANNOTE_SEGMENT] = [self.get_segment(row)
                                for r, row in df.iterrows()]

        # add uri column in case it does not exist
        if PYANNOTE_URI not in df:
            if uri is None:
                raise ValueError('missing uri -- use uri=')
            df[PYANNOTE_URI] = uri

        # obtain list of resources
        uris = list(df[PYANNOTE_URI].unique())

        # add modality column in case it does not exist
        if PYANNOTE_MODALITY not in df:
            if modality is None:
                modality = self.get_default_modality()
            df[PYANNOTE_MODALITY] = modality if modality is not None else ""

        # obtain list of modalities
        modalities = list(df[PYANNOTE_MODALITY].unique())

        self._loaded = {}

        # loop on resources
        for uri in uris:

            # filter based on resource
            df_ = df[df[PYANNOTE_URI] == uri]

            # loop on modalities
            for modality in modalities:

                # filter based on modality
                modality = modality if modality is not None else ""
                df__ = df_[df_[PYANNOTE_MODALITY] == modality]
                a = Annotation.from_df(df__, modality=modality, uri=uri)
                self._loaded[uri, modality] = a

        return self

    def no_match(self, uri=None, modality=None):
        return Annotation(uri=uri, modality=modality)


class CustomTextualAnnotationParser(BaseTextualAnnotationParser):
    def __init__(self, num_fields, uri=None, modality=None,
                 label=None, track=None,
                 start=None, end=None, duration=None,
                 comment=None):
        super(CustomTextualAnnotationParser, self).__init__()

        self.num_fields = num_fields
        self.fields = {}

        if isinstance(uri, int):
            self.fields[uri] = PYANNOTE_URI

        if isinstance(modality, int):
            self.fields[modality] = PYANNOTE_MODALITY

        if isinstance(track, int):
            self.fields[track] = PYANNOTE_TRACK

        if isinstance(label, int):
            self.fields[label] = PYANNOTE_LABEL

        if isinstance(start, int):
            self.fields[start] = 'start'

        if isinstance(end, int):
            self.fields[end] = 'end'

        if isinstance(duration, int):
            self.fields[duration] = 'duration'

        self.start = start
        self.end = end
        self.duration = duration

        self.comment = comment

    def get_converters(self):
        return None

    def get_default_modality(self):
        return None

    def get_comment(self):
        return self.comment

    def get_fields(self):
        return [self.fields[i] if i in self.fields else i
                for i in range(self.num_fields)]

    def get_segment(self, row):
        if self.end is not None:
            return Segment(row['start'], row['end'])
        elif self.duration is not None:
            return Segment(row['start'], row['start'] + row['duration'])
        else:
            raise ValueError('do not know how to build a segment')


class BaseTextualScoresParser(BaseTextualParser):

    def read(self, path, modality=None, **kwargs):

        names = self.get_fields()

        converters = self.get_converters()
        if converters is None:
            converters = {}
        if PYANNOTE_LABEL not in converters:
            converters[PYANNOTE_LABEL] = lambda x: x
        if PYANNOTE_TRACK not in converters:
            converters[PYANNOTE_TRACK] = lambda x: x

        # load whole file
        df = pandas.read_table(path,
                               delim_whitespace=True,
                               header=None, names=names,
                               comment=self.get_comment(),
                               converters=converters)

        # remove comment lines
        # (i.e. lines for which all fields are either None or NaN)
        keep = [not all([pandas.isnull(r[n]) for n in names]) for _, r in df.iterrows()]
        df = df[keep]

        # add 'segment' column build from start time & duration
        df[PYANNOTE_SEGMENT] = [self.get_segment(row) for r, row in df.iterrows()]

        # add unique track number per segment if they are not read from file
        if PYANNOTE_TRACK not in names:
            s2t = {s: t for t, s in enumerate(df[PYANNOTE_SEGMENT].unique())}
            df[PYANNOTE_TRACK] = [s2t[s] for s in df[PYANNOTE_SEGMENT]]

        # add modality column in case it does not exist
        if PYANNOTE_MODALITY not in df:
            if modality is None:
                modality = self.get_default_modality()
            df[PYANNOTE_MODALITY] = modality if modality is not None else ""

        # remove all columns but those six
        df = df[[PYANNOTE_URI, PYANNOTE_MODALITY, PYANNOTE_SEGMENT, PYANNOTE_TRACK, PYANNOTE_LABEL, PYANNOTE_SCORE]]

        # obtain list of resources
        uris = list(df[PYANNOTE_URI].unique())

        # obtain list of modalities
        modalities = list(df[PYANNOTE_MODALITY].unique())

        self._loaded = {}

        # loop on resources
        for uri in uris:

            # filter based on resource
            df_ = df[df[PYANNOTE_URI] == uri]

            # loop on modalities
            for modality in modalities:

                # filter based on modality
                df__ = df_[df_[PYANNOTE_MODALITY] == (modality if modality is not None else "")]

                s = Scores.from_df(df__, modality=modality, uri=uri)

                self._loaded[uri, modality] = s

        return self

    def no_match(self, uri=None, modality=None):
        return Scores(uri=uri, modality=modality)


class BasePeriodicFeatureParser(object):

    def __init__(self):
        super(BasePeriodicFeatureParser, self).__init__()

    def _read_header(self, fp):
        """
        Read the header of a binary file.

        Parameters
        ----------
        fp : file

        Returns
        -------
        dtype :
            Feature vector type
        sliding_window : :class:`pyannote.base.segment.SlidingWindow`

        count :
            Number of feature vectors

        """
        raise NotImplementedError('')

    def _read_data(self, fp, dtype, count=-1):
        """
        Construct an array from data in a binary file.

        Parameters
        ----------
        file : file
            Open file object
        dtype : data-type
            Data type of the returned array.
            Used to determine the size and byte-order of the items in the file.
        count : int
            Number of items to read. ``-1`` means all items (i.e., the complete
            file).

        Returns
        -------

        """
        raise NotImplementedError('')

    def read(self, path, uri=None, **kwargs):
        """

        Parameters
        ----------
        path : str
            path to binary feature file
        uri : str, optional

        Returns
        -------
        feature : :class:`pyannote.base.feature.SlidingWindowFeature`


        """

        # open binary file
        fp = open(path, 'rb')
        # read header
        dtype, sliding_window, count = self._read_header(fp)
        # read data
        data = self._read_data(fp, dtype, count=count)

        # if `uri` is not provided, use `path` instead
        if uri is None:
            uri = str(path)

        # create feature object
        feature = SlidingWindowFeature(data, sliding_window)

        # close binary file
        fp.close()

        return feature


class BaseBinaryPeriodicFeatureParser(BasePeriodicFeatureParser):

    """
    Base class for periodic feature stored in binary format.
    """

    def __init__(self):
        super(BaseBinaryPeriodicFeatureParser, self).__init__()

    def _read_data(self, fp, dtype, count=-1):
        """
        Construct an array from data in a binary file.

        Parameters
        ----------
        file : file
            Open file object
        dtype : data-type
            Data type of the returned array.
            Used to determine the size and byte-order of the items in the file.
        count : int
            Number of items to read. ``-1`` means all items (i.e., the complete
            file).

        Returns
        -------

        """
        return np.fromfile(fp, dtype=dtype, sep='', count=count)


class BaseTextualPeriodicFeatureParser(BasePeriodicFeatureParser):

    def __init__(self):
        super(BaseTextualPeriodicFeatureParser, self).__init__()

    def _read_data(self, fp, dtype, count=-1):
        raise NotImplementedError('')

if __name__ == "__main__":
    import doctest
    doctest.testmod()
