#!/bin/bash

# Exit on error
set -e

PROJECT_ID="silver-455021"
SERVICE_ACCOUNT_EMAIL="github-ci-cd-sa@${PROJECT_ID}.iam.gserviceaccount.com"
GITHUB_REPO="surfiniaburger/vigilant-journey"

echo "Creating Workload Identity Pool..."
gcloud iam workload-identity-pools create "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Pool"

echo "Creating Workload Identity Provider for GitHub..."
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

echo "Allowing GitHub to impersonate the service account..."
gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-pool/subject/repo:${GITHUB_REPO}:ref:refs/heads/main"

echo "Workload Identity Federation setup is complete."
echo "Please create the following secrets in your GitHub repository:"
echo "GCP_WORKLOAD_IDENTITY_PROVIDER: projects/$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-pool/providers/github-provider"
echo "GCP_SERVICE_ACCOUNT_EMAIL: ${SERVICE_ACCOUNT_EMAIL}"
