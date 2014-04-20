import os
import subprocess
import tempfile
import shutil

from .p3 import urlparse, HTTPConnection, urlopen


# files i/o

def _check_system_path_exists(path, fail=True):
    answer = os.path.exists(path)
    if not answer and fail:
        raise IOError("File does not exist: {}".format(path))
    else:
        return answer


def _check_system_path_is(nature, path, fail=True):
    if nature == 'file':
        check_fun = os.path.isfile
    elif nature == 'dir':
        check_fun = os.path.isdir
    answer = check_fun(path)
    if not answer and fail:
        raise IOError("{} is not a {}.".format(path, nature))
    else:
        return answer


def check_file(path, fail=True):
    syspath = system_path(path)
    return (_check_system_path_exists(syspath, fail=fail)
            and _check_system_path_is('file', syspath, fail=fail))


def check_directory(path, fail=True):
    syspath = system_path(path)
    return (_check_system_path_exists(syspath, fail=fail)
            and _check_system_path_is('dir', syspath, fail=fail))


def read_file(filepath):
    check_file(filepath)
    with open(system_path(filepath), 'r') as f:
        s = f.read()
    return s


def write_file(filepath, data):
    check_directory(os.path.dirname(filepath))
    with open(system_path(filepath), 'w') as f:
        f.write(data)


def system_path(path):
    return os.path.abspath(os.path.expanduser(path))


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


def get_content(path, ui=None):
    """Will be useful when we need to get content from url"""
    if content_type(path) == 'url':
        if ui is not None:
            ui.print_('dowloading {}'.format(path))
        response = urllib2.urlopen(path)
        return response.read()
    else:
        return read_file(path)


def move_content(source, target, overwrite = False):
    if source == target:
        return
    if not overwrite and os.path.exists(target):
        raise IOError('target file exists')
    shutil.move(source, target)


def copy_content(source, target, overwrite = False):
    if source == target:
        return
    if not overwrite and os.path.exists(target):
        raise IOError('target file exists')
    shutil.copy(source, target)


def editor_input(editor, initial="", suffix='.tmp'):
    """Use an editor to get input"""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        tfile_name = temp_file.name
        temp_file.write(initial)
    cmd = editor.split()  # this enable editor command with option, e.g. gvim -f
    cmd.append(tfile_name)
    subprocess.call(cmd)
    with open(tfile_name) as temp_file:
        content = temp_file.read()
    os.remove(tfile_name)
    return content


def edit_file(editor, path_to_file, temporary=True):
    if temporary:
        check_file(path_to_file, fail=True)
        with open(path_to_file) as f:
            content = f.read()
        content = editor_input(editor, content)
        with open(path_to_file, 'w') as f:
            f.write(content)
    else:
        cmd = editor.split()  # this enable editor command with option, e.g. gvim -f
        cmd.append(path_to_file)
        subprocess.call(cmd)
