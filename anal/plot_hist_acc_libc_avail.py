#!/usr/bin/python3
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.ticker import PercentFormatter
import numpy as np
import os
from gccver_to_glibcver import get_libc_for_file
from signame_utils import *

bin_path = '/home/william/samples/unupx'

bin_has_libc_avail = set()

def max_acc_per_bin(filename):
    sig_acc = defaultdict(lambda: defaultdict(lambda: []))
    bin_arch = {}
    bin_libc = {}
    with open(filename) as f:
        for line in f:
            binname, acc, hits, curr_sig, relevant_and_retrived_documents, relevant_documents, retrieved_documents = line.strip().split()
            curr_sig, method = sig_method(curr_sig)
            acc = float(acc)
            hits = int(hits)
            relevant_and_retrived_documents, relevant_documents, retrieved_documents = int(relevant_and_retrived_documents), int(relevant_documents), int(retrieved_documents)

            arch = sig_arch(curr_sig)
            if binname in bin_arch:
                assert arch == bin_arch[binname]
            bin_arch[binname] = arch

            if not binname in bin_libc:
                bin_libc[binname] = get_libc_for_file(os.path.join(bin_path, binname))

            #print(ver_from_signame(curr_sig))
            if ver_from_signame(curr_sig) in bin_libc[binname]:
                bin_has_libc_avail.add(binname)

            sig_acc[arch][binname].append(acc)
    return {arch: {binname: max(v[binname]) for binname in v.keys() if binname in bin_has_libc_avail} for arch, v in sig_acc.items()}


ida = max_acc_per_bin('ida_tptn_fpfn.txt')
labels = []
data = []
for arch, arch_bins in ida.items():
    vals = list(arch_bins.values())
    print('ida', arch, len(vals), 'samples')
    if len(vals) > 0:
        print('ida', arch, '>=0.80', sum(1 for x in vals if x>=0.80)/len(vals))
        labels.append(arch)
        data.append(vals)
plt.boxplot(data, 0, labels=labels, showmeans=True, meanprops={'alpha': 0.3})


plt.xlabel('Arquitetura')
plt.ylabel('F1 score')
plt.ylim([-0.01, 1.01])
plt.savefig('hist_acc_ida_libc_avail.pdf')


plt.clf()

r2 = max_acc_per_bin('r2_tptn_fpfn.txt')
labels = []
data = []
for arch, arch_bins in r2.items():
    vals = list(arch_bins.values())
    print('r2', arch, len(vals), 'samples')
    if len(vals) > 0:
        print('r2', arch, '>=0.20', sum(1 for x in vals if x>=0.20)/len(vals))
        labels.append(arch)
        data.append(vals)
plt.boxplot(data, 0, labels=labels, showmeans=True, meanprops={'alpha': 0.3})


plt.xlabel('Arquitetura')
plt.ylabel('F1 score')
plt.ylim([-0.01, 1.01])
plt.savefig('hist_acc_r2_libc_avail.pdf')