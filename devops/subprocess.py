""" Deployment dev, using python & subprocess. (Enable hot reloading when changes happens)

"""
# Global import
import os
import signal
from typing import List, Dict, Any
from subprocess import Popen, PIPE, STDOUT
import threading
import time
import psutil


class StdoutListener(threading.Thread):
    def __init__(self, stdout: Any):
        threading.Thread.__init__(self)
        self.stdout = stdout
        self.buffer = []

    def run(self) -> None:
        for msg in iter(self.stdout.readline, b""):
            self.buffer.append(str(msg))


class SubprocessThread(threading.Thread):

    def __init__(
            self, l_args: List[str], key: str, log_color: str, global_var: Dict[str, str] = None
    ):
        threading.Thread.__init__(self)
        self.args = l_args
        self.global_var = global_var or {}
        self.key = key
        self.log_color = log_color
        self.shutdown_flag = threading.Event()

    def log(self, msg: str):
        print(f'{self.log_color}[{self.key}]: {msg}')

    def sigint_handler(self):
        self.log('Ctr(C ignored')

    def run(self) -> None:
        # Launch main sub process
        process = Popen(self.args, stdout=PIPE, stderr=STDOUT, env={**os.environ, **self.global_var})

        # listen to process output in a new thread
        listen_th = StdoutListener(process.stdout)
        listen_th.start()

        # listen to shut down Event
        stop, msg, i, j = False, "", 0, 1
        while not stop:
            # Display log from process if any, otherwise log heart bit
            if len(listen_th.buffer) > i:
                msg = listen_th.buffer[i]
                self.log(msg)
                i += 1
            else:
                j += 1
                if j > 1000:
                    self.log('Process ok')
                    j = 0

            time.sleep(0.1)
            if self.shutdown_flag.is_set():
                # terminating subprocesses
                self.log('Terminating subprocesses ...')
                stop = True
                try:
                    # Kill parent and child process
                    parent = psutil.Process(process.pid)
                    for child_process in parent.children(recursive=True):
                        child_process.send_signal(signal.SIGINT)

                    process.stdout.close()
                    process.send_signal(signal.SIGINT)

                except psutil.NoSuchProcess:
                    return


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass
