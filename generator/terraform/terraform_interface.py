import distutils.spawn
import select
import subprocess
import logging
import os
import sys
import threading

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
                            #TODO Temp log to stdout
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
        return ret_code == 0

    def plan(self, tf_file, vars_files=None):
        args_list = ['plan']
        for var, val in Terraform.__gather_env_vars().items():
            args_list.append(f'-var={var}={val}')
        args_list.append('-var-file=/home/pablintino/Sources/k8s/terraform/config.tfvars')
        self.__call_tf_process(args_list, os.path.dirname(tf_file), timeout=180)
