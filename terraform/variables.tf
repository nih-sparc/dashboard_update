variable "aws_region" {
  default = "us-east-1"
}

variable "aws_account" {}

variable "bf_secret" {}

variable "bf_token" {}

variable "environment_name" {
  default = "dev"
}

variable "service_name" {
  default = "sparc-dash"
}

variable "version_number" {}

variable "bucket" {}

variable "dataset_name" {}

variable "api_loc" {
  default = "https://api.blackfynn.io"
}
