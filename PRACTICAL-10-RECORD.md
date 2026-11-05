# Practical-10: Deploy the Tested GHCR Image to Render

## Aim
Deploy the already-tested Student Result Prediction Docker image from GitHub Container Registry (GHCR) to a public Render Web Service and verify the deployed HTTP endpoints.

## Project-specific values
- GitHub repository: `saimanindragarapati-ui/student-result-ml-ci-`
- GHCR image: `ghcr.io/saimanindragarapati-ui/student-result-ml:latest`
- Container: Flask application
- Default local/container port: `5000`
- Render port: `10000` (set the `PORT` environment variable; app.py reads it)
- Health endpoint: `GET /health`
- Root endpoint: `GET /`
- Prediction endpoint: `POST /predict`
- Swagger `/docs`: Not available in the current Flask application. Do not record this endpoint as tested or successful.

## Continuity from Practical-9
Practical-9 builds, tests, and publishes the image to GHCR. Practical-10 deploys that image without rebuilding the application or retraining the model. Use the GHCR tag produced by the successful Practical-9 run.

## Important app adjustment for Render
Render recommends that a web service bind to `0.0.0.0` and use the `PORT` environment variable (default 10000). The existing app used a fixed port 5000. The supplied updated `app.py` keeps 5000 as the default for local development and CI, but honors `PORT` when Render supplies it. Commit this app.py change and let Practical-9 run again before deploying, so the image in GHCR contains the Render-compatible code.

## Private GHCR access
The `student-result-ml` package is private. In Render, add a container registry credential:
- Name: `ghcr-student-result-read` (suggested)
- Registry: GitHub Container Registry / `ghcr.io`
- Username: `saimanindragarapati-ui`
- Personal Access Token: a newly generated GitHub Personal Access Token (classic) with only `read:packages`.
Never reuse or share a token that has been exposed. Do not place the token in this repository, the report, or screenshots.

## Render deployment procedure
1. Confirm the latest Practical-9 GitHub Actions run succeeded and published `latest`.
2. Confirm the package is available in GHCR.
3. Sign in to the Render Dashboard.
4. Select **New → Web Service**.
5. Under source, select **Existing Image**.
6. Enter `ghcr.io/saimanindragarapati-ui/student-result-ml:latest`.
7. Select or create the `ghcr-student-result-read` registry credential for the private GHCR package.
8. Connect/verify the image.
9. Set service name to `student-result-prediction` (or another available name).
10. Choose an available region and plan.
11. In Advanced settings, set environment variable `PORT` to `10000`.
12. Set Health Check Path to `/health`.
13. Create/deploy the service and wait for the Live status.
14. Copy the actual `https://<service-name>.onrender.com` URL assigned by Render.

## Verify the deployed service
Replace `<RENDER_URL>` with the actual URL assigned by Render.

- Root: `https://<RENDER_URL>/`
- Health: `https://<RENDER_URL>/health`
- Prediction: send a POST request to `https://<RENDER_URL>/predict` with JSON:
  `{"attendance":90,"internal_marks":85,"assignment_marks":90,"previous_score":88}`

Expected prediction response is JSON containing `prediction` and `prediction_code`; the validated classroom payload previously returned `PASS` and code `1`.

The current app does not provide `/docs` or Swagger UI. A Swagger endpoint would require an additional API documentation implementation and is outside the existing app contract.

## Logs and update behavior
- Inspect Render Events and Logs for successful image pull, startup, and absence of repeated crashes.
- Render image-backed services do not automatically redeploy when a mutable tag such as `latest` changes. After Practical-9 publishes a newer image, use **Manual Deploy → Deploy latest reference** in Render.

## Observation table
| Checkpoint | Expected observation | Student record |
|---|---|---|
| Practical-9 image | `latest` exists in GHCR | Pending |
| Existing Image source | Render uses the GHCR image | Pending |
| Private image credential | Render can pull private GHCR package | Pending |
| Port | App listens on Render `PORT` | Pending |
| Health check | `/health` succeeds | Pending |
| Deployment | Render service becomes Live | Pending |
| Public URL | Render assigns an HTTPS URL | Pending |
| Root endpoint | `/` returns service status JSON | Pending |
| Prediction | `/predict` returns valid prediction JSON | Pending |
| Logs | No repeated startup or runtime errors | Pending |
| Image update | Manual Deploy pulls the latest image | Pending |

## Security and best practices
- Use the minimum `read:packages` permission for Render to pull a private GHCR image.
- Never expose registry tokens, deploy hooks, or other secrets in code, reports, or screenshots.
- Deploy the image already tested in Practical-9.
- Record a commit-specific image tag or digest for traceability where practical.
- Do not submit real student personal data to a public classroom endpoint.

## Result
The practical is complete only after Render successfully pulls the GHCR image, the service becomes Live, and the deployed root, health, and prediction endpoints have been verified. Record the actual Render URL and screenshots after deployment.
