#!/usr/bin/env python

"""Solidifier.

Usage:
    solidifier.py [verify | translate] [-o <outfile>] [-c <cfile>] [--verbose] <solfile> 
    solidifier.py -h | --help | --version

Options:
    verify      Verify the solifity code.
    translate   Translate the solidity code to C.

    -h --help     Show this screen.
    --version     Show version.
    --verbose     Print the output from the model checker.
    -o <outfile>  Specify output file (requires --verbose).
    -c <cfile>    Specify output translated C file.
"""

from docopt import docopt
import subprocess, sys
import os
from tempfile import mkstemp

import sol2c
import utils

if __name__ == '__main__':
    arguments = docopt(__doc__, version='El solidificador')
    fname = arguments['<solfile>']
    outname = arguments['-o']
    verbose = arguments['--verbose']
    verify = arguments['verify']
    translate = arguments['translate']
    coutfile = arguments['-c']

    if verify or translate:
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
        
        if coutfile != None:
            filename, fileext = os.path.splitext(coutfile)
            if fileext != '.c':
                print 'Output C file should have .c extension'
                sys.exit(1)
            cfile = coutfile
            with open(coutfile, 'w') as f:
                f.write(C_code)
        elif translate:
            print C_code
                
    if verify:
        if coutfile == None:
            (_, cfile) = mkstemp(suffix='.c', dir='.')
            with open(cfile, 'w') as f:
                f.write(C_code)

        seahorn_process = subprocess.Popen(['sea', 'pf', cfile], stdout=subprocess.PIPE)
        out, err = seahorn_process.communicate()
        if verbose:
            if outname != None:
                with open(outname, 'w') as f:
                    f.write(out)
            else:
                print out

        if coutfile == None:
            os.remove(cfile)

