
output "db_user" {
  value = google_sql_user.user.name
}

output "db_password" {
  value = google_sql_user.user.password
}

output "database_ip" {
  value = google_sql_database_instance.instance.public_ip_address
}

output "app_ip" {
  value = google_compute_global_address.ingress_ip.address
}