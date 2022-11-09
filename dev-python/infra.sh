#!/bin/bash
# Usage:  ./infra.sh build,clean,pgadmin
set -e

IFS=',' read -r -a action_array <<< "$1"

run(){
  case $1 in

      build)
        sudo docker pull postgres && \
          sudo docker run -d --name postgresql -e POSTGRES_USER=$2 -e POSTGRES_PASSWORD="${3}" \
          -p $4:$4 -v ${HOME}/postgres-data/:/var/lib/postgresql/data -d postgres
        ;;

      pgadmin)
        source ${HOME}/pgadmin4/bin/activate && pgadmin4 -d
        ;;

      clean)
          sudo docker stop postgresql ; \
            sudo docker container rm postgresql ;  \
            sudo rm -rf ${HOME}/postgres-data/
          ;;

      *)
      echo "Action not recognize. Action authorized: build,clean,pgadmin"
      ;;
  esac
}

for action in ${action_array[@]};
do
  run $action $2 $3 $4 || true
done

