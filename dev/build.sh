#!/bin/bash
# To run from root directory
# Usage: ./dev/build.sh --build

python devops/config.py && \
  export PROJECT_CONFIG="$(cat ./conf/local/dev/auth.yaml)" && \
  export $(cat conf/local/dev/deploy.env | xargs) && \
  export PATH_API=${HOME}${PATH_API} && \
  cp -f ${PATH_API}/deploy-simple/conf/local/dev/front.env ${PATH_API}/front-simple/${FRONT_ENV_PATH} && \
  envsubst '$HOSTNAME $PROTOCOL $AUTH_URI' < ${PATH_API}/deploy-simple/conf/global/dev/nginx-template.conf > \
    ${PATH_API}/nginx-simple/conf/local/nginx.conf && \
  sudo -E docker-compose -f dev/docker-compose.yaml up $1


