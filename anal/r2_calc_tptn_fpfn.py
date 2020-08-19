#!/usr/bin/pypy3
import os
import re
#from math import sqrt
from fuzzy_match import fuzzy_match
from symfile_utils import load_sym_file
from collections import defaultdict

log_path = '/home/william/r2_logs'


for filename in os.listdir(log_path):
    if not filename.endswith('.log'):
        continue
    basename = os.path.basename(filename)
    binname = basename[:-4]
    truth_symbols = load_sym_file(binname)
    if not truth_symbols:
        continue
    filename = os.path.join(log_path, filename)

    sig_symbols = {}
    sig_hits = {}

    with open(filename) as f:
        state = 0
        curr_sig = None
        for line in f:
            if state == 0:
                if line.startswith('==>'):
                    state = 1
                    arr = line.split()
                    curr_sig = arr[1]
                    hits = int(arr[2])
                    curr_symbols = defaultdict(lambda: defaultdict(lambda: set()))
            elif state == 1:
                if line.strip() == '':
                    state = 0
                    combined = defaultdict(lambda: set())
                    for method, meth_sym in curr_symbols.items():
                        if method != 'offset':
                            for addr, names in meth_sym.items():
                                combined[addr].update(names)
                    curr_symbols['combined'] = combined   # all methods except offset
                    sig_symbols[curr_sig] = dict(curr_symbols)
                    sig_hits[curr_sig] = hits
                elif line.startswith('f '):
                    unused, name, unused, unused, addr = line.split()
                    m = re.search('^sign\.([^.]+)\.sym\.([^\s]+)', name)
                    if m:
                        method, name = m.groups()
                        name = name.lstrip('_')   # sometimes there are preceding '_'s
                        addr = int(addr, 16)
                        curr_symbols[method][addr].add(name)


    curr_stats = []

    for curr_sig, curr_symbols in sig_symbols.items():
        for method, meth_sym in curr_symbols.items():
            # https://en.wikipedia.org/wiki/Precision_and_recall#Definition_(information_retrieval_context)
            relevant_documents = len(truth_symbols)
            retrieved_documents = 0
            relevant_and_retrived_documents = 0
            for addr, names in meth_sym.items():
                est_name = truth_symbols.get(addr)
                for name in names:
                    retrieved_documents += 1
                    if est_name and fuzzy_match(name, est_name):
                        relevant_and_retrived_documents += 1
            precision = relevant_and_retrived_documents/retrieved_documents if retrieved_documents else 0
            recall = relevant_and_retrived_documents/relevant_documents if relevant_documents else 0
            # https://en.wikipedia.org/wiki/F1_score
            acc = 2/(1/precision + 1/recall) if precision!=0 and recall!=0 else 0

            hits = sig_hits[curr_sig]
            curr_stats.append((acc, hits, method, curr_sig, relevant_and_retrived_documents, relevant_documents, retrieved_documents))

    curr_stats.sort(reverse=True)
    for acc, hits, method, curr_sig, relevant_and_retrived_documents, relevant_documents, retrieved_documents in curr_stats:
        print('%s\t%5.4f\t%d\t%s\t%d\t%d\t%d' % (binname.ljust(64), acc, hits, (curr_sig+':'+method).ljust(50), relevant_and_retrived_documents, relevant_documents, retrieved_documents))
