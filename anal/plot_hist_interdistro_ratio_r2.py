#!/usr/bin/python3
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.ticker import PercentFormatter
from fuzzy_match import fuzzy_match
import multiprocessing

log_path = '/home/william/r2_logs'

sig_distro = {}
with open('sig_distro.txt') as f:
    for line in f:
        signame, distro = line.strip().split()
        sig_distro[signame] = distro


def process(filename):
    if not filename.endswith('.log'):
        return []
    basename = os.path.basename(filename)
    binname = basename[:-4]
    filename = os.path.join(log_path, filename)

    sig_symbols = {}
    sig_hits = []

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
                    sig_symbols[curr_sig] = dict(combined)     # all methods except offset
                    #sig_symbols[curr_sig] = dict(curr_symbols['graph'])
                    sig_hits.append((hits, curr_sig))
                elif line.startswith('f '):
                    unused, name, unused, unused, addr = line.split()
                    m = re.search('^sign\.([^.]+)\.sym\.([^\s]+)', name)
                    if m:
                        method, name = m.groups()
                        name = name.lstrip('_')   # sometimes there are preceding '_'s
                        addr = int(addr, 16)
                        curr_symbols[method][addr].add(name)


    # estimated est
    est_hits, est_signame = max(sig_hits)
    est_symbols = sig_symbols[est_signame]
    est_distro = sig_distro[est_signame]
    #total_est_symbols = sum(1 for name in est_symbols.values() if name)

    distro_acc = defaultdict(lambda: [])

    if len(est_symbols) < 5 or est_hits < 50:
        return []

    truth_symbols = est_symbols

    for curr_sig, meth_sym in sig_symbols.items():
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

        distro_acc[sig_distro[curr_sig]].append(acc)

    res = []
    print(binname, est_distro, est_hits, len(est_symbols))
    for distro, accs in distro_acc.items():
        k = distro + '/' + est_distro
        max_acc = max(accs)
        #print(binname, k, max_acc)
        res.append((k, max_acc))
    return res


distro_ratios = defaultdict(lambda: [])
p = multiprocessing.Pool()
for res in p.map(process, os.listdir(log_path)):
    for k, max_accs in res:
        distro_ratios[k].append(max_accs)


#labels = sorted(distro_ratios.keys())
labels = ['alpine/debian', 'debian/alpine',
          'alpine/ubuntu', 'ubuntu/alpine',
          'alpine/rhel', 'rhel/alpine',
          'debian/ubuntu', 'ubuntu/debian',
          'debian/rhel', 'rhel/debian',
          'rhel/ubuntu', 'ubuntu/rhel']
for k in 'alpine', 'debian', 'ubuntu', 'rhel':
    k = k+'/'+k
    arr = np.array(distro_ratios[k])
    if len(arr):
        print('%s\t%.5f\t%.5f' % (k, arr.mean(), arr.std()))
print()
for k in labels:
    arr = np.array(distro_ratios[k])
    if len(arr):
        print('%s\t%.5f\t%.5f' % (k, arr.mean(), arr.std()))
data = [distro_ratios[k] for k in labels]
plt.xlabel('Distro analisada / distro referência')
plt.ylabel('F1 score')
#plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.boxplot(data, 0, labels=labels, showmeans=True, meanprops={'alpha': 0.3})
plt.gcf().subplots_adjust(bottom=0.25)
plt.xticks(fontsize=7, rotation=90)
plt.savefig('hist_interdistro_ratio_r2.pdf')
