from __future__ import unicode_literals

import sys
import os
import shutil

from .p3 import urlparse, HTTPConnection, urlopen


"""Conventions:
    - all files are written using utf8 encoding by default,
    - any function returning or variable containing byte data should
      be prefixed by 'byte_'
"""


class UnableToDecodeTextFile(Exception):

    _msg = "unknown encoding (maybe not a text file) for: {}"

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self._msg.format(self.path)


# files i/o

def _check_system_path_exists(path, fail=True):
    answer = os.path.exists(path)
    if not answer and fail:
        raise IOError('File does not exist: {}'.format(path))
    else:
        return answer


def _check_system_path_is(nature, path, fail=True):
    check_fun = getattr(os.path, nature)
    answer = check_fun(path)
    if not answer and fail:
        raise IOError('{} is not a {}.'.format(path, nature))
    else:
        return answer


def system_path(path):
    return os.path.abspath(os.path.expanduser(path))


def _open(path, mode):
    if 'b' in mode or sys.version_info < (3,):
        return open(system_path(path), mode)
    else:
        return open(system_path(path), mode, encoding='utf-8')


def check_file(path, fail=True):
    syspath = system_path(path)
    return (_check_system_path_exists(syspath, fail=fail) and
            _check_system_path_is('isfile', syspath, fail=fail))


def check_directory(path, fail=True):
    syspath = system_path(path)
    return (_check_system_path_exists(syspath, fail=fail) and
            _check_system_path_is('isdir', syspath, fail=fail))


def read_text_file(filepath, fail=True):
    check_file(filepath, fail=fail)
    try:
        with _open(filepath, 'r') as f:
            content = f.read()
            try:  # Python 2
                content = content.decode('utf-8')
            except AttributeError:  # Python 3
                pass
    except UnicodeDecodeError:
        raise UnableToDecodeTextFile(filepath)
        # Should "raise from", if Python 2 support is dropped.

    return content


def read_binary_file(filepath, fail=True):
    check_file(filepath, fail=fail)
    with _open(filepath, 'rb') as f:
        content = f.read()
    return content


def remove_file(filepath):
    check_file(filepath)
    os.remove(filepath)


def write_file(filepath, data, mode='w'):
    """Write data to file.

    Data should be unicode except when binary mode is selected,
    in which case data is expected to be binary.
    """
    check_directory(os.path.dirname(filepath))
    if 'b' not in mode and sys.version_info < (3,):
        # _open returns in binary mode for python2
        # Data must be encoded
        data = data.encode('utf-8')
    with _open(filepath, mode) as f:
        f.write(data)


# dealing with formatless content

def content_type(path):
    parsed = urlparse(path)
    if parsed.scheme == 'http':
        return 'url'
    else:
        return 'file'


def url_exists(url):
    parsed = urlparse(url)
    conn = HTTPConnection(parsed.netloc)
    conn.request('HEAD', parsed.path)
    response = conn.getresponse()
    conn.close()
    return response.status == 200


def check_content(path):
    if content_type(path) == 'url':
        return url_exists(path)
    else:
        return check_file(path)


def _get_byte_url_content(path, ui=None):
    if ui is not None:
        ui.message('dowloading {}'.format(path))
    response = urlopen(path)
    return response.read()


def _dump_byte_url_content(source, target):
    """Caution: this method does not test for existing destination.
    """
    byte_content = _get_byte_url_content(source)
    with _open(target, 'wb') as f:
        f.write(byte_content)


def get_content(path, ui=None):
    """Will be useful when we need to get content from url"""
    if content_type(path) == 'url':
        return _get_byte_url_content(path, ui=ui).decode(encoding='utf-8')
    else:
        return read_text_file(path)


def move_content(source, target, overwrite=False):
    source = system_path(source)
    target = system_path(target)
    if source == target:
        return
    if not overwrite and os.path.exists(target):
        raise IOError('target file exists')
    shutil.move(source, target)


def copy_content(source, target, overwrite=False):
    source_is_url = content_type(source) == 'url'
    if not source_is_url:
        source = system_path(source)
    target = system_path(target)
    if source == target:
        return
    if not overwrite and os.path.exists(target):
        raise IOError('{} file exists.'.format(target))
    if source_is_url:
        _dump_byte_url_content(source, target)
    else:
        shutil.copy(source, target)
