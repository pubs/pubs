import os
import subprocess

from .autofill_tools import replace_pattern

DO_NOT_MODIFY_PATTERN = '%DO_NOT_MODIFY{INFO}'
HEADER_PATTERN = '%HEADER{INFO}'


def extract_note(text):
    text = replace_pattern(text, DO_NOT_MODIFY_PATTERN, 'INFO')
    text = text.replace(DO_NOT_MODIFY_PATTERN, '')
    text = replace_pattern(text, HEADER_PATTERN, 'INFO')
    text = text.replace(HEADER_PATTERN, '')
    return remove_empty_lines(text)


def remove_empty_lines(text):
    cleaned_text = ''
    for line in text.split('\n'):
        if line.strip():
                cleaned_text += line + '\n'
    return cleaned_text[:-1]


def full_compile(full_path_to_file, verbose=False):
    FNULL = None
    if not verbose:
        FNULL = open(os.devnull, 'w')
    filename, extension = os.path.splitext(full_path_to_file)
    run_pdflatex(filename, stdout=FNULL)
    run_bibtex(filename, stdout=FNULL)
    run_makeglossaries(filename, stdout=FNULL)
    run_pdflatex(filename, stdout=FNULL, nb_time=3)


def run_command(command, full_path_to_file, stdout=None, nb_time=1):
    origWD = os.getcwd() # remember our original working directory
    folder, filename = os.path.split(full_path_to_file)
    os.chdir(folder)
    for _ in xrange(nb_time):
        cmd = command.split()
        cmd.append(filename)
        subprocess.call(cmd, stdout=stdout)
    os.chdir(origWD) # get back to our original working directory


def run_pdflatex(full_path_to_file, stdout=None, nb_time=1):
    run_command('pdflatex', full_path_to_file, stdout, nb_time)


def run_bibtex(full_path_to_file, stdout=None, nb_time=1):
    run_command('bibtex', full_path_to_file, stdout, nb_time)

def run_makeglossaries(full_path_to_file, stdout=None, nb_time=1):
    run_command('makeglossaries', full_path_to_file, stdout, nb_time)
