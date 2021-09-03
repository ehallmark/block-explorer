PROJECT_NAME="ehallmarksolutions"
APP_NAME="bsc-explorer"
GCLOUD_USER=evan@ehallmarksolutions.com

echo "Logging into GCP"
gcloud auth login $GCLOUD_USER
gcloud config set project "$PROJECT_NAME"

gcloud container clusters get-credentials $APP_NAME --region us-west2-c
