
import unittest
from unittest.mock import patch

from app import app


class TestPredictionApplication(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")
        self.assertTrue(response.headers.get("X-Request-ID"))

    def test_custom_request_id(self):
        response = self.client.get(
            "/health",
            headers={"X-Request-ID": "practical-11-test"}
        )

        self.assertEqual(
            response.headers.get("X-Request-ID"),
            "practical-11-test"
        )

    def test_high_performance_prediction(self):
        response = self.client.post(
            "/predict",
            json={
                "attendance": 90,
                "internal_marks": 85,
                "assignment_marks": 88,
                "previous_score": 80
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["prediction"], "PASS")
        self.assertEqual(response.get_json()["prediction_code"], 1)

    def test_low_performance_prediction(self):
        response = self.client.post(
            "/predict",
            json={
                "attendance": 55,
                "internal_marks": 30,
                "assignment_marks": 40,
                "previous_score": 35
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["prediction"], "FAIL")
        self.assertEqual(response.get_json()["prediction_code"], 0)

    def test_missing_field_validation(self):
        with self.assertLogs(
            "student-result-api",
            level="WARNING"
        ) as captured:

            response = self.client.post(
                "/predict",
                json={
                    "attendance": 90,
                    "internal_marks": 85
                }
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("missing_fields", response.get_json())
        self.assertIn(
            "event=validation_error",
            "\n".join(captured.output)
        )

    def test_invalid_numeric_input(self):
        with self.assertLogs(
            "student-result-api",
            level="WARNING"
        ) as captured:

            response = self.client.post(
                "/predict",
                json={
                    "attendance": "high",
                    "internal_marks": 85,
                    "assignment_marks": 88,
                    "previous_score": 80
                }
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "event=validation_error",
            "\n".join(captured.output)
        )

    def test_unknown_route(self):
        with self.assertLogs(
            "student-result-api",
            level="WARNING"
        ) as captured:

            response = self.client.get("/not-a-real-route")

        self.assertEqual(response.status_code, 404)
        self.assertIn(
            "event=route_not_found",
            "\n".join(captured.output)
        )

    def test_prediction_runtime_error(self):
        with patch(
            "app.model.predict",
            side_effect=RuntimeError("synthetic failure")
        ):

            with self.assertLogs(
                "student-result-api",
                level="ERROR"
            ) as captured:

                response = self.client.post(
                    "/predict",
                    json={
                        "attendance": 90,
                        "internal_marks": 85,
                        "assignment_marks": 88,
                        "previous_score": 80
                    }
                )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {"error": "Prediction failed"}
        )

        self.assertIn(
            "event=prediction_failed",
            "\n".join(captured.output)
        )


if __name__ == "__main__":
    unittest.main()
