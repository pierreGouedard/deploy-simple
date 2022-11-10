#!/bin/bash
# To run from root directory
# Usage: ./dev/build.sh --build
export PROJECT_CONFIG="$(cat ./conf/local/dev/auth.yaml)" && \
  export $(cat conf/local/dev/deploy.env | xargs) && \
  export PATH_API=${HOME}/${PATH_API} && \
  export FRONT_ENV_PATH=${PATH_API}/front-simple/envs/dckr-cmps.env && \
  cp -f ${PATH_API}/deploy-simple/conf/local/dev/front.env ${PATH_API}/front-simple/envs/dckr-cmps.env
  sudo -E docker-compose -f dev/docker-compose.yaml up $1


