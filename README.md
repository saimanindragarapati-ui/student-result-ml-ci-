# Student Result Prediction — Practical 7: Automated Docker Build and Test

Practical-7 extends the ML CI/CD workflow by validating the final Docker runtime inside GitHub Actions.

## Automated workflow

1. Install dependencies.
2. Train the student-result model.
3. Enforce the ML quality gate.
4. Run ML pipeline and Flask API tests.
5. Build a Docker image tagged with the current Git commit SHA.
6. Start the container with host port 5000 mapped to container port 5000.
7. Retry the `/health` endpoint until the Flask service is ready.
8. Send a prediction request to `/predict` and verify the PASS response.
9. Capture logs and remove the container even if an earlier step fails.

## API endpoints

- `GET /` and `GET /health`: service health.
- `POST /predict`: requires `attendance`, `internal_marks`, `assignment_marks`, and `previous_score`.

## Run locally

```bash
python -m pip install -r requirements.txt
python train_model.py
python quality_gate.py
python -m unittest test_ml_pipeline.py -v
python -m unittest test_app.py -v
docker build -t student-result-ml:local .
docker run -d --name student-result-ml-container -p 5000:5000 student-result-ml:local
curl --fail http://localhost:5000/health
curl --fail -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"attendance":90,"internal_marks":85,"assignment_marks":88,"previous_score":80}'
docker logs student-result-ml-container
docker rm -f student-result-ml-container
```

The image is built and tested inside a temporary GitHub Actions runner. This practical does not publish the image to a registry or deploy it to production.
