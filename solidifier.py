#!/usr/bin/python

import os
import sys

import sol2c
import utils

if __name__ == '__main__':
    fname = sys.argv[1]

    os.system('solc --ast-json ' + fname + ' > ' + fname + '.json')
    fname += '.json'

    utils.purify_json(fname)
    t = sol2c.CTranslator()
    C_code = t.translate_to_C(fname)
    print C_code


