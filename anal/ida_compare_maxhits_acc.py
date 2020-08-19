#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.ticker import PercentFormatter

sig_acc = defaultdict(lambda: {})
sig_hits = defaultdict(lambda: [])

with open('ida_tptn_fpfn.txt') as f:
    for line in f:
        binname, acc, hits, curr_sig, relevant_and_retrived_documents, relevant_documents, retrieved_documents = line.strip().split()
        acc = float(acc)
        hits = int(hits)
        relevant_and_retrived_documents, relevant_documents, retrieved_documents = int(relevant_and_retrived_documents), int(relevant_documents), int(retrieved_documents)
        sig_acc[binname][curr_sig] = acc
        sig_hits[binname].append((hits, curr_sig))

deviations = []

for k in sig_acc.keys():
    maxhits, unused = max(sig_hits[k])
    maxacc = max(sig_acc[k].values())
    maxacc_maxhits = max(sig_acc[k][sig] for hits, sig in sig_hits[k] if hits == maxhits)
    deviations.append(maxacc - maxacc_maxhits)

dev=np.array(deviations, dtype=np.float)
print('min', dev.min())
print('max', dev.max())
print('mean', dev.mean())
print('std', dev.std())
print('<=0.01', sum(1 for x in dev if x<=0.01)/len(deviations))
plt.hist(dev, bins=20, weights=np.ones(len(dev)) / len(dev))
plt.ylabel('Porcentagem')
plt.xlabel('max(F1 score) - F1 score da assinatura com max(casamentos)')
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.savefig('ida_compare_maxhits_acc.pdf')
