from typing import Tuple, Dict, Any

import dotenv
from dotenv import dotenv_values
from pathlib import Path
import argparse
import yaml
import os


def check_dev_python_conf(
        deploy_conf: Dict[str, Any], auth_conf: Dict[str, Any], front_env: Dict[str, Any]
) -> None:
    """
    """
    # Check consistency between auth_conf and devops conf
    for k in ['hostname', 'port', 'name', 'user', 'password']:
        try:
            assert deploy_conf['auth-database'][k] == auth_conf['project-database'][k]
        except AssertionError:
            print(f'deploy_conf:auth-database differs from auth_conf:project-database differs on key {k}')

    # Check consistency between auth_conf and front_env
    url_auth_conf = f"{auth_conf['project']['protocol']}://{auth_conf['project']['hostname']}" \
        f":{auth_conf['project']['port']}/"
    try:
        assert front_env['AUTH_URL'] == url_auth_conf
    except AssertionError:
        print(f"Auth service URL doesn't match wht front config auth url: {url_auth_conf} != {front_env['AUTH_URL']}")


def get_config(local_conf_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """

    """
    # Load dev-python-python devops config
    print(f'Loading deploy config at {(local_conf_path / "deploy.yaml").as_posix()} ...')
    deploy_conf = yaml.safe_load((local_conf_path / 'deploy.yaml').open())
    deploy_conf['global'].update(
        {k: v.format(HOME=os.environ['HOME']) for k, v in deploy_conf['global'].items()}
    )

    # Load auth project config
    print(f'Loading auth config at {local_conf_path / "auth.yaml" } ...')
    auth_conf = yaml.safe_load((local_conf_path / 'auth.yaml').open())

    # Load front env
    print(f'Loading auth config at {local_conf_path / "front.env"} ...')
    front_env = dict(dotenv_values((local_conf_path / 'front.env').as_posix()))

    # Check if everything is ok with config
    check_dev_python_conf(deploy_conf, auth_conf, front_env)

    return deploy_conf, auth_conf, front_env


def check_conf(path_conf: Path) -> None:
    # Load conf:
    d_auth = yaml.safe_load((path_conf / 'auth.yaml').open())
    d_deploy = dict(dotenv_values(path_conf / 'deploy.env'))
    d_front = dict(dotenv_values(path_conf / 'front.env'))

    # Check consistency between auth & deploy conf
    for k, l in [
        ('POSTGRES_PORT', 'port'), ('POSTGRES_DB', 'name'), ('POSTGRES_USER', 'user'),
        ('POSTGRES_PASSWORD', 'password')
    ]:
        try:
            assert d_deploy[k] == d_auth['project-database'][l]
        except AssertionError:
            raise ValueError(f'deploy conf and  auth conf differs on auth database on key {k}')

    for k, l in [('HOSTNAME', 'hostname'), ('PROTOCOL', 'protocol'), ('AUTH_PORT', 'port')]:
        try:
            assert str(d_deploy[k]) == str(d_auth['project'][l])
        except AssertionError:
            raise ValueError(f'deploy conf and  auth conf differs on auth {k}')

    # Check consistency between front conf & (auth, deploy) conf
    url_auth = f"{d_auth['project']['protocol']}://{d_auth['project']['hostname']}{d_deploy['AUTH_URI']}/"
    try:
        assert d_front['AUTH_URL'] == url_auth
    except AssertionError:
        raise ValueError(
            f"Auth service URL doesn't match with front config auth url: "
            f"{url_auth} != {d_front['AUTH_URL']}"
        )
    try:
        assert d_front['PORT'] == d_deploy['FRONT_PORT']
    except AssertionError:
        raise ValueError(
            f"Front port from front and deploy env differs {d_front['PORT']} != {d_deploy['FRONT_PORT']}"
        )


class CheckConfigArgParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(description="Arg parser for Heka task updating.")
        self.add_argument(
            "--path",
            metavar="path",
            default="conf/local/dev",
            type=str,
            help="path to config dir to check",
        )


if __name__ == '__main__':
    # get args
    args = CheckConfigArgParser().parse_args()

    # Set paths
    project_path = Path(__file__).parent.parent
    conf_path = project_path / args.path

    # Check conf
    check_conf(conf_path)

