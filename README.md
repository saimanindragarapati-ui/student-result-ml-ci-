# Student Result Prediction - Practical 6: Dockerize the ML Prediction Application

This practical continues Practical-5 by adding Docker configuration and preparing a Docker-ready release candidate through GitHub Actions. The Docker image is built and run manually on the local machine; automatic Docker build and validation in GitHub Actions is reserved for Practical-7.

## Files added

- `Dockerfile`: Python 3.11 slim image, installs `requirements.txt`, copies the Flask app, trained model, and metrics, exposes port 5000, and starts `app.py`.
- `.dockerignore`: excludes Python caches, Git metadata, tests, generated CSV data, and the local release-candidate directory from the Docker build context.
- `.github/workflows/ml-ci.yml`: retains the Practical-5 training, quality-gate, and tests, then includes `Dockerfile` and `.dockerignore` in the `student-result-ml-release` artifact.

## Build and run locally

First, download the `student-result-ml-release` artifact from a successful GitHub Actions run and extract it. Run these commands from the extracted folder containing `Dockerfile`:

```bash
docker --version
docker info
docker build -t student-result-ml:1.0 .
docker images
docker run -d --name student-result-ml-container -p 5000:5000 student-result-ml:1.0
docker ps
```

Health check:

```bash
curl http://localhost:5000/
```

High-performing sample (expected class: PASS):

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"attendance":90,"internal_marks":85,"assignment_marks":88,"previous_score":80}'
```

Low-performing sample (expected class: FAIL):

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"attendance":55,"internal_marks":30,"assignment_marks":40,"previous_score":35}'
```

Inspect logs and clean up:

```bash
docker logs student-result-ml-container
docker stop student-result-ml-container
docker rm student-result-ml-container
```

## Important scope

Practical-6 prepares and uploads a Docker-ready release candidate. It does not build a Docker image in GitHub Actions. That automation is introduced in Practical-7.
