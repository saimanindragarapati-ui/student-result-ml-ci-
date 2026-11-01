# Practical-6: Dockerize the ML Prediction Application

## Objective
Containerize the Student Result Prediction application prepared in Practical-5. Package the Flask application, trained model, Python runtime, and dependencies into a Docker image, run it as a container, and verify its health and prediction endpoints from the host.

## Docker concepts
- **Dockerfile:** instructions used to build the image.
- **Image:** packaged application, trained model, runtime, and dependencies.
- **Container:** running instance of the image.
- **Port mapping:** maps host port 5000 to container port 5000.
- **Build context:** directory whose files are available to the Docker build.

## Step 1: Verify Docker

```bash
docker --version
docker info
docker run --rm hello-world
```

Docker Desktop or Docker Engine must be running.

## Step 2: Add Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY student_result_model.pkl .
COPY metrics.json .

EXPOSE 5000

CMD ["python", "app.py"]
```

The Flask app must bind to `0.0.0.0` on port `5000` so it is accessible through the container network interface.

## Step 3: Add .dockerignore

```text
__pycache__/
*.pyc
.git/
.github/
test_*.py
student_results.csv
release_candidate/
```

## Step 4: Update the delivery workflow

The Practical-5 workflow continues to train the model, run the quality gate, and execute ML and API tests. In its `Prepare release candidate` step, it must additionally copy `Dockerfile` and `.dockerignore` into `release_candidate/`. The workflow in `.github/workflows/ml-ci.yml` implements this packaging change. The uploaded artifact remains named `student-result-ml-release`.

## Step 5: Download the artifact

After a successful GitHub Actions run, download and extract `student-result-ml-release`. Confirm it contains `app.py`, `student_result_model.pkl`, `metrics.json`, `requirements.txt`, `Dockerfile`, `.dockerignore`, and `DEPLOYMENT.txt`.

## Step 6: Build the image

Run from the extracted release folder:

```bash
docker build -t student-result-ml:1.0 .
docker images
```

## Step 7: Run the container

```bash
docker run -d --name student-result-ml-container -p 5000:5000 student-result-ml:1.0
docker ps
```

The port mapping exposes the Flask API on the host at `localhost:5000`. `EXPOSE 5000` in the Dockerfile documents the container port; `-p 5000:5000` publishes it to the host.

## Step 8: Test the health endpoint

Open `http://localhost:5000/` or run:

```bash
curl http://localhost:5000/
```

Expected response:

```json
{"service":"student-result-prediction","status":"ok"}
```

## Step 9: Test a high-performance prediction

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"attendance":90,"internal_marks":85,"assignment_marks":88,"previous_score":80}'
```

Expected class: `PASS`, prediction code `1`.

## Step 10: Test a low-performance prediction

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"attendance":55,"internal_marks":30,"assignment_marks":40,"previous_score":35}'
```

Expected class: `FAIL`, prediction code `0`.

## Step 11: Inspect logs and stop the container

```bash
docker logs student-result-ml-container
docker stop student-result-ml-container
docker rm student-result-ml-container
```

## Important scope note

Practical-6 uses GitHub Actions to prepare a Docker-ready artifact, but builds and tests the Docker image manually on the local system. Automated Docker image building and validation in GitHub Actions is the subject of Practical-7.

## Result
The validated Student Result Prediction application is configured for Docker packaging. Once the image is built and run locally, its health and prediction APIs can be verified through the published host port.

## Evidence to capture
1. Successful GitHub Actions run with Dockerfile and `.dockerignore` included in the artifact.
2. Extracted release candidate folder contents.
3. `docker --version` and successful `docker info`.
4. Successful Docker image build.
5. `docker images` showing `student-result-ml:1.0`.
6. `docker ps` showing the running container and port mapping.
7. Health endpoint response.
8. PASS prediction request and response.
9. FAIL prediction request and response.
10. Container logs.
