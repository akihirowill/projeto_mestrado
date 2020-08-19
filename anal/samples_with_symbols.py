#!/usr/bin/python3
import os
import re
import pickle
import subprocess
from collections import defaultdict


bin_path = '/home/william/samples/unupx'
sym_path = '/home/william/samples/symbols'


os.makedirs(sym_path, exist_ok=True)


with open('libc_symbol_names.txt') as f:
    libc_symbol_names = set(s.strip() for s in f)


for filename in os.listdir(bin_path):
    binname = filename
    filename = os.path.join(bin_path, filename)
    try:
        out = subprocess.check_output(['nm', filename]).decode('utf-8')
    except subprocess.CalledProcessError:
        continue
    results = defaultdict(lambda: set())
    for line in out.splitlines():
        m = re.match(r'^\s*([0-9a-fA-F]+)\s+[tT]\s+([^\s]+)', line)  # only .text entries
        if not m:
            continue
        addr, symbol = m.groups()
        addr = int(addr, 16)
        symbol = symbol.lstrip('_')   # sometimes there are preceding '_'s
        if symbol in libc_symbol_names:
            results[addr].add(symbol)
    if results:
        with open(os.path.join(sym_path, binname + '.pickle'), 'wb') as f:
            pickle.dump(dict(results), f)
