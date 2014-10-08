import os
import sys
from pkg_resources import iter_entry_points

__all__ = []

# file_extension --> plugin_class
annotation_parsers = {}

for o in iter_entry_points(group='pyannote.parser.annotation', name=None):

    parser_name = o.name
    parser_class = o.load()

    for extension in parser_class.file_extensions():

        if extension in annotation_parsers:

            raise ValueError('conflict')

        annotation_parsers[extension] = parser_class

    setattr(sys.modules[__name__], parser_name, parser_class)
    __all__.append(parser_name)


class MagicAnnotationParser(object):

    def __init__(self, **kwargs):
        super(MagicAnnotationParser, self).__init__()
        self.init_kwargs = kwargs

    def load(self, path, **kwargs):

        _, ext = os.path.splitext(path)
        ext = ext[1:]  # .mdtm ==> mdtm

        try:
            parser_class = annotation_parsers[ext]
        except:
            raise NotImplementedError('unknown extension {0}'.format(ext))

        parser = parser_class(**self.init_kwargs)
        parser.load(path, **kwargs)

        return parser


__all__.append(MagicAnnotationParser)
