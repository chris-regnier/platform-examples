provider "kubernetes" {
    config_path = "~/.kube/config"
    config_context = "kind-kind-ingress"
}

module "kubernetes_deployment" {
  source = "../../../../deployments/opentofu/modules/kubernetes"
}