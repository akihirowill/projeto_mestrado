import os
import pickle

sym_path = '/home/william/samples/symbols'

def load_sym_file(binname):
    symfile = os.path.join(sym_path, binname + '.pickle')
    if not os.path.exists(symfile):
        return None
    with open(symfile, 'rb') as f:
        symbols : dict = pickle.load(f)
    return symbols
