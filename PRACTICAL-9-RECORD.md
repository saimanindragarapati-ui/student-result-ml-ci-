# Practical-9: Automate Docker Build, Test and GHCR Publish Using GitHub Actions

## Objective
Automate the build, runtime testing, and publication of the Student Result Prediction Docker image to GitHub Container Registry (GHCR) using GitHub Actions.

## Repository-specific configuration
- Repository: `saimanindragarapati-ui/student-result-ml-ci-`
- Workflow: `.github/workflows/docker-publish.yml`
- Trigger: push to `main` or manual `workflow_dispatch`
- GHCR image: `ghcr.io/saimanindragarapati-ui/student-result-ml`
- Container port: `5000`
- Health endpoint: `GET /health`
- Prediction endpoint: `POST /predict`
- Published tags: `latest` and `sha-<full-commit-SHA>`

## Experiment procedure
1. Confirm the Practical-8 application files and Dockerfile are committed to the repository.
2. Add `.github/workflows/docker-publish.yml` to the repository.
3. Ensure GitHub Actions is enabled.
4. In the existing GHCR package settings, open **Manage Actions access** and grant this repository **Write** access if it is not already listed.
5. Push the workflow file to `main`.
6. In the Actions tab, open **Student Result Prediction - Build, Test and Publish to GHCR**.
7. Confirm dependency installation, model generation, ML quality gate, unit tests, Docker build, container startup, health check, prediction smoke test, GHCR login, and both image pushes succeed.
8. Open GitHub Packages and verify `latest` and the matching `sha-<commit>` version.
9. Make a harmless README change and push it to `main`; verify a second run publishes a new commit-SHA tag and updates `latest`.

## Why the workflow trains the model
The repository's Dockerfile copies `student_result_model.pkl` and `metrics.json`, while `train_model.py` creates these files. A clean GitHub Actions checkout does not contain generated files unless they are committed. The workflow therefore runs `train_model.py` before the Docker build, keeping generated model artifacts out of source control while making the runner's build context complete.

## Security
The workflow declares only `contents: read` and `packages: write`, and authenticates using the automatically generated `GITHUB_TOKEN`. Do not add the Practical-8 personal access token to the workflow, repository files, Dockerfile, or logs. Since the package was created manually in Practical-8, confirm the repository has Write access under the package's **Manage Actions access** settings.

## Important adaptation from the handout
The handout's generic sample uses package name `student-result-prediction` and port `8000`. This repository uses the validated Practical-8 package `student-result-ml` and Flask port `5000`, so this experiment preserves the working project configuration and API contract.

## Observation table
| Checkpoint | Expected observation | Student record |
|---|---|---|
| Workflow file | `docker-publish.yml` exists under `.github/workflows` | Pending execution |
| Trigger | Push to `main` starts a workflow run | Pending execution |
| Model preparation | `train_model.py` creates model and metrics artifacts | Pending execution |
| Tests | Quality gate and unit tests pass | Pending execution |
| Docker build | Image builds on GitHub-hosted runner | Pending execution |
| Container test | Temporary container starts | Pending execution |
| Health gate | `GET /health` succeeds before publishing | Pending execution |
| Prediction test | Valid request returns PASS and code 1 | Pending execution |
| GHCR login | Workflow authenticates using `GITHUB_TOKEN` | Pending execution |
| Latest tag | Tested image is pushed as `latest` | Pending execution |
| SHA tag | `sha-<commit>` appears in GHCR | Pending execution |
| Second update | Later push triggers a second successful run | Pending execution |

## Evidence to capture
- Repository showing `.github/workflows/docker-publish.yml`.
- First successful Actions run, including Docker build and API health/prediction steps.
- GHCR login and push success logs (with no token exposed).
- GHCR package Versions showing `latest` and `sha-<commit>`.
- Second successful Actions run after a later README update.

## Result
The practical is complete only after the workflow has run successfully and the GHCR package shows the `latest` and commit-specific tags. The workflow is prepared here; fill in the observations and evidence only after the corresponding GitHub Actions run is verified.
