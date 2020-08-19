import re


_well_known_synonyms = {
    'IO_getc': 'fgetc',
    'IO_putc': 'fputc',
    'llseek': 'lseek64',
}
for k, v in list(_well_known_synonyms.items()):
    _well_known_synonyms[v] = k


def _fuzzy_match_1(name, symbols):
    if name in symbols:
        return name
    # try to remove a trailing optimization suffix
    for suffix in '_x86', '_ia32', '_sse2':
        if name.endswith(suffix) and name[:-len(suffix)] in symbols:
            return name[:-len(suffix)]
    # try to match a synonym
    n = _well_known_synonyms.get(name)
    if n in symbols:
        return n


def _fuzzy_match_0(name, symbols):
    n = _fuzzy_match_1(name, symbols)
    if n:
        return n
    # try to add a 'libc_' prefix
    return _fuzzy_match_1('libc_' + name, symbols)


def fuzzy_match(name, symbols):
    n = _fuzzy_match_0(name, symbols)
    if n:
        return n
    # try to remove a trailing _number
    m = re.match(r'^(.*?)_\d+$', name)
    return m and _fuzzy_match_0(m.group(1), symbols)
