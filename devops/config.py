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
    # Load dev devops config
    print(f'Loading deploy config at {(local_conf_path / "deploy.yaml").as_posix()} ...')
    deploy_conf = yaml.safe_load((local_conf_path / 'deploy.yaml').open())
    deploy_conf['global'].update(
        {k: v.format(HOME=os.environ['HOME']) for k, v in deploy_conf['global'].items()}
    )
    print('[Found]')

    # Load auth project config
    print(f'Trying to find auth config at {Path(deploy_conf["global"]["PATH_API"]) / "auth-simple" } ...')
    pth_auth_conf = Path(deploy_conf['global']['PATH_API']) / 'auth-simple' / 'conf' / 'local' / 'project_config.yaml'
    if pth_auth_conf.exists():
        print("[Found]")
        auth_conf = yaml.safe_load(pth_auth_conf.open())
        deploy_conf['auth-database'] = auth_conf['project-database']

    else:
        print(f"[Not Found]: Taking from {(local_conf_path / 'auth.yaml').as_posix()}")
        auth_conf = yaml.safe_load((local_conf_path / 'auth.yaml').open())

    # Load front env
    print(f'Trying to find front config at {Path(deploy_conf["global"]["PATH_API"]) / "front-simple"} ...')
    pth_front_env = Path(deploy_conf["global"]["PATH_API"]) / 'front-simple' / 'dev.env'
    if pth_front_env.exists():
        front_env = dict(dotenv_values(pth_front_env.as_posix()))
        print("[Found]")

    else:
        print(f"[Not Found]: Taking from {(local_conf_path / 'front.env').as_posix()}")
        front_env = dict(dotenv_values((local_conf_path / 'front.env').as_posix()))

    check_conf_consistency(deploy_conf, auth_conf, front_env)

    return deploy_conf, auth_conf, front_env
