#!/usr/bin/python3
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.ticker import PercentFormatter
from signame_utils import sig_arch
from symfile_utils import load_sym_file
import numpy as np
from signame_utils import *


def max_acc_per_bin(filename):
    sig_acc = defaultdict(lambda: defaultdict(lambda: []))
    bin_arch = {}
    bin_symlen = {}
    with open(filename) as f:
        for line in f:
            binname, acc, hits, curr_sig, relevant_and_retrived_documents, relevant_documents, retrieved_documents = line.strip().split()
            curr_sig, method = sig_method(curr_sig)
            acc = float(acc)
            hits = int(hits)
            relevant_and_retrived_documents, relevant_documents, retrieved_documents = int(relevant_and_retrived_documents), int(relevant_documents), int(retrieved_documents)

            if binname not in bin_symlen:
                bin_symlen[binname] = len(load_sym_file(binname))

            arch = sig_arch(curr_sig)
            if binname in bin_arch:
                assert arch == bin_arch[binname]
            bin_arch[binname] = arch

            assert bin_symlen[binname] == relevant_documents
            sig_acc[arch][binname].append(relevant_and_retrived_documents/bin_symlen[binname])
    return {arch: {binname: max(v[binname]) for binname in v.keys()} for arch, v in sig_acc.items()}


ida = max_acc_per_bin('ida_tptn_fpfn.txt')
labels = []
data = []
for arch, arch_bins in ida.items():
    vals = list(arch_bins.values())
    print(arch, '>=0.80', sum(1 for x in vals if x>=0.80)/len(vals))
    labels.append(arch)
    data.append(vals)
plt.ylabel('Funções corretamente detectadas / funções da libc')
plt.xlabel('Arquitetura')
plt.ylim([-0.01, 1.01])
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.boxplot(data, 0, labels=labels, showmeans=True, meanprops={'alpha': 0.3})
plt.savefig('hist_hitratio.pdf')

