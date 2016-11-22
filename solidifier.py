#!/usr/bin/env python

"""Solidifier.

Usage:
    solidifier.py verify [--filename=<solidity file>]
    solidifier.py (-h | --help)

Options:
    -h --help     Show this screen.
    --version     Show version.
    --file        Solidity filename

"""
import subprocess, sys
import docopt
from tempfile import mkstemp

import sol2c
import utils

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='El solidificador')
    fname = arguments['--filename']

    solc_process = subprocess.Popen(['solc', '--ast-json', fname], stdout=subprocess.PIPE)
    out, err = solc_process.communicate()
    if err != None:
        print 'Error running solc', err
        sys.exit(1)
    (_, tmp_json) = mkstemp()

    with open(tmp_json, 'w') as f:
        f.write(out)
    
    utils.purify_json(tmp_json)
    t = sol2c.CTranslator()
    C_code = t.translate_to_C(tmp_json)
    
    with open('tmp.c', 'w') as f:
        f.write(C_code)

    seahorn_process = subprocess.Popen(['sea', 'pf', 'tmp.c'], stdout=subprocess.PIPE)
    out, err = solc_process.communicate()
    print out

