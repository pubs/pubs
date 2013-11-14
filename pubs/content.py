import os
import subprocess
import tempfile
import shutil

import urlparse
import httplib
import urllib2


    # files i/o

def check_file(path, fail=True):
    if fail:
        if not os.path.exists(path):
            raise IOError("File does not exist: {}.".format(path))
        if not os.path.isfile(path):
            raise IOError("{} is not a file.".format(path))
        return True
    else:
        return os.path.exists(path) and os.path.isfile(path)

def check_directory(path, fail=True):
    if fail:
        if not os.path.exists(path):
            raise IOError("File does not exist: {}.".format(path))
        if not os.path.isdir(path):
            raise IOError("{} is not a directory.".format(path))
        return True
    else:
        return os.path.exists(path) and os.path.isdir(path)

def read_file(filepath):
    check_file(filepath)
    with open(filepath, 'r') as f:
        s = f.read()
    return s
        
def write_file(filepath, data):
    check_directory(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        f.write(data)


    # dealing with formatless content

def content_type(path):
    parsed = urlparse.urlparse(path)
    if parsed.scheme == 'http':
        return 'url'
    else:
        return 'file'

def url_exists(url):
    parsed = urlparse.urlparse(url)
    conn = httplib.HTTPConnection(parsed.netloc)
    conn.request('HEAD', parsed.path)
    response = conn.getresponse()
    conn.close()
    return response.status == 200

    
def check_content(path):
    if content_type(path) == 'url':
        return url_exists(path)
    else:
        return check_file(path)

def get_content(path):
    """Will be useful when we need to get content from url"""
    if content_type(path) == 'url':
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


    # editor input

def editor_input(editor, initial="", suffix=None):
    """Use an editor to get input"""
    if suffix is None:
        suffix = '.tmp'
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        tfile_name = temp_file.name
        temp_file.write(initial)
        temp_file.flush()
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
