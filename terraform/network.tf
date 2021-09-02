
resource "google_compute_network" "default" {
  name                    = var.app_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "default" {
  name                     = var.app_name
  ip_cidr_range            = "10.168.0.0/20"  // Change as per your region/zone (https://cloud.google.com/vpc/docs/vpc#ip-ranges)
  network                  = google_compute_network.default.self_link
  region                   = var.region
  private_ip_google_access = true
}

// managed certificate to use with ingress lb
resource "google_compute_managed_ssl_certificate" "managed_certificate" {
  provider = google-beta
  name     = element(split(".", var.domain), 0)

  project = var.project_name

  managed {
    domains = [var.domain]
  }
}

// public ip reserved for ingress load balancer
resource "google_compute_global_address" "ingress_ip" {
  name = var.app_name
}