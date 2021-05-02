import os
import sys
import json
import select
import logging
import tempfile
import threading
import subprocess
import distutils.spawn

import fs.file_utils
from generator import utils

logger = logging.getLogger(__name__)


class Terraform:

    def __init__(self, tf_path=None):
        self.tf_binary = distutils.spawn.find_executable('terraform') if not tf_path else tf_path

    @staticmethod
    def __gather_env_vars():
        return {utils.remove_prefix(env, 'CLDGEN_TF_').lower(): val for env, val in os.environ.items() if
                env.startswith('CLDGEN_TF')}

    def __call_tf_process(self, params, cwd=None, timeout=180):
        working_dir = os.getcwd() if not cwd else cwd
        arg_list = [self.tf_binary]
        arg_list.extend(params)
        try:
            return (
                True,
                subprocess.check_output(arg_list, stdin=subprocess.DEVNULL, universal_newlines=True, cwd=working_dir,
                                        timeout=timeout))
        except subprocess.CalledProcessError:
            return False, None

    def __run_tf_process(self, params, cwd=None, timeout=180):
        working_dir = os.getcwd() if not cwd else cwd
        arg_list = [self.tf_binary]
        arg_list.extend(params)
        proc = subprocess.Popen(arg_list, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True, cwd=working_dir)
        timer = threading.Timer(timeout, proc.kill)
        try:
            timer.start()
            while True:
                reads = [proc.stdout.fileno(), proc.stderr.fileno()]
                # 5 seconds hardcoded timeout. Seems OK taking into account that we'll retry if proc has not finished
                ret = select.select(reads, [], [], 5 if timeout > timeout else timeout)
                for fd in ret[0]:
                    if fd == proc.stdout.fileno():
                        while proc.poll() is None:
                            read = proc.stdout.readline()
                            # TODO Temp log to stdout
                            sys.stdout.write(read)
                    if fd == proc.stderr.fileno():
                        while proc.poll() is None:
                            read = proc.stderr.readline()
                            # TODO Temp log to stderr
                            sys.stderr.write(read)
                if proc.poll() is not None:
                    ret_code = proc.poll()
                    break
        finally:
            if not timer.is_alive():
                logger.error('TF execution time out')
                ret_code = 1
            timer.cancel()

        logger.debug(f'TF execution finished. Return code {ret_code}')
        return ret_code

    def __run_parametrized_command(self, command, tf_file, vars_files=None, opts=None):
        args_list = [command]
        for var, val in Terraform.__gather_env_vars().items():
            args_list.append(f'-var={var}={val}')

        if vars_files:
            for file in vars_files:
                args_list.append(f'-var-file={file}')
        if opts:
            args_list.extend(opts)
        return self.__run_tf_process(args_list, os.path.dirname(tf_file), timeout=180)

    def plan(self, tf_file, vars_files=None, json_out=False):
        opts = []
        if json:
            fd, filename = tempfile.mkstemp()
            opts = [f'-out={filename}']
        ret_ok = self.__run_parametrized_command('plan', tf_file, vars_files, opts=opts)
        if ret_ok == 0 and json_out:
            show_res, json_capture = self.show(tf_file, filename)
            fs.file_utils.safe_file_delete(filename)
            return show_res, json_capture
        fs.file_utils.safe_file_delete(filename)
        return ret_ok, None

    def apply(self, tf_file, vars_files=None):
        return self.__run_parametrized_command('apply', tf_file, vars_files, opts=['-auto-approve']) == 0

    def destroy(self, tf_file, vars_files=None):
        return self.__run_parametrized_command('destroy', tf_file, vars_files) == 0

    def output(self, tf_file):
        res_ok, result = self.__call_tf_process(['output', '-json'], cwd=os.path.dirname(tf_file), timeout=180)
        return res_ok, json.loads(result) if res_ok and result else None

    def init(self, tf_file, plugins_dir=None):
        command = ['init']
        if plugins_dir:
            command.append(f'----plugin-dir={plugins_dir}')

        res_ok, result = self.__call_tf_process(command, cwd=os.path.dirname(tf_file), timeout=180)
        return res_ok

    def providers_mirror(self, tf_file, plugins_dir):
        res_ok, result = self.__call_tf_process(['providers', 'mirror', plugins_dir], cwd=os.path.dirname(tf_file),
                                                timeout=180)
        return res_ok

    def show(self, tf_file, input_file=None):
        command = ['show', '-json']
        if input_file:
            command.append(input_file)
        res_ok, result = self.__call_tf_process(command, cwd=os.path.dirname(tf_file), timeout=180)
        return res_ok, json.loads(result) if res_ok and result else None
