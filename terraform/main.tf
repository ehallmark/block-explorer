terraform {
  required_providers {
  }
}

provider "google" {
  version = "3.49.0"
  project = var.project_name
  region  = var.region
  zone    = var.location
}

provider "kubernetes" {
  version = "~> 1.10.0"
  host    = google_container_cluster.primary.endpoint
  token   = data.google_client_config.current.access_token
  client_certificate = base64decode(
  google_container_cluster.primary.master_auth[0].client_certificate,
  )
  client_key = base64decode(google_container_cluster.primary.master_auth[0].client_key)
  cluster_ca_certificate = base64decode(
  google_container_cluster.primary.master_auth[0].cluster_ca_certificate,
  )
}