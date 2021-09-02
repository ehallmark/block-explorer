
PROJECT_NAME="ehallmarksolutions"
APP_NAME="bsc-explorer"

echo "Logging into GCP"
gcloud auth login evan@ehallmarksolutions.com
gcloud config set project "$PROJECT_NAME"

IMAGE_NAME="gcr.io/$PROJECT_NAME/$APP_NAME:latest"

echo "Building image"
docker build -t $IMAGE_NAME .

docker push $IMAGE_NAME