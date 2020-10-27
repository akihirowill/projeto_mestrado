#!/usr/bin/python3
import sqlite3
import os
from signame_utils import ver_from_signame
from gccver_to_glibcver import get_libc_for_file
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

bin_path = '/home/william/samples/unupx'
log_path = '/home/william/ida_logs'

conn = sqlite3.connect('versions.db')

with open('allsigs.txt') as f:
    allsigs = set(ver_from_signame(s.strip()) for s in f)


def get_timestamp(name, version):
    c = conn.cursor()
    c.execute("SELECT timestamp FROM versions "
              "WHERE name=? AND version=?",
              (name, version))
    row = c.fetchone()
    if not row:
        return None
    ts, = row
    return ts


results_avail = []
results_unavail = []

for filename in os.listdir(log_path):
    if not filename.endswith('.log'):
        continue
    basename = os.path.basename(filename)
    binname = basename[:-4]
    filename = os.path.join(log_path, filename)

    predicted_ver = get_libc_for_file(os.path.join(bin_path, binname))
    if not predicted_ver:
        continue

    if any(ver in allsigs for ver in predicted_ver):
        results = results_avail
    else:
        results = results_unavail

    predicted_ts = [get_timestamp('glibc', ver) for ver in predicted_ver]
    predicted_ts = [ts for ts in predicted_ts if ts is not None]  # skip musl by now
    if predicted_ts == []:
        continue

    with open(filename) as f:
        sigs = []
        for line in f:
            if line.startswith('==>'):
                arr = line.split()
                curr_sig = arr[1]
                hits = int(arr[2])
                sigs.append((hits, curr_sig))
        maxhits, unused = max(sigs)
        if maxhits < 50:
            continue
        maxsigs = [signame for hits, signame in sigs if hits>0.9*maxhits]
        maxsigs_ver = [ver_from_signame(signame) for signame in maxsigs]
        maxsigs_ts = [get_timestamp('glibc', ver) for ver in maxsigs_ver]
        #maxsigs_ts = [ts for ts in maxsigs_ts if ts is not None]
        if None in maxsigs_ts:
            print(binname, [ver for ver in maxsigs_ver if not get_timestamp('glibc', ver)])
            continue
        diff = []
        for ts1 in predicted_ts:
            for ts2 in maxsigs_ts:
                diff.append(abs(ts2 - ts1))
        mindiff = min(diff)/(24*3600)
        #print(mindiff)
        results.append(mindiff)

series = [results_avail, results_unavail]
#total = len(results_avail) + len(results_unavail)

for qtd in 7, 15, 30:
    print('avail <=%d dias: %.5f' % (qtd, sum(1 for d in results_avail if d <= qtd)/len(results_avail)))
    print('unavail <=%d dias %.5f' % (qtd, sum(1 for d in results_unavail if d <= qtd)/len(results_unavail)))

plt.hist(series, bins=20, histtype='bar',
         #weights=[np.ones(len(results_avail)) / len(results_avail), np.ones(len(results_unavail)) / len(results_unavail)],
         label=['Versão prevista disponível', 'Versão prevista indisponível'])

plt.ylabel('Quantidade de amostras')
plt.xlabel('Dias de diferença entre versão prevista e versão da assinatura')
#plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.legend(loc='upper right')
plt.savefig('hist_diff_changelog.pdf')
