PROJECT_NAME="ehallmarksolutions"
APP_NAME="bsc-explorer"

echo "Logging into GCP"
gcloud auth login evan@ehallmarksolutions.com
gcloud config set project "$PROJECT_NAME"

gcloud container clusters get-credentials $APP_NAME --region us-west2-c
