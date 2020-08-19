import os
import sys
import logging
from flair import Flair, FlairNotSupportedError, FlairError


logging.basicConfig(level=logging.INFO)

flair = Flair('../flair70/bin/linux')

sig_dir_name = '../../sigs/flair'

for deb_path in sys.argv[1:]:
    sig_desc = os.path.splitext(os.path.basename(deb_path))[0]
    sig_name = '{}.sig'.format(sig_desc)
    sig_name = os.path.join(sig_dir_name, sig_name)

    try:
        logging.info('Processing {}'.format(deb_path))
        info = flair.deb_to_sig(deb_path, 'libc.a', sig_name, sig_desc, is_compress=True)
        logging.info('Target library : {}'.format(info['a']))
        logging.info('Signature has been generated. -> {}'.format(info['sig']))
    except FlairNotSupportedError:
        logging.exception('FlairNotSupportedError for {}'.format(deb_path))
    except FileExistsError:
        pass
