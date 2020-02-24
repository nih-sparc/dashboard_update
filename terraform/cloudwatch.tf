resource "aws_cloudwatch_event_rule" "every_24_hours" {
  name                = "every_24_hours"
  description         = "Fires every 24 hours"
  schedule_expression = "rate(24 hours)"
}

resource "aws_cloudwatch_event_target" "check_foo_every_24_hours" {
  rule      = "${aws_cloudwatch_event_rule.every_24_hours.name}"
  target_id = "lambda"
  arn       = "${aws_lambda_function.lambda_function_dashboard_update.arn}"
}