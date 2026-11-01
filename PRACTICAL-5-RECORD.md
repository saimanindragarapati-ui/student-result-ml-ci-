# Practical-5: Continuous Delivery of an ML Prediction Application using GitHub Actions

## Objective
Extend the Student Result Prediction ML CI workflow to validate a Flask prediction API, package the validated model and application files, and preserve the package as a release candidate.

## Files added or used

- `app.py` — Flask health-check and prediction endpoints.
- `test_app.py` — application tests for health, PASS, FAIL, and missing fields.
- `requirements.txt` — Flask and ML dependencies.
- `.github/workflows/ml-ci.yml` — training, quality gate, ML tests, API tests, release packaging, and artifact upload.
- `train_model.py`, `quality_gate.py`, `test_ml_pipeline.py` — existing ML CI components from the preceding practicals.

## Execution sequence

1. Checkout source and install Python dependencies.
2. Train the model and generate metrics.
3. Run `quality_gate.py` (minimum accuracy: 0.85).
4. Run the ML pipeline tests.
5. Run the Flask API tests.
6. Copy `app.py`, `student_result_model.pkl`, `metrics.json`, and `requirements.txt` into `release_candidate/` and write `DEPLOYMENT.txt`.
7. Upload the directory as the `student-result-ml-release` Actions artifact.

## Expected API behavior

- `GET /` returns service status `ok`.
- `POST /predict` accepts attendance, internal marks, assignment marks, and previous score.
- A high-performance sample should return `PASS`.
- A low-performance sample should return `FAIL`.
- An incomplete request should return HTTP 400 with `missing_fields`.

## Result

The CI workflow is extended to Continuous Delivery: a release artifact is produced only after the model quality gate and both ML and API test suites succeed. Production deployment is not part of this practical.

## Verification note

The GitHub Actions run and artifact must be verified in the repository's Actions tab after these files are pushed. Do not mark the GitHub workflow as passed until that run is green.
