import color
import yaml

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

try:
    import pybtex.database.input.bibtex
    import pybtex.database.input.bibtexml
    import pybtex.database.input.bibyaml
    import pybtex.database.output.bibtex
    import pybtex.database.output.bibtexml
    import pybtex.database.output.bibyaml

except ImportError:
    print(color.dye('error', color.error) +
          ": you need to install Pybtex; try running 'pip install "
          "pybtex' or 'easy_install pybtex'")
    exit(-1)


class EnDecoder(object):
    """ Encode and decode content.

        Design choices:
        * Has no interaction with disk.
        * Incoming content is not trusted.
        * Returned content must be correctly formatted (no one else checks).
        * Failures raise ValueError
        * encode_bibdata will try to recognize exceptions
    """

    decode_fmt = {'bibyaml' : pybtex.database.input.bibyaml,
                  'bibtex'  : pybtex.database.input.bibtex,
                  'bib'     : pybtex.database.input.bibtex,
                  'bibtexml': pybtex.database.input.bibtexml}

    encode_fmt = {'bibyaml' : pybtex.database.output.bibyaml,
                  'bibtex'  : pybtex.database.output.bibtex,
                  'bib'     : pybtex.database.output.bibtex,
                  'bibtexml': pybtex.database.output.bibtexml}

    def encode_metadata(self, metadata):
        return yaml.safe_dump(metadata, allow_unicode=True, encoding='UTF-8', indent = 4)
        
    def decode_metadata(self, metadata_raw):
        return yaml.safe_load(metadata_raw)
    
    def encode_bibdata(self, bibdata, fmt='bibyaml'):
        """Encode bibdata """
        s = StringIO.StringIO()
        EnDecoder.encode_fmt[fmt].Writer().write_stream(bibdata, s)
        return s.getvalue()

    def decode_bibdata(self, bibdata_raw):
        """"""
        bibdata_rawutf8 = bibdata_raw
#        bibdata_rawutf8 = unicode(bibdata_raw, 'utf8') # FIXME this doesn't work
        for fmt in EnDecoder.decode_fmt.values():
            try:
                bibdata_stream = StringIO.StringIO(bibdata_rawutf8)
                return self._decode_bibdata(bibdata_stream, fmt.Parser())
            except ValueError:
                pass
        raise ValueError('could not parse bibdata')

    def _decode_bibdata(self, bibdata_stream, parser):
        try:
            entry = parser.parse_stream(bibdata_stream)
            if len(entry.entries) > 0:
                return entry
        except Exception:
            pass        
        raise ValueError('could not parse bibdata')
