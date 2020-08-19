#!/usr/bin/python3
import os
import re
import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path

r2_path = '/home/william/r2_logs'
ida_path = '/home/william/ida_logs'
samples_path = '/home/william/samples/stripped'

with open('num_funcs_per_bin.pickle', 'rb') as f:
    num_funcs_per_bin = pickle.load(f)


def func(x, a):
    return a * x


def do_path(path, fit_spec, pts_spec, lbl_fmt):
    xdata = []
    ydata = []

    for filename in os.listdir(path):
        if not filename.endswith('.log'):
            continue
        basename = os.path.basename(filename)
        binname = basename[:-4]
        filename = os.path.join(path, filename)
        with open(filename) as f:
            for line in f:
                m = re.search(r'^\*\*\* time spent with the initial analysis: ([^\s]+)', line)
                if m:
                    xdata.append(num_funcs_per_bin[binname])
                    #xdata.append(Path(os.path.join(samples_path, binname)).stat().st_size / 1e6)
                    ydata.append(float(m.group(1)))
                    break

    xdata = np.array(xdata, dtype=np.float)
    ydata = np.array(ydata, dtype=np.float)

    popt, pcov = curve_fit(func, xdata, ydata)
    print(path, 'popt=', popt, 'pcov=', pcov)

    plt.plot(xdata, func(xdata, *popt), fit_spec, alpha=.3, label=lbl_fmt % tuple(popt))
    plt.plot(xdata, ydata, pts_spec, markersize=5, markeredgewidth=0)


do_path(r2_path, 'r-', 'r.', 'radare2 (fit: a=%.3f)')
do_path(ida_path, 'g-', 'g.', 'IDA Pro (fit: a=%.3f)')
plt.xlim([0, 10500])
plt.ylim([0, 520])
#plt.xlabel('Tamanho do arquivo (Mbytes)')
plt.xlabel('Número de funções (detectadas pelo IDA Pro)')
plt.ylabel('Tempo de análise inicial (segundos)')
plt.legend(loc='upper center')
plt.savefig('plot_initial_analysis_time.pdf')
