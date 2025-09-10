# txt
Zip project:
  zip -r health-ai-backend.zip . -x "*.pyc" "__pycache__/*"
Docker push:
  docker build -t <registry>/health-ai-backend:latest .
  docker push <registry>/health-ai-backend:latest
Copy CI:
  mkdir -p .github/workflows && cp github_actions_ci.yml .github/workflows/ci.yml
