from typing import Tuple, Dict, Any
from dotenv import dotenv_values
from pathlib import Path
import yaml
import os


def check_conf_consistency(
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
    # Load dev-python devops config
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
    check_conf_consistency(deploy_conf, auth_conf, front_env)

    return deploy_conf, auth_conf, front_env
