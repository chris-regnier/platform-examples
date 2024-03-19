# Setting up Kubernetes

## Installing kubectl

`kubectl` is the command line utilty for Kubernetes. You can install it with brew:

```shell
brew install kubectl
```

## Installing kind

I like using [KinD](https://kind.sigs.k8s.io/) to run Kubernetes inside containers. You may see a button at the bottom of Podman Desktop that looks like a warning sign next to the word kind; clicking this button will prompt you to install the KinD binary on your machine.

Podman desktop has a wizard for configuring a cluster with Ingress, too, which is fantastic and saves a lot of research and manual configuration. Simply navigate to Settings > Resources and KinD should be the third option you see. Clicking `Create new ...` will open up a wizard for configuration. The defaults are reasonable.

You can confirm the Kubernetes installation is up and active by using `kubectl`:

```shell
kubectl get all
# there might be a service here
kubectl get namespaces
# should be the stock namespaces and ``projectcontour'' if you enabled ingress
```
