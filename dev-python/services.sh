#!/bin/bash
# Usage:  ./services.sh start-auth,start-front /home/api-simple/ /tmp/config
# Require that a conda env has been set before and is actionable from terminal
set -e

IFS=',' read -r -a action_array <<< "$1"


run(){

  case $1 in
      start-auth)
        cd $PATH_API/auth-simple && \
          export PROJECT_CONFIG="$(cat $2/auth.yaml)" && \
          source $CONDA_BIN_ACTIVATE auth-env && \
          python wsgi.py
        ;;

      # Write dev-python-python.env in folder
      start-front)
        cd $PATH_API/front-simple && \
          source $CONDA_BIN_ACTIVATE front-env && \
          cp -f $2/front.env $PATH_API/front-simple/envs/dev-python.env && \
          export ENV_PATH=envs/dev-python.env
          npm run devwebpack
        ;;

      *)
      echo "Action not recognize. Action authorized: start-auth,start-front"
      ;;
  esac
}

for action in ${action_array[@]};
do
  run $action $2
done

