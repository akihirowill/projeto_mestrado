#!/usr/bin/pypy3
import os
#from math import sqrt
from fuzzy_match import fuzzy_match
from symfile_utils import load_sym_file

log_path = '/home/william/ida_logs'


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
    sig_dets = []
    sig_hits = {}

    with open(filename) as f:
        state = 0
        signame = None
        for line in f:
            if state == 0:
                if line.startswith('==>'):
                    state = 1
                    arr = line.split()
                    signame = arr[1]
                    hits = int(arr[2])
                    symbols = {}
            elif state == 1:
                if line.strip() == '':
                    state = 0
                    sig_symbols[signame] = symbols
                    sig_dets.append((len(symbols), signame))
                    sig_hits[signame] = hits
                else:
                    addr, name, is_new, is_lib = line.split()
                    name = name.lstrip('_')   # sometimes there are preceding '_'s
                    addr = int(addr, 16)
                    is_new = int(is_new) == 1
                    is_lib = int(is_lib) == 1
                    is_a_match = is_new and is_lib  # criteria for match
                    if is_a_match:
                        symbols[addr] = name


        # estimated est
        unused, est_signame = min(sig_dets)
        est_hits = len(truth_symbols)
        est_symbols = truth_symbols
        #total_est_symbols = sum(1 for name in est_symbols.values() if name)

        curr_stats = []

        for curr_sig, meth_sym in sig_symbols.items():
            # https://en.wikipedia.org/wiki/Precision_and_recall#Definition_(information_retrieval_context)
            relevant_documents = len(est_symbols)
            retrieved_documents = 0
            relevant_and_retrived_documents = 0
            for addr, name in meth_sym.items():
                est_name = est_symbols.get(addr)
                retrieved_documents += 1
                if est_name and fuzzy_match(name, est_name):
                    relevant_and_retrived_documents += 1
            precision = relevant_and_retrived_documents/retrieved_documents if retrieved_documents else 0
            recall = relevant_and_retrived_documents/relevant_documents if relevant_documents else 0
            # https://en.wikipedia.org/wiki/F1_score
            acc = 2/(1/precision + 1/recall) if precision!=0 and recall!=0 else 0

            hits = sig_hits[curr_sig]
            curr_stats.append((acc, hits, curr_sig, relevant_and_retrived_documents, relevant_documents, retrieved_documents))

        curr_stats.sort(reverse=True)
        for acc, hits, curr_sig, relevant_and_retrived_documents, relevant_documents, retrieved_documents in curr_stats:
            print('%s\t%5.4f\t%d\t%s\t%d\t%d\t%d' % (binname.ljust(64), acc, hits, curr_sig.ljust(50), relevant_and_retrived_documents, relevant_documents, retrieved_documents))
