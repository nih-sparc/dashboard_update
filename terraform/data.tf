// IMPORT LAMBDA S3 BUCKET OBJECT
data "aws_s3_bucket_object" "s3_bucket_object" {
  bucket = "${var.bucket}"
  key    = "${var.service_name}/${var.service_name}-${var.version_number}.zip"
}