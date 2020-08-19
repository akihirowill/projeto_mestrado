#!/usr/bin/python3
import sys
import re

result = set()

for name in sys.stdin:
    name = name.strip().lstrip('_')
    result.add(name)
    m = re.match(r'^(.*?)_\d+$', name)
    if m:
        result.add(m.group(1))

for name in sorted(result):
    print(name)
