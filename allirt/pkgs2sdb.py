import os
import sys
import logging
from sdb import Sdb, FlairNotSupportedError
import multiprocessing

logging.basicConfig(level=logging.INFO)

sdb = Sdb(flair='/usr/bin')

sig_dir_name = '../../sigs/sdb'


def do_sig(deb_path):
    sig_desc = os.path.splitext(os.path.basename(deb_path))[0]
    sig_name = '{}.sdb'.format(sig_desc)
    sig_name = os.path.join(sig_dir_name, sig_name)

    try:
        logging.info('Processing {}'.format(deb_path))
        if deb_path.endswith('.apk'):
            info = sdb.deb_to_sig(deb_path, 'libc.musl-*.so.1', sig_name, sig_desc)
        else:
            info = sdb.deb_to_sig(deb_path, 'libc.so.6', sig_name, sig_desc)
        logging.info('Target library : {}'.format(info['a']))
        logging.info('Signature has been generated. -> {}'.format(info['sig']))
    except FlairNotSupportedError:
        logging.exception('FlairNotSupportedError for {}'.format(deb_path))
    except FileExistsError:
        pass


def main():
    p = multiprocessing.Pool()
    p.map(do_sig, sys.argv[1:])


if __name__ == '__main__':
    main()
