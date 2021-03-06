#!/usr/bin/python3
import os
import re
import pickle
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.optimize import curve_fit
from matplotlib.ticker import PercentFormatter
from fuzzy_match import fuzzy_match
from symfile_utils import load_sym_file
import multiprocessing

log_path = '/home/william/ida_logs'


with open('sensitivity_sample.pickle', 'rb') as f:
    sensitivity_sample = pickle.load(f)


def process(args):
    binname, sig_sequence = args  # from sensitivity_sample, generated by plot_version_sensitivity_r2
    filename = os.path.join(log_path, binname + '.log')

    truth_symbols = load_sym_file(binname)
    if not truth_symbols:
        return None

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

    if len(est_symbols) < 5 or est_hits < 50:
        return None

    sensitivity_decay = []
    allowed_sigs = set(sig_sequence)

    for curr_sig, meth_sym in sig_symbols.items():
        if curr_sig.replace('-dev', '').replace('-devel', '').replace('-static', '') not in allowed_sigs:
            continue
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

        sensitivity_decay.append(acc)

    sensitivity_decay.sort(reverse=True)

    return sensitivity_decay


decay = []
p = multiprocessing.Pool()
for res in p.map(process, sensitivity_sample):
    if res:
        decay_item = res
        if decay_item[0] > 1e-3:
            for i in range(len(decay_item)):
                if i >= len(decay):
                    for j in range(len(decay) - i + 1):
                        decay.append([])
                decay[i].append(decay_item[i]/decay_item[0])


print(len(decay[0]), 'samples after all...')

plt.xlabel('Distância da melhor versão de libc')
plt.ylabel('F1 score normalizado')
#plt.yscale('log')
#plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.boxplot(decay, 0, showmeans=True, meanprops={'alpha': 0.3})


def func(x, a):
    return np.exp(a * (x-1))

xdata = []
ydata = []
for i, sublist in enumerate(decay):
    xdata.extend([i+1]*len(sublist))
    ydata.extend(sublist)
xdata = np.array(xdata, dtype=np.float)
ydata = np.array(ydata, dtype=np.float)
popt, pcov = curve_fit(func, xdata, ydata)
print('popt=', popt, 'pcov=', pcov)
plt.plot(xdata, func(xdata, *popt), 'g-', alpha=.3, label='fit: a=%.3f' % tuple(popt))

plt.gcf().subplots_adjust(bottom=0.25)
plt.xticks(fontsize=7, rotation=90)
plt.legend(loc='upper right')
plt.savefig('version_sensitivity_ida.pdf')
