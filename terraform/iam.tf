# LAMBDA IAM ROLE
resource "aws_iam_role" "lambda_iam_role" {
  name = "${var.environment_name}-${var.service_name}-lambda-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


# CREATE LAMBDA IAM ROLE POLICY
resource "aws_iam_role_policy" "lambda_iam_role_policy" {
  name = "${aws_iam_role.lambda_iam_role.name}-policy"
  role = "${aws_iam_role.lambda_iam_role.name}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Lambda",
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": [
        "*"
      ]
    },
    {
      "Sid": "CloudwatchLogPermissions",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutDestination",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": [
        "*"
      ]
    },
    {
      "Sid": "Ec2Permissions",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DeleteNetworkInterface",
        "ec2:CreateNetworkInterface",
        "ec2:AttachNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "autoscaling:CompleteLifecycleAction"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}
EOF
}
