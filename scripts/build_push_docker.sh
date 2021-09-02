
PROJECT_NAME="ehallmarksolutions"
APP_NAME="bsc-explorer"
GCLOUD_USER=evan@ehallmarksolutions.com

echo "Logging into GCP"
gcloud auth login $GCLOUD_USER
gcloud config set project "$PROJECT_NAME"

IMAGE_NAME="gcr.io/$PROJECT_NAME/$APP_NAME:latest"

echo "Building image"
docker build -t $IMAGE_NAME .

docker push $IMAGE_NAME