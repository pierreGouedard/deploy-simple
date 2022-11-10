""" Deployment dev-python-python, using python & subprocess.
 Enable to choose whihc service to deploy

"""
# Global import
import time
import sys
import signal

import yaml
from colorama import Fore
from pathlib import Path
import argparse

# Local import
project_path = Path(__file__).parent.parent
sys.path.append(project_path.as_posix())
from devops.config import get_config
from devops.subprocess import SubprocessThread, ServiceExit
from devops.temp import Temp


class DeployArgParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(description="Arg parser for Heka task updating.")
        self.add_argument(
            "--services",
            metavar="services",
            default="front,auth",
            type=str,
            help="comma separated list of services to run.",
        )


def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit


# Choose which service to build.

if __name__ == '__main__':
    # Get args
    args = DeployArgParser().parse_args()

    # Get project path and load (if any) dev-python env
    local_conf_path = project_path / "conf" / "local" / "dev-python"
    deploy_conf, auth_conf, front_env = get_config(local_conf_path)

    # Write merged conf files to tmp dir.
    tmp_dir = Temp('simple_', is_dir=True)
    with (tmp_dir.path / 'front.env').open('w') as f:
        for k, v in front_env.items():
            f.write(f"{k}={v}\n")
    yaml.dump(auth_conf, (tmp_dir.path / 'auth.yaml').open('w'))

    if 'auth' in args.services:
        # clean auth DB pg and rebuild it.
        infra_th = SubprocessThread(
            [
                './dev-python-python/infra.sh', 'clean,build,pgadmin', deploy_conf['auth-database']['user'],
                deploy_conf['auth-database']['password'], deploy_conf['auth-database']['port']
            ], 'INFRA', Fore.GREEN
        )

        # Auth service thread.
        auth_th = SubprocessThread(
            ['./dev-python-python/services.sh', 'start-auth', tmp_dir.path.as_posix()], 'AUTH', Fore.BLUE, deploy_conf['global']
        )

    if 'front' in args.services:
        # Front server thread.
        front_th = SubprocessThread(
            ['./dev-python-python/services.sh', 'start-front', tmp_dir.path.as_posix()], 'FRONT', Fore.RED, deploy_conf['global']
        )

    # Register the signal handlers to terminate nicely threads
    signal.signal(signal.SIGTERM, service_shutdown)  # SIGTERM
    signal.signal(signal.SIGINT, service_shutdown)  # Ctrl-C

    try:
        if 'auth' in args.services:
            infra_th.start()
            time.sleep(15)
            auth_th.start()
            time.sleep(5)

        if 'front' in args.services:
            front_th.start()

        while True:
            time.sleep(1)

    except ServiceExit:
        # Terminate the running threads.
        if 'auth' in args.services:
            infra_th.shutdown_flag.set()
            auth_th.shutdown_flag.set()
        if 'front' in args.services:
            front_th.shutdown_flag.set()

        # Wait for the threads to close...
        if 'auth' in args.services:
            infra_th.join()
            auth_th.join()
        if 'front' in args.services:
            front_th.join()

        # Clean infra
        if 'auth' in args.services:
            infra_th = SubprocessThread(
                [
                    './dev-python-python/infra.sh', 'clean', deploy_conf['auth-database']['user'],
                    deploy_conf['auth-database']['password'], deploy_conf['auth-database']['port']
                ], 'INFRA', Fore.GREEN,
            )
            infra_th.start()
            infra_th.shutdown_flag.set()
            infra_th.join()

        # Remove tmp config.
        tmp_dir.remove()

    print('Exiting main program')
