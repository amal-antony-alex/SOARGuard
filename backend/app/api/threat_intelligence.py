from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.threat_intelligence import ThreatIntelligence


router = APIRouter(
    prefix="/threat-intelligence",
    tags=["Threat Intelligence"]
)


# --------------------------------------------------
# GET THREAT INTELLIGENCE FOR AN ALERT
# --------------------------------------------------

@router.get("/alert/{alert_id}")
def get_threat_intelligence_for_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    records = (
        db.query(ThreatIntelligence)
        .filter(
            ThreatIntelligence.alert_id == alert_id
        )
        .order_by(
            ThreatIntelligence.id.desc()
        )
        .all()
    )

    return records


# --------------------------------------------------
# GET THREAT INTELLIGENCE HISTORY FOR AN IP
# --------------------------------------------------

@router.get("/ip/{ip_address}")
def get_threat_intelligence_for_ip(
    ip_address: str,
    db: Session = Depends(get_db)
):
    records = (
        db.query(ThreatIntelligence)
        .filter(
            ThreatIntelligence.ip_address == ip_address
        )
        .order_by(
            ThreatIntelligence.enriched_at.desc()
        )
        .all()
    )

    return records


# --------------------------------------------------
# GET THREAT INTELLIGENCE RECORD BY ID
# --------------------------------------------------

@router.get("/{threat_intelligence_id}")
def get_threat_intelligence_by_id(
    threat_intelligence_id: int,
    db: Session = Depends(get_db)
):
    record = (
        db.query(ThreatIntelligence)
        .filter(
            ThreatIntelligence.id == threat_intelligence_id
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Threat intelligence record not found"
        )

    return record