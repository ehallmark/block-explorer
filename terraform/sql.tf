
resource "google_sql_database_instance" "instance" {
  name   = "${var.app_name}-13"
  region = var.region
  database_version = "POSTGRES_13"
  settings {
    tier              = "db-f1-micro"
    disk_autoresize   = true
    ip_configuration {
      require_ssl = false
      ipv4_enabled = true
      authorized_networks {
        value = "0.0.0.0/0"
        name = "allow-all"
      }
    }
  }
  deletion_protection = false
}


resource "google_sql_database" "database" {
  name = var.app_name
  instance = google_sql_database_instance.instance.name
}


resource "google_sql_user" "user" {
  name     = var.sql_user
  instance = google_sql_database_instance.instance.name
  password = var.sql_password
}


