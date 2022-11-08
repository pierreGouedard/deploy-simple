#!/bin/bash
# Usage:  ./scripts/run_test.sh build,run,stop,clean
# arg1 comma separated lit of action arg2 args for pytest run
# ./tests/run_test.sh stop,clean,build
set -e

IFS=',' read -r -a action_array <<< "$1"

# Docker compose up lol