from fastapi import FastAPI

from app.database.database import Base, engine

from app.models.incident import Incident

from fastapi.middleware.cors import CORSMiddleware

# ==================================================
# IMPORT DATABASE MODELS
# ==================================================

from app.models.alert import Alert

from app.models.playbook_execution import (
    PlaybookExecution
)

from app.models.playbook_action import (
    PlaybookAction
)

from app.models.threat_intelligence import (
    ThreatIntelligence
)

from app.models.approval_decision import (
    ApprovalDecision
)
from app.models.incident import Incident


# ==================================================
# IMPORT API ROUTERS
# ==================================================

from app.api.alerts import router as alerts_router

from app.api.playbooks import (
    router as playbooks_router
)

from app.api.threat_intelligence import (
    router as threat_intelligence_router
)
from app.api.incidents import (
    router as incidents_router
)
from app.api.incidents import (
    router as incidents_router
)
from app.api.dashboard import router as dashboard_router

# ==================================================
# CREATE DATABASE TABLES
# ==================================================

Base.metadata.create_all(
    bind=engine
)


# ==================================================
# CREATE FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="SOARGuard API",
    description=(
        "Automated SOC Incident Response and "
        "Playbook Orchestration Platform"
    ),
    version="0.1.0"
)


# ==================================================
# ENABLE CORS FOR FRONTEND
# ==================================================

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# BASIC API ENDPOINTS
# ==================================================

@app.get("/")
def root():

    return {
        "message": "Welcome to SOARGuard",
        "status": "running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# ==================================================
# REGISTER API ROUTERS
# ==================================================

app.include_router(alerts_router)
app.include_router(playbooks_router)
app.include_router(
    threat_intelligence_router
)
app.include_router(incidents_router)
app.include_router(dashboard_router)