
variable "domain" {
  default = "bsc-explorer.evanhallmark.com"
}

variable "region" {
  default = "us-west2" // Set as per your nearest location or preference
}

variable "location" {
  default = "us-west2-c"  // Set as per your nearest location or preference
}

variable "project_name" {
  default = "ehallmarksolutions"
}

variable "app_name" {
  default = "bsc-explorer"
}

variable "sql_user" {
  default = "explorer"
}

variable "sql_password" {}

variable "bscscan_api_key" {}

variable "etherscan_api_key" {}

variable "polygonscan_api_key" {}

variable "account_id" {}
