//DEFINE PROVIDER
provider "aws" {
  profile = "${var.aws_account}"
  region  = "${var.aws_region}"
  version = "~> 2.50"
}
