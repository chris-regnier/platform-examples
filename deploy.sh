#!/usr/bin/env bash -eo pipefail

# This is a helper script for deploying the various examples.

unset deployment_dir current_context

DEPLOYMENT_TARGET=${1:-"python"}
CONTAINER_ORCHESTRATION_SYSTEM=${2:-"kubernetes"}
CONTAINER_ORCHESTRATION_FLAVOR=${3:-"kind"}
CONTAINER_TAG=${4:-"local"}

current_context=$(kubectl config current-context)
current_context=${current_context/kind-/""}

load_image() {
    echo "Loading the Docker image for the ${DEPLOYMENT_TARGET} example in ${current_context}"
    podman image save localhost/platform-examples-${DEPLOYMENT_TARGET}:${CONTAINER_TAG} -o /tmp/platform-examples-${DEPLOYMENT_TARGET}-${CONTAINER_TAG}.tar
    kind load image-archive -n ${current_context} /tmp/platform-examples-${DEPLOYMENT_TARGET}-${CONTAINER_TAG}.tar
    rm /tmp/platform-examples-${DEPLOYMENT_TARGET}-${CONTAINER_TAG}.tar
    return $?
}

deploy() {
    local working_directory

    working_directory=$(pwd)
    echo "Deploying the ${DEPLOYMENT_TARGET} example in ${working_directory} using ${CONTAINER_ORCHESTRATION_SYSTEM} and ${CONTAINER_ORCHESTRATION_FLAVOR}"
    if [[ "${CONTAINER_ORCHESTRATION_SYSTEM}" == "kubernetes" ]]; then
        if [[ "${CONTAINER_ORCHESTRATION_FLAVOR}" == "kind" ]]; then
            kubectl apply -f ${working_directory}/deployments/${DEPLOYMENT_TARGET}/manifests.yaml
        fi
    fi
    return $?
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Running the deploy script directly."
    load_image
    deploy
fi