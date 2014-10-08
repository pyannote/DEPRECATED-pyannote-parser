from pyannote.core import Segment
from pyannote.core import PYANNOTE_URI, PYANNOTE_MODALITY, PYANNOTE_LABEL

from base import AnnotationParser


class MDTMParser(AnnotationParser):

    @classmethod
    def file_extensions(cls):
        return ['mdtm']

    def fields(self):
        return [PYANNOTE_URI,
                'channel',
                'start',
                'duration',
                PYANNOTE_MODALITY,
                'confidence',
                'gender',
                PYANNOTE_LABEL]

    def comment(self):
        return ';'

    def get_segment(self, row):
        return Segment(row['start'], row['start'] + row['duration'])

    def _append(self, annotation, f, uri, modality):

        try:
            format = '%s 1 %%g %%g %s NA %%s %%s\n' % (uri, modality)
            for segment, track, label in annotation.itertracks(label=True):
                f.write(format % (segment.start, segment.duration,
                                  track, label))
        except Exception, e:
            print "Error @ %s%s %s %s" % (uri, segment, track, label)
            raise e
