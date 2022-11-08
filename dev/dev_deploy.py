""" Deployment dev, using python & subprocess. (Enable hot reloading when changes happens)

"""
# Global import
import time
import sys
import signal

import yaml
from colorama import Fore
from pathlib import Path

# Local import
project_path = Path(__file__).parent.parent
sys.path.append(project_path.as_posix())
from devops.config import get_config
from devops.subprocess import SubprocessThread, ServiceExit
from devops.temp import Temp


def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit


if __name__ == '__main__':

    # Get project path and load (if any) dev env
    local_conf_path = project_path / "conf" / "local" / "dev"
    deploy_conf, auth_conf, front_env = get_config(local_conf_path)

    # Write merged conf files to tmp dir.
    tmp_dir = Temp('simple_', is_dir=True)
    with (tmp_dir.path / 'front.env').open('w') as f:
        for k, v in front_env.items():
            f.write(f"{k}={v}\n")
    yaml.dump(auth_conf, (tmp_dir.path / 'auth.yaml').open('w'))

    # 1. clean pg and rebuild it.
    infra_th = SubprocessThread(
        [
            './dev/infra.sh', 'clean,build,pgadmin', deploy_conf['auth-database']['user'],
            deploy_conf['auth-database']['password'], deploy_conf['auth-database']['port']
        ], 'INFRA', Fore.GREEN
    )

    # 2. launch auth service.
    auth_th = SubprocessThread(
        ['./dev/services.sh', 'start-auth', tmp_dir.path.as_posix()], 'AUTH', Fore.BLUE, deploy_conf['global']
    )

    # 3. Launch front server.
    front_th = SubprocessThread(
        ['./dev/services.sh', 'start-front', tmp_dir.path.as_posix()], 'FRONT', Fore.RED, deploy_conf['global']
    )

    # Register the signal handlers to terminate nicely threads
    signal.signal(signal.SIGTERM, service_shutdown)  # SIGTERM
    signal.signal(signal.SIGINT, service_shutdown)  # Ctrl-C

    time.sleep(10)
    try:
        infra_th.start()
        time.sleep(15)
        auth_th.start()
        time.sleep(5)
        front_th.start()

        while True:
            time.sleep(1)

    except ServiceExit:
        # Terminate the running threads.
        infra_th.shutdown_flag.set()
        auth_th.shutdown_flag.set()
        front_th.shutdown_flag.set()

        # Wait for the threads to close...
        infra_th.join()
        auth_th.join()
        front_th.join()

        # Clean infra
        infra_th = SubprocessThread(
            [
                './dev/infra.sh', 'clean', deploy_conf['auth-database']['user'],
                deploy_conf['auth-database']['password'], deploy_conf['auth-database']['port']
            ], 'INFRA', Fore.GREEN,
        )
        infra_th.start()
        infra_th.shutdown_flag.set()
        infra_th.join()

        # Remove tmp config.
        tmp_dir.remove()

    print('Exiting main program')
