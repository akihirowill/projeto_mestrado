import os
import sys
import time
import pickle
import r2pipe
import multiprocessing

sdb_path = '/home/william/w/libc/sigs/sdb'
out_path = '/home/william/r2_logs'
os.makedirs(out_path, exist_ok=True)

with open('sample.pickle', 'rb') as f:
    sigsample = pickle.load(f)


def doit(filename):
    basename = os.path.basename(filename)
    sigset = sigsample.get(basename)
    if not sigset:
        return
    with open(os.path.join(out_path, basename + '.log'), 'w') as log:
        print('analysing', repr(basename))
        r2 = r2pipe.open(filename)
        t1 = time.time()
        r2.cmd('aaa')
        t2 = time.time()
        log.write('\n\n*** time spent with the initial analysis: %.3f seconds\n' % (t2 - t1))
        r2.cmd('e search.in=io.section')
        for sig in sigset:
            print('applying sig', repr(sig))
            r2.cmd('z-*')
            r2.cmd('zo {}.sdb'.format(os.path.join(sdb_path, sig)))
            res = r2.cmd('z/*')
            hits = sum(1 for line in res.splitlines() if line.startswith('f sign.'))
            log.write('\n\n==> %s %d\n' % (sig, hits))
            log.write(res)
            log.flush()
        t3 = time.time()
        log.write('\n\n*** time spent applying sigs: %.3f seconds\n' % (t3 - t2))


if __name__ == '__main__':
    p = multiprocessing.Pool()
    p.map(doit, sys.argv[1:])
