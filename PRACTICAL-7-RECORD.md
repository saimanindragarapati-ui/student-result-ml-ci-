# Practical-7: Automate Docker Build and Test Using GitHub Actions

## Objective
Extend the Student Result Prediction ML CI/CD workflow so GitHub Actions trains and validates the model, builds a Docker image, starts the container, verifies the Flask health endpoint, tests a prediction, captures logs, and cleans up the container.

## Changes
- Added a `/health` route while retaining the existing `/` route.
- Updated `.github/workflows/ml-ci.yml` to run Docker validation after model and application tests.
- Docker image tag includes the GitHub commit SHA.
- The workflow waits up to 15 attempts (2 seconds each) for health readiness.
- Prediction test checks for the expected PASS response and code 1.
- Logs and container cleanup use `if: always()`.

## Workflow
Checkout → Set up Python → Install dependencies → Train model → Quality gate → ML tests → API tests → Docker build → Container start → Health check → Prediction test → Logs → Cleanup.

## Important distinction
The Docker image is built and tested only on the temporary GitHub Actions runner. This practical does not push the image to a container registry or deploy it to production.

## Verification evidence to capture
1. Repository showing Dockerfile and `.dockerignore`.
2. Updated Actions workflow file.
3. Successful Docker build log.
4. Successful container startup.
5. Successful `/health` response.
6. Successful `/predict` response.
7. Container logs.
8. Complete green workflow run.
9. Controlled health-check failure and subsequent corrected successful run.

## Result
The ML prediction application is validated inside its Docker runtime automatically by GitHub Actions, including build, startup, health, prediction, log collection, and cleanup.
