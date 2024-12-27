#!/bin/sh
set -e

if [ -t 1 ] ; then
    TTY_ENV_ARGS="-e LINES=$(tput lines) -e COLUMNS=$(tput cols)"
else
    TTY_ENV_ARGS=""
fi

SERVICE_NAME="@PROJECT-dev"
if ! [ $# -eq 0 ] ; then
    if [ "$1" = "--amd64" ] ; then
        SERVICE_NAME="$SERVICE_NAME-amd64"
        shift
    fi
fi

CONTAINER_ID=$(docker-compose -f 'docker/compose.yml' ps -q "$SERVICE_NAME")
if [ -z "$CONTAINER_ID" ] ; then
    echo "$SERVICE_NAME not running" 1>&2
    exit 1
fi

if [ -z "$DOCKER_HOST_PLATFORM" ] ; then
    if [ $(uname) = "Linux" ] ; then
        DOCKER_HOST_PLATFORM=linux
    elif [ $(uname) = "Darwin" ] ; then
        DOCKER_HOST_PLATFORM=darwin
    fi
fi

exec docker exec \
    $TTY_ENV_ARGS \
    -e DOCKER_HOST_PLATFORM="$DOCKER_HOST_PLATFORM" \
    --privileged \
    --detach-keys 'ctrl-o,ctrl-d' \
    -it "$CONTAINER_ID" \
    "$@"
