

resource "kubernetes_namespace" "etl" {
  metadata {
    name = "etl"
  }
}


resource "kubernetes_cron_job" "bsc-explorer" {
  metadata {
    name = "bsc-explorer-ingest"
    namespace = kubernetes_namespace.etl.metadata[0].name
  }

  spec {
    concurrency_policy            = "Forbid"
    failed_jobs_history_limit     = 5
    schedule                      = "*/5 * * * *"
    starting_deadline_seconds     = 10
    successful_jobs_history_limit = 10
    job_template {
      metadata {}
      spec {
        backoff_limit = 3
        template {
          metadata {}
          spec {
            container {
              image = "gcr.io/${var.project_name}/${var.app_name}:latest"
              name = "main"
              command = ["python"]
              args = ["-u", "-m", "etl"]

              env {
                name = "DATABASE_URL"
                value = "postgresql://${google_sql_database_instance.instance.public_ip_address}:5432/${var.app_name}?user=${google_sql_user.user.name}&password=${google_sql_user.user.password}"
              }

              env {
                name = "BSCSCAN_API_KEY"
                value = var.bscscan_api_key
              }

              env {
                name = "ETHERSCAN_API_KEY"
                value = var.etherscan_api_key
              }

              env {
                name = "POLYGONSCAN_API_KEY"
                value = var.polygonscan_api_key
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
            }
          }
        }
      }
    }
  }
}
