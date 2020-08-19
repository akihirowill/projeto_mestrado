#!/usr/bin/python3
# download debian dir (containing changelog) from all ubuntu dists
import sys
import re
import subprocess
import traceback
import requests

package = sys.argv[1]
arch = 'amd64'

dists = """
groovy
focal
eoan
disco
cosmic
bionic
artful
zesty
yakkety
xenial
wily
vivid
utopic
trusty
saucy
raring
quantal
precise
oneiric
natty
maverick
lucid
karmic
jaunty
intrepid
hardy
gutsy
feisty
edgy
dapper
breezy
hoary
warty
""".strip().splitlines()

for dist in dists:
    print('downloading for {}...'.format(dist))
    try:
        r = requests.get('https://launchpad.net/ubuntu/{}/{}/{}/'.format(dist, arch, package))
        r.raise_for_status()
        ver_link = re.search(r'<a href="(/ubuntu/{}/{}/{}/.*?)"'.format(re.escape(dist), re.escape(arch), re.escape(package)), r.text).group(1)
        r = requests.get('https://launchpad.net{}'.format(ver_link))
        r.raise_for_status()
        src_link = re.search(r'<a href="(/ubuntu/\+source/.*?)"', r.text).group(1)
        r = requests.get('https://launchpad.net{}'.format(src_link))
        r.raise_for_status()
        debdir_link = re.search(r'<a class="sprite download" href="(.*?(\.debian\.tar\.xz|\.diff\.gz))"', r.text).group(1)
        subprocess.call(['wget', '-c', format(debdir_link)])
    except:
        traceback.print_exc()


