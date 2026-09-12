from datetime import datetime

from sqlalchemy.orm import Session

from app.models.threat_intelligence import (
    ThreatIntelligence
)


def save_threat_intelligence(
    db: Session,
    alert_id: int,
    enrichment_result: dict
) -> ThreatIntelligence:
    """
    Save one IOC enrichment result
    into the database.
    """

    enriched_at = enrichment_result.get(
        "enriched_at"
    )

    if enriched_at:
        enriched_at = datetime.fromisoformat(
            enriched_at
        )
    else:
        enriched_at = datetime.utcnow()

    ioc_type = enrichment_result.get(
        "ioc_type",
        "ip"
    )

    ioc_value = enrichment_result.get(
        "ioc_value"
    )

    # Backward compatibility for older
    # IP enrichment results.
    if not ioc_value:
        ioc_value = enrichment_result.get(
            "ip_address"
        )

    threat_record = ThreatIntelligence(
        alert_id=alert_id,

        ioc_type=ioc_type,

        ioc_value=ioc_value,

        # Only populate IP address when
        # the IOC is an IP.
        ip_address=(
            ioc_value
            if ioc_type == "ip"
            else None
        ),

        reputation=enrichment_result.get(
            "reputation",
            "unknown"
        ),

        confidence_score=enrichment_result.get(
            "confidence_score",
            0
        ),

        malicious_detections=enrichment_result.get(
            "malicious_detections",
            0
        ),

        suspicious_detections=enrichment_result.get(
            "suspicious_detections",
            0
        ),

        harmless_detections=enrichment_result.get(
            "harmless_detections",
            0
        ),

        source=enrichment_result.get(
            "source",
            "Unknown"
        ),

        enriched_at=enriched_at
    )

    db.add(threat_record)
    db.commit()
    db.refresh(threat_record)

    return threat_record