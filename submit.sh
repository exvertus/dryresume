gcloud builds submit --region=us-central1 --project=$GOOGLE_CLOUD_PROJECT --config=cloudbuild.yaml --substitutions=_LOCATION="us-central1",_AR_PATH="us-central1-docker.pkg.dev"
