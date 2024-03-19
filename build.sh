#!/usr/bin/env bash -eo pipefail

# This is a helper script for building the various examples.
unset source_dir dockerfile_dir

BUILD_TARGET=${1:-"python"}
CONTAINER_BUILD_SYSTEM=${2:-"podman"}
CONTAINER_TAG=${3:-"local"}

source_dir="src/${BUILD_TARGET}"
dockerfile_dir="containers/${BUILD_TARGET}"

# Build the Docker image
build () {
    local working_directory

    working_directory=$(pwd)
    echo "Building the Docker image for the ${BUILD_TARGET} example in ${working_directory}"
    $CONTAINER_BUILD_SYSTEM build \
        -t platform-examples-${BUILD_TARGET}:${CONTAINER_TAG} \
        -f ${dockerfile_dir}/Dockerfile \
        $working_directory
    return $?
}

# Run the build function if the script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Running the build script directly."
    build
fi
