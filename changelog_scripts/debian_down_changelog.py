#!/usr/bin/python3
# download debian dir (containing changelog) for latest version of package
import sys
import re
import subprocess
import requests

package = sys.argv[1]

r = requests.get('https://launchpad.net/debian/+source/{}/+changelog'.format(package))
r.raise_for_status()
src_link = re.search(r'<a href="(/debian/\+source/.*?)"', r.text).group(1)
r = requests.get('https://launchpad.net{}'.format(src_link))
r.raise_for_status()
debdir_link = re.search(r'<a class="sprite download" href="(.*?(\.debian\.tar\.xz|\.diff\.gz))"', r.text).group(1)
subprocess.call(['wget', '-c', format(debdir_link)])
