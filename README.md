# Platform Examples

Herein lies resources and assets for working with various platforms.

This repository is intended to be used as reference, both personally and professionally.

## Getting Started

Make sure that you have this project's dependencies installed (see [containers](./containers/README.md), [kubernetes](./kubernetes/README.md), and [src/python](./src/python/README.md))

- Python (3.12 or better), consider using [pyenv](https://github.com/pyenv/pyenv-installer)
- [Podman Desktop](https://podman-desktop.io/) or Docker
- [KinD](https://kind.sigs.k8s.io/)


## Building

You can use the provider build helper script to build the Python project as a container:

```
./build.sh
```

## Running

After you have built the container, you can run interactively against your local code, mounted into the container for a hermetic environment:

```
./run.sh
```

## Deploying

To deploy using Kubernetes, have a local KinD cluster running with [Ingress from Contour configured](https://projectcontour.io/docs/1.28/guides/kind/)

```
./deploy.sh
```
