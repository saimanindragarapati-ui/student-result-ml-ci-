
import logging
import os
import time
import uuid
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, g, jsonify, request

# Configure logging to standard output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()],
    force=True,
)

logger = logging.getLogger("student-result-api")

app = Flask(__name__)

MODEL_PATH = Path("student_result_model.pkl")

FEATURES = [
    "attendance",
    "internal_marks",
    "assignment_marks",
    "previous_score",
]

# Do not log full student input data
SAFE_INPUT_FIELDS = set()


# Load the existing trained model
def load_model():
    logger.info("event=model_load_started model_file=%s", MODEL_PATH.name)

    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "student_result_model.pkl was not found. "
                "Run the training pipeline first."
            )

        loaded_model = joblib.load(MODEL_PATH)

        logger.info("event=model_loaded model_file=%s", MODEL_PATH.name)

        return loaded_model

    except Exception:
        logger.exception("event=model_load_failed")
        raise


try:
    model = load_model()
except Exception:
    logger.exception("event=application_startup_failed")
    raise


# Request tracking middleware
@app.before_request
def start_request_tracking():
    supplied_id = request.headers.get("X-Request-ID", "").strip()

    g.request_id = supplied_id[:128] if supplied_id else str(uuid.uuid4())
    g.request_started_at = time.perf_counter()


@app.after_request
def log_request(response):
    duration_ms = (
        time.perf_counter() - g.request_started_at
    ) * 1000

    level = (
        logging.WARNING
        if response.status_code >= 400
        else logging.INFO
    )

    logger.log(
        level,
        "event=http_request request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        g.request_id,
        request.method,
        request.path,
        response.status_code,
        duration_ms,
    )

    response.headers["X-Request-ID"] = g.request_id

    return response


# Handle missing routes
@app.errorhandler(404)
def handle_not_found(error):
    logger.warning(
        "event=route_not_found request_id=%s path=%s",
        getattr(g, "request_id", "unknown"),
        request.path,
    )

    return jsonify({"error": "Not found"}), 404


# Handle unexpected application errors
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    logger.exception(
        "event=unhandled_exception request_id=%s path=%s",
        getattr(g, "request_id", "unknown"),
        request.path,
    )

    return jsonify({"error": "Internal server error"}), 500


# Health endpoint
@app.get("/")
@app.get("/health")
def health_check():
    return jsonify({
        "status": "ok",
        "service": "student-result-prediction",
    })


# Prediction endpoint
@app.post("/predict")
def predict():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        logger.warning(
            "event=validation_error request_id=%s reason=invalid_json",
            g.request_id,
        )

        return jsonify({
            "error": "A JSON object request body is required"
        }), 400

    missing_fields = [
        feature for feature in FEATURES
        if feature not in data
    ]

    if missing_fields:
        logger.warning(
            "event=validation_error request_id=%s missing_fields=%s",
            g.request_id,
            missing_fields,
        )

        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields,
        }), 400

    invalid_fields = [
        feature for feature in FEATURES
        if isinstance(data[feature], bool)
        or not isinstance(data[feature], (int, float))
    ]

    if invalid_fields:
        logger.warning(
            "event=validation_error request_id=%s invalid_fields=%s",
            g.request_id,
            invalid_fields,
        )

        return jsonify({
            "error": "Numeric values are required",
            "invalid_fields": invalid_fields,
        }), 400

    safe_input = {
        key: data[key]
        for key in SAFE_INPUT_FIELDS
        if key in data
    }

    logger.info(
        "event=prediction_request request_id=%s feature_names=%s safe_input=%s",
        g.request_id,
        sorted(data.keys()),
        safe_input,
    )

    try:
        input_df = pd.DataFrame([
            {feature: data[feature] for feature in FEATURES}
        ])

        prediction_code = int(model.predict(input_df)[0])

        prediction = (
            "PASS" if prediction_code == 1 else "FAIL"
        )

        logger.info(
            "event=prediction_success request_id=%s prediction=%s",
            g.request_id,
            prediction,
        )

        return jsonify({
            "prediction": prediction,
            "prediction_code": prediction_code,
        })

    except Exception:
        logger.exception(
            "event=prediction_failed request_id=%s",
            g.request_id,
        )

        return jsonify({
            "error": "Prediction failed"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port
    )
