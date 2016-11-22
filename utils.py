def purify_json(fname):
    f = open(fname, 'r')
    source = f.read()
    f.close()
    begin = source.index('{')
    end = source.rindex('}')
    f = open(fname, 'w')
    f.write(source[begin:(end + 1)])
    f.close()
