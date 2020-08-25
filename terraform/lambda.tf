resource "aws_lambda_function" "lambda_function_dashboard_update" {
  function_name    = "${var.environment_name}-${var.service_name}"
  role             = "${aws_iam_role.lambda_iam_role.arn}"
  handler          = "sparc_dash.lambda_handler"
  runtime          = "python3.7"
  s3_bucket        = "${var.bucket}"
  s3_key           = "${var.service_name}/${var.service_name}-${var.version_number}.zip"
  s3_object_version = "${data.aws_s3_bucket_object.s3_bucket_object.version_id}"
  timeout          = 900

  environment {
    variables = {
      BLACKFYNN_API_TOKEN = "${var.bf_token}"
      BLACKFYNN_API_SECRET = "${var.bf_secret}"
      BLACKFYNN_API_LOC = "${var.api_loc}"
      BLACKFYNN_LOCAL_DIR = "/tmp/blackfynn"
      BLACKFYNN_USE_CACHE = 0
      DASHBOARD_DATASET_NAME = "${var.dataset_name}"
      SCICRUNCH_API_KEY = "${var.scicrunch_api_key}"
    }
  }
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_foo" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda_function_dashboard_update.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.every_24_hours.arn}"
}