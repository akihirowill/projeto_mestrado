import glob
import os
import subprocess
import sys
from tempfile import TemporaryDirectory

from flair import *


class Sdb(Flair):
    def make_sig(self, lib_name, sig_name, sig_desc='', is_compress=True):
        if os.path.exists(sig_name):
            raise FileExistsError(sig_name)

        sig = sig_name

        flair_dir = self._dir_names['flair']
        rasign2 = os.path.join(flair_dir, 'rasign2')
        if not os.path.exists(rasign2):
            raise FlairUtilNotFoundError('rasign2 util not found. check your flair directory.')

        args = [rasign2, '-a', '-o', sig, lib_name]
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        unused, err = process.communicate()
        exit_code = process.wait()
        if exit_code != 0:
            sys.stderr.buffer.write(err)
            raise FlairError('rasign2: Unknown Error')

        return True

    def _extract_deb(self, deb_name, out_name):
        extract_archive(deb_name, outdir=out_name, verbosity=-1)
        if not os.path.exists(os.path.join(out_name, 'lib')) and not os.path.exists(os.path.join(out_name, 'lib64')): #data.tar extracted
            data = os.path.join(out_name, self._FILE_NAMES['data'])
            extract_archive(data, outdir=out_name, verbosity=-1)
            if not os.path.exists(data): #deb extract not working
                args = ['ar','x', deb_name, self._FILE_NAMES['data_gz']]
                subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                data = os.path.join(out_name, self._FILE_NAMES['data_gz'])
                if not os.path.exists(self._FILE_NAMES['data_gz']):
                    raise FlairError('deb: Extract error')
                os.rename(self._FILE_NAMES['data_gz'], data)
        return True

    @staticmethod
    def single_glob(pattern):
        res = glob.glob(pattern)
        if len(res) > 1:
            raise FlairError('multiple matches for %r' % pattern)
        return res[0] if res else None

    def _extract_a(self, deb_name, so_name, out_name): #deb -> extract -> copy .so
        if os.path.exists(out_name):
            raise FileExistsError(out_name)

        with TemporaryDirectory() as temp:
            self._extract_deb(deb_name, temp)
            lib = os.path.join(temp, 'lib')
            if not os.path.exists(lib):
                lib = os.path.join(temp, 'lib64')
            so = self.single_glob(os.path.join(lib, so_name))
            if not so: #libc.so not exists in ./lib
                platforms = list(filter(lambda x: os.path.isdir(os.path.join(lib, x)), os.listdir(lib)))
                if len(platforms) >= 1:
                    if len(platforms) != 1:
                        self._logger.warning('warning: multi platforms found')

                    platform = ''
                    for relative_dir, dirs, filenames in os.walk(lib):
                        for filename in filenames:
                            if filename == so_name:
                                platform = relative_dir
                                break
                    if platform == '':
                        raise FlairError('deb: Platform not found')
                    so = self.single_glob(os.path.join(lib, platform, so_name))
                else:
                    raise FlairError('deb: Platform not found')
            so = os.path.realpath(so)
            os.rename(so, out_name)
            so_lib_path = so.replace(temp, '.')
        return so_lib_path