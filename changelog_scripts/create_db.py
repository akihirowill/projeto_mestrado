#!/usr/bin/python3
# create database of versions
import sqlite3
import tarfile
import gzip
import os
import re
import traceback
from subprocess import Popen, PIPE
from datetime import datetime


conn = sqlite3.connect('versions.db')
c = conn.cursor()
c.executescript("""
CREATE TABLE IF NOT EXISTS versions (
  package text not null,
  version text not null,
  timestamp int not null,
  distro text not null,
  distro_release text,
  UNIQUE (package, version, timestamp, distro, distro_release)
);
""")


def insert_row(package, version, timestamp, distro, distro_release=None):
    c.execute('INSERT OR REPLACE INTO versions (package, version, timestamp, distro, distro_release) VALUES (?, ?, ?, ?, ?)',
              (package, version, timestamp, distro, distro_release))


def debian_changelog_readlines(filename):
    if filename.endswith('.diff.gz'):
        with gzip.open(filename) as gzf:
            state_in = False
            for line in gzf:
                if state_in:
                    if line.startswith(b'---'):
                        state_in = False
                        break
                    elif line.startswith(b'+'):
                        yield line[1:]
                else:
                    if line.startswith(b'+++') and line.endswith(b'/debian/changelog\n'):
                        state_in = True
    else:
        with tarfile.open(filename) as tarf:
            for line in tarf.extractfile('debian/changelog'):
                yield line


def redhat_changelog_readlines(filename):
    with Popen(['rpm', '-q', '--changelog', '-p', filename], stdout=PIPE, env={'LC_ALL': 'C'}) as p:
        for line in p.stdout:
            yield line


def debian_changelog_process(filename, ignore_distro_release=True):
    for line in debian_changelog_readlines(filename):
        m = re.search(br'^[^ ]+ \(([^)]+)\) ([^;]+)', line)
        if m:
            version, rel = m.groups()
            if ignore_distro_release:
                distro_releases = [None]
            else:
                distro_releases = rel.split()
        m = re.search(br'^ -- [^>]+>\s+(.+)', line)
        if m:
            timestr, = m.groups()
            try:
                timestamp = datetime.strptime(timestr.decode('ascii'),
                                              '%a, %d %b %Y %H:%M:%S %z').timestamp()
            except:
                traceback.print_exc()
            for distro_release in distro_releases:
                if isinstance(distro_release, bytes):
                    distro_release = re.sub(br'-.*', b'', distro_release)  # remove -proposed, -updates, -security, etc.
                yield version.decode('ascii'), timestamp, distro_release and distro_release.decode('ascii')


def redhat_changelog_process(filename):
    for line in redhat_changelog_readlines(filename):
        m = re.search(br'^\* ([^ ]+ [^ ]+ [^ ]+ [^ ]+) [^>]+>\s+-?\s*(.+)', line)
        if m:
            timestr, version = m.groups()
            timestamp = datetime.strptime(timestr.decode('ascii'),
                                          '%a %b %d %Y').timestamp()
            yield version.decode('ascii'), timestamp


def list_dir(distro, package):
    path = os.path.join(distro, package)
    for filename in os.listdir(path):
        yield os.path.join(path, filename)


for package in 'glibc', 'gcc':
    distro = 'debian'
    for filename in list_dir(distro, package):
        for version, timestamp, distro_release in debian_changelog_process(filename):
            insert_row(package, version, timestamp, distro, distro_release)

    distro = 'ubuntu'
    for filename in list_dir(distro, package):
        for version, timestamp, distro_release in debian_changelog_process(filename, ignore_distro_release=False):
            insert_row(package, version, timestamp, distro, distro_release)

    distro = 'centos'
    for filename in list_dir(distro, package):
        distro_release = re.search('el\d', filename).group(0)
        for version, timestamp in redhat_changelog_process(filename):
            insert_row(package, version, timestamp, distro, distro_release)


conn.commit()
