import json
from pathlib import Path

from fastapi.testclient import TestClient
from prometheus_client import generate_latest

from services.api.app import create_app

ROOT = Path(__file__).parents[1]


def test_api_metrics_endpoint_is_prometheus_compatible() -> None:
    client = TestClient(create_app())
    client.get("/metrics")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "platform_api_requests_total" in response.text
    assert "platform_api_request_duration_seconds" in response.text
    assert 'route="/metrics"' in response.text


def test_application_metric_names_are_low_cardinality() -> None:
    output = generate_latest().decode("utf-8")

    assert "platform_consumer_events_received_total" in output
    assert "platform_consumer_event_processing_duration_seconds" in output
    assert "event_id" not in output
    assert "correlation_id" not in output


def test_logging_context_is_json_and_excludes_credentials(capsys) -> None:
    from shared.logging import configure_logging, get_logger

    configure_logging()
    get_logger("observability-test").info(
        "request_completed", request_id="request-1", status_code=200
    )
    record = json.loads(capsys.readouterr().out)

    assert record["message"] == "request_completed"
    assert record["request_id"] == "request-1"
    assert "password" not in record
    assert "DATABASE_URL" not in record


def test_prometheus_configuration_names_all_required_targets() -> None:
    config = (ROOT / "observability" / "prometheus" / "prometheus.yml").read_text()
    alerts = (ROOT / "observability" / "prometheus" / "alerts.yml").read_text()

    for target in (
        "analytics-api:8000",
        "consumer:9101",
        "kafka-exporter:9308",
        "postgres-exporter:9187",
    ):
        assert target in config
    for alert in ("AnalyticsApiDown", "IngestionConsumerDown", "SustainedConsumerLag"):
        assert alert in alerts


def test_grafana_provisioning_contains_dashboard_and_prometheus_datasource() -> None:
    datasource = (
        ROOT
        / "observability"
        / "grafana"
        / "provisioning"
        / "datasources"
        / "prometheus.yml"
    )
    dashboard = ROOT / "observability" / "grafana" / "dashboards" / "platform-observability.json"

    assert "url: http://prometheus:9090" in datasource.read_text()
    dashboard_config = json.loads(dashboard.read_text())
    assert dashboard_config["title"] == "Cloud Data Platform Observability"
    assert len(dashboard_config["panels"]) >= 6
