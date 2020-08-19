#!/usr/bin/python3
import glob
import os
import subprocess
import multiprocessing


def detect_arch(filename):
    what = subprocess.check_output(['file', filename]).decode('utf-8')

    if 'ELF' not in what:
        return

    bits = 0
    if '32-bit' in what:
        bits = 32
    elif '64-bit' in what:
        bits = 64
    assert bits != 0

    endian = None
    if ' LSB ' in what:
        endian = 'el'
    elif ' MSB ' in what:
        endian = 'eb'

    arch = None
    if ', Intel 80386,' in what:
        assert bits == 32
        assert endian == 'el'
        arch = 'i386'
    elif ', x86-64,' in what:
        assert bits == 64
        assert endian == 'el'
        arch = 'amd64'
    elif ', MIPS,' in what:
        assert bits == 32
        arch = 'mips' + endian
    elif ', PowerPC or cisco 4500,' in what:
        assert bits == 32
        assert endian == 'eb'
        arch = 'powerpc'
    elif ', ARM,' in what:
        assert bits == 32
        assert endian == 'el'
        arch = 'arm32'
    elif ', ARM aarch64,' in what:
        assert bits == 64
        assert endian == 'el'
        arch = 'arm64'

    return arch


def cleanup_idb(filename):
    for to_clean in glob.glob(glob.escape(filename) + '*.*'):
        os.remove(to_clean)


def process_file(filename):
    arch = detect_arch(filename)
    if arch is None:
        return
    print(filename, arch)
    cleanup_idb(filename)
    subprocess.check_call(["ida64", "-A",
                           "-S/home/william/trysigs.py /home/william/siglist/{}.txt".format(arch),
                           filename])
    cleanup_idb(filename)


def main():
    p = multiprocessing.Pool()
    p.map(process_file, os.listdir('.'))


if __name__ == '__main__':
    main()
