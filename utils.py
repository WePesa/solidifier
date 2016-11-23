def purify_json(fname):
    with open(fname, 'r') as f:
        source = f.read()
        f.close()
        begin = source.index('{')
        end = source.rindex('}')
    with open(fname, 'w') as f:
        f.write(source[begin:(end + 1)])
        f.close()

def calculate_program_hash():
    from hashlib import sha256
    hasher = sha256()
    files = ['solidifier', 'solidifier.h', 'sol2c.py', 'utils.py']
    for f in files:
        with open(f, 'r') as of:
            buf = of.read()
            hasher.update(buf)
    return hasher.hexdigest()

