# Student Result Prediction — Practical 5 (Continuous Delivery)

This repository contains the student-result ML training pipeline and a Flask prediction API. Practical-5 extends the earlier CI workflow into Continuous Delivery by creating a release candidate only after the model quality gate, ML tests, and API tests pass.

## Workflow

1. Install dependencies.
2. Train the student-result model and save `student_result_model.pkl` plus `metrics.json`.
3. Enforce the 0.85 minimum-accuracy quality gate.
4. Run the ML pipeline tests.
5. Run the Flask API tests.
6. Package `app.py`, the trained model, metrics, dependencies, and deployment instructions.
7. Upload the `student-result-ml-release` artifact.

## Run locally

```bash
python -m pip install -r requirements.txt
python train_model.py
python quality_gate.py
python -m unittest test_ml_pipeline.py -v
python -m unittest test_app.py -v
python app.py
```

The health endpoint is `GET /`. The prediction endpoint is `POST /predict` and requires `attendance`, `internal_marks`, `assignment_marks`, and `previous_score` in its JSON body.

Example request:

```json
{
  "attendance": 90,
  "internal_marks": 85,
  "assignment_marks": 88,
  "previous_score": 80
}
```

The workflow prepares a release candidate; production deployment is a separate step.
