# alertmanager-teams-forwarder

Forwards monitoring alerts to a chat platform through an automation flow and stores alert data in Elasticsearch.

## Background

Legacy webhook integrations used by older chat platform connectors are being phased out. This service acts as a middleware layer that transforms Alertmanager webhook payloads into Adaptive Card-compatible payloads for automation workflows.

## Architecture

Monitoring system → Alert router → alertmanager-teams-forwarder → Automation flow → Chat platform  
                                                                             ↓  
                                                                     Elasticsearch

## Alert format in chat platform

Each alert is displayed as an Adaptive Card containing:
- Alert name
- Namespace
- Severity
- Description
- Tracking ID (fingerprint)

The card also includes actions for:
- View Alert
- View Dashboard
- Silence Alert

## Configuration

| Variable | Description |
|---|---|
| WEBHOOK_URL | Automation flow webhook URL |
| ES_HOST | Elasticsearch host URL |
| ES_API_KEY | Elasticsearch API key |
| DASHBOARD_URL | Dashboard base URL |
| ALERT_ROUTER_URL | Alert router base URL |

## Automation flow setup

To obtain a `WEBHOOK_URL`:

1. Create a new automation flow with an HTTP request trigger
2. Add an action that posts Adaptive Cards to a chat or channel
3. Forward the incoming payload to the Adaptive Card action
4. Save the flow and use the generated HTTP POST URL as `WEBHOOK_URL`

## Elasticsearch

Alerts are logged to Elasticsearch indices grouped by date.

## Files

- `docker/main.py` — FastAPI application
- `docker/Dockerfile` — Docker image definition
- `docker/pyproject.toml` — Python dependencies
- `docker/uv.lock` — Locked dependency versions
- `development/deployment.yaml` — Kubernetes deployment for development
- `development/service.yaml` — Kubernetes service for development
- `development/kustomization.yaml` — Kustomize config for development
- `production/deployment.values` — Kustomize patch for production
- `production/kustomization.yaml` — Kustomize config for production
- `application-dev.yaml` — ArgoCD application for development
- `application.yaml` — ArgoCD application for production
- `images.yaml` — Docker image tagging configuration