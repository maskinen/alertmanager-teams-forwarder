from fastapi import FastAPI, Request
from datetime import datetime, timezone
from elasticsearch import AsyncElasticsearch
import httpx
import os

app = FastAPI()

WEBHOOK_URL = os.getenv(
    "WEBHOOK_URL",
    "https://automation.example.com/webhook"
)

ES_HOST = os.getenv(
    "ES_HOST",
    "https://elasticsearch.example.com"
)

GRAFANA_URL = os.getenv(
    "GRAFANA_URL",
    "https://grafana.example.com"
)

ALERTMANAGER_URL = os.getenv(
    "ALERTMANAGER_URL",
    "https://alertmanager.example.com"
)

es = AsyncElasticsearch(
    [ES_HOST],
    api_key=os.getenv("ES_API_KEY"),
    verify_certs=False
)

@app.post("/alert")
async def receive_alert(request: Request):
    payload = await request.json()

    alerts = payload.get("alerts", [])

    for alert in alerts:
        alertname = alert["labels"].get("alertname", "Unknown")
        namespace = alert["labels"].get("namespace", "Unknown")
        severity = alert["labels"].get("severity", "Unknown")
        description = alert["annotations"].get("description", "No description")
        fingerprint = alert.get("fingerprint", "unknown")

        print(f"Alert: {alertname} | Fingerprint: {fingerprint}")

        card = {
            "type": "AdaptiveCard",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"Alert: {alertname}",
                    "weight": "bolder",
                    "size": "medium",
                    "wrap": True
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Namespace", "value": namespace},
                        {"title": "Severity", "value": severity},
                        {"title": "Tracking ID", "value": fingerprint},
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": description,
                    "wrap": True,
                    "isSubtle": True
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "View Alert",
                    "url": f"{ALERTMANAGER_URL}/#/alerts"
                },
                {
                    "type": "Action.OpenUrl",
                    "title": "View in Grafana",
                    "url": f"{GRAFANA_URL}/alerting/list"
                },
                {
                    "type": "Action.OpenUrl",
                    "title": "Silence Alert",
                    "url": f"{ALERTMANAGER_URL}/#/silences"
                }
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(WEBHOOK_URL, json=card)

            print(
                f"Webhook response: "
                f"{response.status_code} {response.text}"
            )

        index = (
            f"alertmanager-"
            f"{datetime.now(timezone.utc).strftime('%Y.%m.%d')}"
        )

        doc = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alertname": alertname,
            "namespace": namespace,
            "severity": severity,
            "description": description,
            "fingerprint": fingerprint,
            "teams_status": response.status_code
        }

        await es.index(index=index, document=doc)

        print(f"Logged to Elasticsearch index: {index}")

    return {"status": "ok"}

@app.on_event("shutdown")
async def shutdown():
    await es.close()