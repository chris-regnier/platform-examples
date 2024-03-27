output "deployment_name" {
  value = kubernetes_deployment.deployment.metadata.0.name
}

output "namespace_name" {
  value = kubernetes_namespace.namespace.metadata.0.name
}

output "service_name" {
  value = kubernetes_service.service.metadata.0.name
}