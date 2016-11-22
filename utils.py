def purify_json(fname):
    with open(fname, 'r') as f:
        source = f.read()
        f.close()
        begin = source.index('{')
        end = source.rindex('}')
    with open(fname, 'w') as f:
        f.write(source[begin:(end + 1)])
        f.close()

