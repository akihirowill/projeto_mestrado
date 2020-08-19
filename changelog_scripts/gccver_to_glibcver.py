#!/usr/bin/python3
# get probable glibc versions by gcc version
import sqlite3
import logging
import subprocess
from datetime import datetime
import sys
import re

logging.basicConfig(level=logging.WARN)

conn = sqlite3.connect('versions.db')


def ts2str(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def get_timespan(package, version, distro):
    c = conn.cursor()
    c.execute("SELECT timestamp, distro_release FROM versions "
              "WHERE package=? AND version=? AND distro=?",
              (package, version, distro))
    row = c.fetchone()
    if not row:
        return None
    t1, distro_release = row
    c.execute("SELECT timestamp, version FROM versions "
              "WHERE package=? AND distro=? "
              "  AND (distro_release=? OR distro_release IS NULL) "
              "  AND timestamp>?"
              "ORDER BY timestamp ASC LIMIT 1",
              (package, distro, distro_release, t1))
    row = c.fetchone()
    t2, v2 = None, None
    if row:
        t2, v2 = row   # None if open-ended
    logging.info('get_timespan: %s %s -> %s (%s): %s -> %s',
                 package,
                 version, v2 or 'None',
                 distro_release or 'None',
                 ts2str(t1),
                 ts2str(t2) if t2 else 'None')
    return t1, t2, distro_release


def versions_in_timespan(package, distro, t1, t2, distro_release):
    vers = set()
    c = conn.cursor()
    c.execute("SELECT version, timestamp FROM versions "
              "WHERE package=? AND distro=? "
              "  AND (distro_release=? OR distro_release IS NULL) "
              "  AND timestamp<=?"
              "ORDER BY timestamp DESC LIMIT 1",
              (package, distro, distro_release, t1))
    row = c.fetchone()
    if row:
        ver, ts = row
        logging.info('versions_in_timespan: %s: %s (%s)', package, ver, ts2str(ts))
        vers.add(ver)
    c.execute("SELECT version, timestamp FROM versions "
              "WHERE package=? AND distro=? "
              "  AND (distro_release=? OR distro_release IS NULL) "
              "  AND timestamp>? "
              "  AND (timestamp<? OR ? IS NULL)"
              "ORDER BY timestamp ASC",
              (package, distro, distro_release, t1, t2, t2))
    for row in c.fetchmany():
        ver, ts = row
        logging.info('versions_in_timespan: %s: %s (%s)', package, ver, ts2str(ts))
        vers.add(ver)
    return vers


def parse_gccver(gccver):
    m = re.search(r'\(Debian ([^)]+)\)', gccver)
    if m:
        ver, = m.groups()
        if 'ubuntu' in ver:
            return 'ubuntu', ver
        return 'debian', ver
    m = re.search(r'\(Ubuntu[^ ]* ([^)]+)\)', gccver)
    if m:
        ver, = m.groups()
        return 'ubuntu', ver
    m = re.search(r'\(Red Hat.*? ([^) ]+)\)', gccver)
    if m:
        ver, = m.groups()
        return 'centos', ver
    m = re.search(r'\(Alpine ([\d.]+)\)', gccver)
    if m:
        ver, = m.groups()
        return 'alpine', ver


def alpine_gccver_to_glibcver(version):
    with open('gcc_musl.txt') as f:
        for line in f:
            distro_release, gcc, musl = line.strip().split()
            if gcc == version:
                return 'alpine', distro_release, {musl, }


def gccver_to_glibcver(gccver):
    res = parse_gccver(gccver)
    if not res:
        return
    distro, version = res
    logging.info('%r -> %s (%s)', gccver, version, distro)

    if distro == 'alpine':
        return alpine_gccver_to_glibcver(version)

    res = get_timespan('gcc', version, distro)
    if not res:
        return
    t1, t2, distro_release = res

    glibc_vers = versions_in_timespan('glibc', distro, t1, t2, distro_release)

    return distro, distro_release, glibc_vers


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        m = re.search(br'^[^:]*:\s*ELF[^,]*,\s*([^,]+)', subprocess.check_output(['file', filename]))
        if not m:
            continue
        arch = m.group(1).decode('ascii')

        gccvers = set()
        with subprocess.Popen(['strings', filename], stdout=subprocess.PIPE) as p:
            for line in p.stdout:
                line = line.strip()
                if line.startswith(b'GCC:'):
                    gccvers.add(line.decode('ascii'))

        distro_vers = set()
        for gccver in gccvers:
            res = gccver_to_glibcver(gccver)
            if not res:
                continue
            distro, distro_release, vers = res
            for ver in vers:
                distro_vers.add((distro, distro_release, ver))

        if distro_vers:
            print(filename)
            for distro, distro_release, ver in distro_vers:
                print(distro, distro_release, ver, arch)
            print()

