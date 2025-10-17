gcloud run deploy alora-mcp-server \
    --no-allow-unauthenticated \
    --region=us-central1 \
    --source=. \
    --labels=app=alora-mcp,env=development
