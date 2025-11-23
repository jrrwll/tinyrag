#!/usr/bin/env bash

set -e
set -x

DOCKER_REGISTRY=jerrywill
VERSION=latest

ROOT_DIR=$(cd "$(dirname $0)" && cd .. && pwd -P)

docker build -f docker/Dockerfile -t $DOCKER_REGISTRY/tinyrag:$VERSION "$ROOT_DIR"
