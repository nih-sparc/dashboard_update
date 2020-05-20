#!/bin/bash -ex

BUILD_NUMBER="6"
PYTHON_BINARY="/usr/bin/python3.7"
PYTHON_VIRTUALENV="venv"

WORKING_DIR=$(pwd)
FUNCTION_NAME="sparc-dash"
VERSION="${BUILD_NUMBER}"
PACKAGE_NAME="${FUNCTION_NAME}-${VERSION}.zip"


build_lambda_template() {
  python3 -m venv ${PYTHON_VIRTUALENV}
  source ${PYTHON_VIRTUALENV}/bin/activate

  pip3 install blackfynn

  cd ${WORKING_DIR}/${PYTHON_VIRTUALENV}/lib/python3.7/site-packages/
  zip -r9 ${WORKING_DIR}/${PACKAGE_NAME} *

  cd ${WORKING_DIR}
  pip3 install awscli
}

build_lambda_template

cd ${WORKING_DIR}/source
zip -r9 ${WORKING_DIR}/${PACKAGE_NAME} sparc_dash.py
cd ${WORKING_DIR}

## Copy zip file to Lambda S3 location
aws s3 cp ${WORKING_DIR}/${PACKAGE_NAME} s3://sparc-tools/${FUNCTION_NAME}/

## remove zip file from project folder
rm -rf ${WORKING_DIR}/${PACKAGE_NAME}
deactivate
