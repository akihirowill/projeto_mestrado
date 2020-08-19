import re


def sig_method(signame):
    if ':' not in signame:
        return signame, None
    return signame.split(':', 1)


def ver_from_signame(signame):
    m = re.search(r'[-_](\d.+?)[._](i.86|x86|x86_64|amd64|powerpc|arm(64|el|hf)?|mips(el)?)$', signame)
    ver = m.group(1)
    m = re.search(r'^(.*?)\.el\d+(_[^_]+)?$', ver)
    if m:
        return m.group(1)
    return ver


def sig_arch(signame):
    if re.search(r'i.86|x86$', signame):
        return 'i386'
    if re.search(r'x86_64|amd64$', signame):
        return 'amd64'
    if re.search(r'powerpc$', signame):
        return 'powerpc'
    if re.search(r'arm64$', signame):
        return 'arm64'
    if re.search(r'arm(el|hf)?$', signame):
        return 'arm32'
    if re.search(r'mips(el)?$', signame):
        return 'mips'
    raise ValueError(signame)
