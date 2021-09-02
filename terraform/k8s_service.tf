
resource "kubernetes_namespace" "service" {
  metadata {
    name = "service"
  }
}


resource "kubernetes_ingress" "bsc_explorer" {
  metadata {
    name=var.app_name
    namespace=kubernetes_namespace.service.metadata[0].name
    annotations = {
      "kubernetes.io/ingress.global-static-ip-name" = google_compute_global_address.ingress_ip.name
      "ingress.gcp.kubernetes.io/pre-shared-cert" = google_compute_managed_ssl_certificate.managed_certificate.name
    }
  }

  spec {
    backend {
      service_name = kubernetes_service.bsc_explorer.metadata[0].name
      service_port = kubernetes_service.bsc_explorer.spec[0].port[0].port
    }

    rule {
      host = var.domain
      http {
        path {
          path = "/*"
          backend {
            service_name = kubernetes_service.bsc_explorer.metadata[0].name
            service_port = kubernetes_service.bsc_explorer.spec[0].port[0].port
          }
        }
      }
    }
  }
}


resource "kubernetes_service" "bsc_explorer" {
  metadata {
    namespace = kubernetes_namespace.service.metadata[0].name
    name      = var.app_name
  }

  spec {
    selector = {
      run = var.app_name
    }

    port {
      protocol    = "TCP"
      port        = 5000
      target_port = 5000
    }

    type = "NodePort"
  }
}

resource "kubernetes_deployment" "bsc_explorer" {
  metadata {
    name      = var.app_name
    namespace = kubernetes_namespace.service.metadata[0].name

    labels = {
      run = var.app_name
    }
  }

  spec {
    replicas = 2
    selector {
      match_labels = {
        run = var.app_name
      }
    }

    template {
      metadata {
        name      = var.app_name
        namespace = kubernetes_namespace.service.metadata[0].name

        labels = {
          run = var.app_name
        }
      }

      spec {
        container {
          image = "gcr.io/${var.project_name}/${var.app_name}:latest"
          name = "main"
          command = ["gunicorn"]
          args = ["-b", "0.0.0.0:5000", "service.server:app"]

          env {
            name = "DATABASE_URL"
            value = "postgresql://${google_sql_database_instance.instance.public_ip_address}:5432/${var.app_name}?user=${google_sql_user.user.name}&password=${google_sql_user.user.password}"
          }

          env {
            name = "ACCOUNT_ID"
            value = var.account_id
          }

          resources {
            requests {
              cpu = 0.2
              memory = "150Mi"
            }
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = kubernetes_service.bsc_explorer.spec[0].port[0].target_port
            }
            initial_delay_seconds = 3
            period_seconds        = 3
          }
          liveness_probe {
            http_get {
              path = "/health"
              port = kubernetes_service.bsc_explorer.spec[0].port[0].target_port
            }
            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }
      }
    }
  }
}