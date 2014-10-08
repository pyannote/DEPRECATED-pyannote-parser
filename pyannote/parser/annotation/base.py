from abc import ABCMeta, abstractmethod
from pyannote.parser.base import Parser

from pyannote.core import Annotation
from pyannote.core import PYANNOTE_URI, PYANNOTE_MODALITY, \
    PYANNOTE_SEGMENT, PYANNOTE_TRACK, PYANNOTE_LABEL

import pandas


class AnnotationParser(Parser):

    @abstractmethod
    def fields(self):
        pass

    @abstractmethod
    def get_segment(self, row):
        pass

    def converters(self):
        return None

    def comment(self):
        return None

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

        # load whole file
        df = pandas.read_table(path,
                               delim_whitespace=True,
                               header=None, names=self.fields(),
                               comment=self.comment(),
                               converters=self.converters(),
                               dtype={PYANNOTE_LABEL: object})

        # remove comment lines
        # (i.e. lines for which all fields are either None or NaN)
        keep = [not all([pandas.isnull(r[n]) for n in self.fields()]) for _, r in df.iterrows()]
        df = df[keep]

        # add unique track numbers if they are not read from file
        if PYANNOTE_TRACK not in self.fields():
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
                raise ValueError('missing modality -- use modality=')
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

    def write(self, annotation, f=None, uri=None, modality=None):
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

    def _append(self, annotation, f, uri, modality):
        raise NotImplementedError('')


