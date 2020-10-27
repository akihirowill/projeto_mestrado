#!/usr/bin/python3
import sqlite3
import os
from signame_utils import ver_from_signame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import matplotlib.dates as mdates
from collections import defaultdict
from datetime import date

log_path = '/home/william/ida_logs'

conn = sqlite3.connect('versions.db')


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


per_year = defaultdict(lambda: 0)


for filename in os.listdir(log_path):
    if not filename.endswith('.log'):
        continue
    basename = os.path.basename(filename)
    binname = basename[:-4]
    filename = os.path.join(log_path, filename)

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
        maxsigs = [signame for hits, signame in sigs if hits==maxhits] #>0.9*maxhits]
        maxsigs_ver = [ver_from_signame(signame) for signame in maxsigs]
        maxsigs_ts = [get_timestamp('glibc', ver) for ver in maxsigs_ver]
        #maxsigs_ts = [ts for ts in maxsigs_ts if ts is not None]
        if None in maxsigs_ts:
            continue
        ts = np.median(maxsigs_ts)
        year = date.fromtimestamp(ts).year
        print(binname, year)
        per_year[year] += 1


#plt.hist(series, bins=20, histtype='bar',
#         #weights=[np.ones(len(results_avail)) / len(results_avail), np.ones(len(results_unavail)) / len(results_unavail)],
#         label=['Versão prevista disponível', 'Versão prevista indisponível'])

min_year, max_year = min(per_year.keys()), max(per_year.keys())
xdata = list(range(min_year, max_year+1))
ydata = [per_year[y] for y in xdata]
plt.bar(xdata, ydata)

#plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
#plt.gca().xaxis.set_major_locator(mdates.YearLocator())
#plt.gcf().autofmt_xdate()
plt.ylabel('Número de amostras')
plt.xlabel('Ano da assinatura')
plt.xticks(xdata, fontsize=7, rotation=90)
plt.savefig('timeline.pdf')
