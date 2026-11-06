
# MLOps Practical-11: Logging and Error Tracking

## 1. Aim

To implement application logging and error tracking in the Student Result Prediction API, test successful and failed requests, publish the updated Docker image through GitHub Actions and GHCR, and redeploy the application on Render.

## 2. Learning Objectives

- Understand application logging.
- Differentiate INFO, WARNING and ERROR log levels.
- Record application startup and model loading events.
- Track HTTP requests using request IDs.
- Measure API response time.
- Record successful and failed predictions.
- Identify invalid requests and runtime errors.
- Inspect application logs through Docker and Render.

## 3. Project Details

- Project: Student Result Prediction
- Framework: Flask
- Programming Language: Python
- ML Model: Logistic Regression
- Containerization: Docker
- CI/CD: GitHub Actions
- Container Registry: GitHub Container Registry (GHCR)
- Cloud Deployment: Render

## 4. Logging Implementation

Python logging was implemented using the logging module.

### INFO
Records normal application events:
- Model loaded successfully.
- Health endpoint accessed.
- Prediction completed successfully.

### WARNING
Records unexpected or invalid requests:
- Missing input fields.
- Invalid numeric values.
- Unknown API routes.

### ERROR
Records application failures:
- Model loading failure.
- Prediction runtime failure.
- Unexpected application exceptions.

## 5. Request Tracking

The application generates a unique request ID for each incoming request.

It records:
- Request ID
- HTTP method
- Request path
- Response status code
- Response duration in milliseconds

The request ID is returned through the X-Request-ID response header.

## 6. Prediction Logging

The existing prediction API is maintained.

Required input features:

1. attendance
2. internal_marks
3. assignment_marks
4. previous_score

The application records prediction request and prediction success events.

Sensitive student information and complete input payloads are not logged.

## 7. Error Tracking

The following cases are handled:

| Test | Expected HTTP Status |
|---|---:|
| Successful health request | 200 |
| Successful prediction | 200 |
| Missing input fields | 400 |
| Invalid numeric input | 400 |
| Unknown API route | 404 |
| Prediction runtime failure | 500 |

Note: This project uses Flask. Its validation responses use HTTP 400, not the HTTP 422 response described in the FastAPI handout.

## 8. Testing Procedure

### Test 1: Health Endpoint

```bash
curl -i http://localhost:5000/health
```

Expected result: HTTP 200 and service status OK.

### Test 2: Successful Prediction

```bash
curl -X POST http://localhost:5000/predict \
-H "Content-Type: application/json" \
-d '{"attendance":90,"internal_marks":85,"assignment_marks":90,"previous_score":88}'
```

Expected result:

```json
{
  "prediction": "PASS",
  "prediction_code": 1
}
```

### Test 3: Invalid Request

```bash
curl -i -X POST http://localhost:5000/predict \
-H "Content-Type: application/json" \
-d '{"attendance":90,"internal_marks":85}'
```

Expected result: HTTP 400 with a validation warning in the logs.

### Test 4: Unknown Route

```bash
curl -i http://localhost:5000/not-a-real-route
```

Expected result: HTTP 404 and a warning log.

## 9. Docker Implementation

Build the updated Docker image:

```bash
docker build -t student-result-ml:practical-11 .
```

Run the container:

```bash
docker run --rm -p 5000:5000 \
--name student-result-p11 \
student-result-ml:practical-11
```

Inspect container logs:

```bash
docker logs student-result-p11
```

## 10. GitHub Actions and GHCR

The existing GitHub Actions workflow is reused.

The workflow:
1. Checks out the repository.
2. Installs Python dependencies.
3. Trains the model for the Docker build context.
4. Executes the ML quality gate.
5. Runs automated tests.
6. Builds the Docker image.
7. Tests the health and prediction endpoints.
8. Publishes the tested image to GHCR.

The updated image is published with latest and commit-specific tags.

## 11. Render Deployment

The existing Render Web Service is reused.

After the updated image is published:
1. Open Render Dashboard.
2. Select Student Result Prediction.
3. Choose Manual Deploy.
4. Select Deploy latest reference.
5. Wait until the service becomes Live.
6. Verify the public health and prediction endpoints.
7. Inspect runtime logs.

## 12. Observation Table

| Experiment | Expected Result | Observed Result |
|---|---|---|
| Model loading | Successful model load log | Pending |
| Health endpoint | HTTP 200 | Pending |
| Prediction endpoint | PASS/FAIL response | Pending |
| Missing fields | HTTP 400 warning | Pending |
| Invalid input | HTTP 400 warning | Pending |
| Unknown route | HTTP 404 warning | Pending |
| Runtime exception | HTTP 500 error log | Pending |
| Docker build | Successful image build | Pending |
| GitHub Actions | Workflow success | Pending |
| GHCR publication | Updated image | Pending |
| Render deployment | Live service | Pending |

## 13. Result

Application logging and error tracking have been implemented in the Student Result Prediction Flask API. The updated application records startup events, HTTP requests, prediction events, validation failures and runtime exceptions.

Final completion will be confirmed after successful local tests, GitHub Actions execution, GHCR publication and Render redeployment.

## 14. Conclusion

Logging and error tracking improve the reliability and maintainability of deployed machine learning applications. They help developers identify API failures, trace individual requests and diagnose prediction errors.

## 15. Future Enhancement

The next practical will focus on monitoring API availability, request latency, error rates, resource usage and alert configuration.
