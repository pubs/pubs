import os
import subprocess


def full_compile(full_path_to_file, verbose=False):
    FNULL = None
    if not verbose:
        FNULL = open(os.devnull, 'w')
    filename, extension = os.path.splitext(full_path_to_file)
    run_pdflatex(filename, stdout=FNULL)
    run_bibtex(filename, stdout=FNULL)
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


