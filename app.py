
import logging
import os
import time
import uuid
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, Response, g, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Configure logging
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

SAFE_INPUT_FIELDS = set()

# ---------------- PROMETHEUS METRICS ----------------

HTTP_REQUESTS = Counter(
    "student_api_http_requests",
    "Total HTTP requests received by the API",
    ["method", "path", "status"],
)

HTTP_LATENCY = Histogram(
    "student_api_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

PREDICTIONS = Counter(
    "student_api_predictions",
    "Total prediction attempts",
    ["result"],
)

MODEL_LOADED = Gauge(
    "student_api_model_loaded",
    "Whether the ML model is loaded",
)

# ---------------- MODEL LOADING ----------------

def load_model():
    logger.info("event=model_load_started model_file=%s", MODEL_PATH.name)

    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "student_result_model.pkl was not found. "
                "Run the training pipeline first."
            )

        loaded_model = joblib.load(MODEL_PATH)

        MODEL_LOADED.set(1)

        logger.info("event=model_loaded model_file=%s", MODEL_PATH.name)

        return loaded_model

    except Exception:
        MODEL_LOADED.set(0)
        logger.exception("event=model_load_failed")
        raise


try:
    model = load_model()
except Exception:
    logger.exception("event=application_startup_failed")
    raise


# ---------------- REQUEST TRACKING ----------------

@app.before_request
def start_request_tracking():
    supplied_id = request.headers.get("X-Request-ID", "").strip()

    g.request_id = supplied_id[:128] if supplied_id else str(uuid.uuid4())
    g.request_started_at = time.perf_counter()


@app.after_request
def log_request(response):

    duration_seconds = time.perf_counter() - g.request_started_at
    duration_ms = duration_seconds * 1000

    # Do not count Prometheus scraping as an application request
    if request.path != "/metrics":

        route = request.url_rule.rule if request.url_rule else "unmatched"

        HTTP_REQUESTS.labels(
            method=request.method,
            path=route,
            status=str(response.status_code),
        ).inc()

        HTTP_LATENCY.labels(
            method=request.method,
            path=route,
        ).observe(duration_seconds)

    level = (
        logging.WARNING
        if response.status_code >= 400
        else logging.INFO
    )

    logger.log(
        level,
        f"event=http_request request_id={g.request_id} "
        f"method={request.method} "
        f"path={request.path} "
        f"status={response.status_code} "
        f"duration_ms={duration_ms:.2f}",
    )

    response.headers["X-Request-ID"] = g.request_id

    return response


# ---------------- PROMETHEUS ENDPOINT ----------------

@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        content_type=CONTENT_TYPE_LATEST,
    )


# ---------------- ERROR HANDLING ----------------

@app.errorhandler(404)
def handle_not_found(error):
    logger.warning(
        "event=route_not_found request_id=%s path=%s",
        getattr(g, "request_id", "unknown"),
        request.path,
    )

    return jsonify({"error": "Not found"}), 404


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    logger.exception(
        "event=unhandled_exception request_id=%s path=%s",
        getattr(g, "request_id", "unknown"),
        request.path,
    )

    return jsonify({"error": "Internal server error"}), 500


# ---------------- HEALTH ENDPOINT ----------------

@app.get("/")
@app.get("/health")
def health_check():
    return jsonify({
        "status": "ok",
        "service": "student-result-prediction",
    })


# ---------------- PREDICTION ENDPOINT ----------------

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

        PREDICTIONS.labels(result="success").inc()

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
        PREDICTIONS.labels(result="error").inc()

        logger.exception(
            "event=prediction_failed request_id=%s",
            g.request_id,
        )

        return jsonify({
            "error": "Prediction failed"
        }), 500


# ---------------- APPLICATION START ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port
    )
