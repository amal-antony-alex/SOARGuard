from app.schemas.alert import AlertCreate


def normalize_alert(alert: AlertCreate) -> dict:
    """
    Convert an incoming security alert into
    SOARGuard's standardized internal format.
    """

    normalized_alert = {
        "source": alert.source.strip().lower(),

        "event_type": (
            alert.event_type.strip().lower()
        ),

        "severity": alert.severity.value,

        "source_ip": (
            alert.source_ip.strip()
            if alert.source_ip
            else None
        ),

        "destination_ip": (
            alert.destination_ip.strip()
            if alert.destination_ip
            else None
        ),

        "raw_log": alert.raw_log.strip(),

        # Keep this as a Python datetime object
        # for SQLAlchemy and SQLite.
        "timestamp": alert.timestamp
    }

    return normalized_alert