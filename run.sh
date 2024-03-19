#!/usr/bin/env bash -eo pipefail

# Use this script to run the application in a container, reloading the container when the source code changes.

BUILD_TARGET=${1:-"python"}
CONTAINER_TAG=${3:-"local"}

source ./build.sh

run_interactive() {
  podman run -it --rm \
    -p 8000:8000 \
    -v $(pwd)/src:/app/src:rw \
    -v $(pwd)/local.sqlite:/app/local.sqlite:rw \
    platform-examples-${BUILD_TARGET}:${CONTAINER_TAG} \
    python -m src.python --host "0.0.0.0" --reload
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Building the Docker image for the ${BUILD_TARGET} example."
    build
    echo "Running the run script directly."
    run_interactive
fi
