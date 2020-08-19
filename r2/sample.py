#!/usr/bin/python3
import os
import sys
import random
import pickle

dic = {}

for filename in sys.argv[1:]:
    assert filename.endswith('.log')
    binfile = os.path.basename(filename)[:-4]
    sigs = []
    with open(filename) as f:
        for line in f:
            if line.startswith('==>'):
                unused, signame, hits = line.strip().split()
                hits = int(hits)
                signame = signame.replace('-devel', '').replace('-static', '').replace('-dev', '')
                sigs.append((hits, signame))
    maxhits, unused = max(sigs)
    choices = {random.choice([signame for hits, signame in sigs if hits == maxhits]), }
    curhits = maxhits
    N = 30
    decrfac = 0.9
    while len(choices) < N and curhits > 0:
        options = [signame for hits, signame in sigs
                   if hits >= int(decrfac * curhits) and
                   hits   <= curhits and
                   signame not in choices]
        if options:
            choices.add(random.choice(options))
        curhits = int(decrfac * curhits)
    options = set(signame for hits, signame in sigs) - choices
    if len(options) >= N - len(choices):
        choices.update(random.sample(set(signame for hits, signame in sigs) - choices,
                                     N - len(choices)))
    dic[binfile] = choices

with open('sample.pickle', 'wb') as f:
    pickle.dump(dic, f)
