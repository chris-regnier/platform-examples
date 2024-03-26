resource "kubernetes_namespace" "namespace" {
    metadata {
        name = var.namespace
    }
}

resource "kubernetes_service" "service" {
    metadata {
        name      = var.application_name
        namespace = kubernetes_namespace.namespace.metadata.0.name
    }

    spec {
        selector = {
            app = var.application_name
        }

        port {
            port        = var.service_port
            target_port = var.service_port
        }
    }
}

resource "kubernetes_persistent_volume_claim" "local_volume" {
    count = var.use_local_volume ? 1 : 0

    metadata {
        name      = "${var.application_name}-pvc"
        namespace = kubernetes_namespace.namespace.metadata.0.name
        annotations = {"volumeType" = "local"}
    }
    spec {
        access_modes = ["ReadWriteOnce"]
        resources {
            requests = {
                storage = "${var.local_volume_size}Gi"
            }
        }
    }

}

resource "kubernetes_deployment" "deployment" {
    metadata {
        name      = var.application_name
        namespace = kubernetes_namespace.namespace.metadata.0.name
    }

    spec {
        replicas = var.application_replicas

        selector {
            match_labels = {
                app = var.application_name
            }
        }

        template {
            metadata {
                labels = {
                    app = var.application_name
                }
            }

            spec {
                security_context {
                    run_as_user = var.application_user_id
                    run_as_group = var.application_user_id
                    fs_group = var.application_user_id
                }
                dynamic "init_container" {
                    for_each = var.use_local_volume ? [1] : []
                    content {
                        name  = "${var.application_name}-data-init"
                        image = "busybox"
                        command = ["sh", "-c", "mkdir -p /data && chown -R ${var.application_user_id}:${var.application_user_id} /data"]
                        volume_mount {
                            name       = kubernetes_persistent_volume_claim.local_volume[0].metadata.0.name
                            mount_path = "/data"
                        }
                    }
                }
                container {
                    name  = var.application_name
                    image = "${var.application_image_repository}:${var.application_image_tag}"
                    dynamic "volume_mount" {
                        for_each = var.use_local_volume ? [1] : []
                        content {
                            name       = kubernetes_persistent_volume_claim.local_volume[0].metadata.0.name
                            mount_path = "/data"
                        }
                    }
                    port {
                        container_port = var.service_port
                    }
                    security_context {
                        run_as_user = 0
                        allow_privilege_escalation = false
                    }
                    env {
                        name = "DATABASE_URL"
                        value = "sqlite+aiosqlite:////data/db.sqlite3"
                    }

                }
            }
        }
    }
}

resource "kubernetes_ingress" "ingress" {
    count = var.deploy_ingress ? 1 : 0

    metadata {
        name      = "${var.application_name}-ingress"
        namespace = kubernetes_namespace.namespace.metadata.0.name
    }

    spec {
        ingress_class_name = "contour"
        rule {
            host = "${var.application_name}.local"
            http {
                path {
                    path = "/"
                    backend {
                        service_name = kubernetes_service.service.metadata.0.name
                        service_port = kubernetes_service.service.spec.0.port.0.port
                    }
                }
            }
        }
    }
}
