import os
import base64
from datetime import datetime

import requests
from dotenv import load_dotenv


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()


VIRUSTOTAL_API_KEY = os.getenv(
    "VIRUSTOTAL_API_KEY"
)


# --------------------------------------------------
# HELPER FUNCTION
# DETERMINE REPUTATION
# --------------------------------------------------

def determine_reputation(
    malicious: int,
    suspicious: int
) -> str:
    """
    Determine IOC reputation based on
    VirusTotal detection statistics.
    """

    if malicious > 0:
        return "malicious"

    elif suspicious > 0:
        return "suspicious"

    return "unknown"


# --------------------------------------------------
# HELPER FUNCTION
# CALCULATE THREAT CONFIDENCE
# --------------------------------------------------

def calculate_confidence_score(
    malicious: int,
    suspicious: int,
    harmless: int
) -> float:
    """
    Calculate threat confidence percentage.
    """

    total = (
        malicious +
        suspicious +
        harmless
    )

    if total == 0:
        return 0

    return round(
        (
            (malicious + suspicious)
            / total
        ) * 100,
        2
    )


# ==================================================
# IP ADDRESS ENRICHMENT
# ==================================================

def enrich_ip_reputation(ip_address: str) -> dict:
    """
    Enrich an IP address using VirusTotal.

    Falls back to local intelligence if the API
    is unavailable or no API key is configured.
    """

    # --------------------------------------------------
    # LOCAL FALLBACK INTELLIGENCE
    # --------------------------------------------------

    known_malicious_ips = {
        "185.220.101.10": {
            "reputation": "malicious",
            "confidence_score": 95,
            "threat_type": "brute_force"
        },

        "203.0.113.20": {
            "reputation": "suspicious",
            "confidence_score": 70,
            "threat_type": "suspicious_login"
        }
    }

    # --------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------

    if not VIRUSTOTAL_API_KEY:

        local_result = known_malicious_ips.get(
            ip_address,
            {
                "reputation": "unknown",
                "confidence_score": 0,
                "threat_type": None
            }
        )

        return {
            "ioc_type": "ip",
            "ip_address": ip_address,
            "ioc_value": ip_address,
            **local_result,
            "source": (
                "SOARGuard Local Threat Intelligence"
            ),
            "enriched_at": datetime.utcnow().isoformat()
        }

    # --------------------------------------------------
    # VIRUSTOTAL API REQUEST
    # --------------------------------------------------

    url = (
        f"https://www.virustotal.com/api/v3/"
        f"ip_addresses/{ip_address}"
    )

    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        stats = (
            data["data"]["attributes"]
            ["last_analysis_stats"]
        )

        malicious = stats.get(
            "malicious",
            0
        )

        suspicious = stats.get(
            "suspicious",
            0
        )

        harmless = stats.get(
            "harmless",
            0
        )

        reputation = determine_reputation(
            malicious,
            suspicious
        )

        confidence_score = (
            calculate_confidence_score(
                malicious,
                suspicious,
                harmless
            )
        )

        return {
            "ioc_type": "ip",
            "ip_address": ip_address,
            "ioc_value": ip_address,
            "reputation": reputation,
            "confidence_score": confidence_score,
            "malicious_detections": malicious,
            "suspicious_detections": suspicious,
            "harmless_detections": harmless,
            "source": "VirusTotal",
            "enriched_at": datetime.utcnow().isoformat()
        }

    except requests.RequestException as error:

        # --------------------------------------------------
        # FALLBACK IF API FAILS
        # --------------------------------------------------

        local_result = known_malicious_ips.get(
            ip_address,
            {
                "reputation": "unknown",
                "confidence_score": 0,
                "threat_type": None
            }
        )

        return {
            "ioc_type": "ip",
            "ip_address": ip_address,
            "ioc_value": ip_address,
            **local_result,
            "source": "SOARGuard Local Fallback",
            "error": str(error),
            "enriched_at": datetime.utcnow().isoformat()
        }


# ==================================================
# DOMAIN ENRICHMENT
# ==================================================

def enrich_domain_reputation(domain: str) -> dict:
    """
    Enrich a domain using VirusTotal.
    """

    # --------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------

    if not VIRUSTOTAL_API_KEY:

        return {
            "ioc_type": "domain",
            "ioc_value": domain,
            "reputation": "unknown",
            "confidence_score": 0,
            "source": (
                "SOARGuard Local Threat Intelligence"
            ),
            "enriched_at": datetime.utcnow().isoformat()
        }

    # --------------------------------------------------
    # VIRUSTOTAL API REQUEST
    # --------------------------------------------------

    url = (
        f"https://www.virustotal.com/api/v3/"
        f"domains/{domain}"
    )

    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        stats = (
            data["data"]["attributes"]
            ["last_analysis_stats"]
        )

        malicious = stats.get(
            "malicious",
            0
        )

        suspicious = stats.get(
            "suspicious",
            0
        )

        harmless = stats.get(
            "harmless",
            0
        )

        reputation = determine_reputation(
            malicious,
            suspicious
        )

        confidence_score = (
            calculate_confidence_score(
                malicious,
                suspicious,
                harmless
            )
        )

        return {
            "ioc_type": "domain",
            "ioc_value": domain,
            "reputation": reputation,
            "confidence_score": confidence_score,
            "malicious_detections": malicious,
            "suspicious_detections": suspicious,
            "harmless_detections": harmless,
            "source": "VirusTotal",
            "enriched_at": datetime.utcnow().isoformat()
        }

    except requests.RequestException as error:

        return {
            "ioc_type": "domain",
            "ioc_value": domain,
            "reputation": "unknown",
            "confidence_score": 0,
            "source": "SOARGuard Local Fallback",
            "error": str(error),
            "enriched_at": datetime.utcnow().isoformat()
        }


# ==================================================
# URL ENRICHMENT
# ==================================================

def enrich_url_reputation(
    url_to_check: str
) -> dict:
    """
    Enrich a URL using VirusTotal.
    """

    # --------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------

    if not VIRUSTOTAL_API_KEY:

        return {
            "ioc_type": "url",
            "ioc_value": url_to_check,
            "reputation": "unknown",
            "confidence_score": 0,
            "source": (
                "SOARGuard Local Threat Intelligence"
            ),
            "enriched_at": datetime.utcnow().isoformat()
        }

    # --------------------------------------------------
    # CREATE VIRUSTOTAL URL ID
    # --------------------------------------------------

    url_id = (
        base64.urlsafe_b64encode(
            url_to_check.encode()
        )
        .decode()
        .strip("=")
    )

    api_url = (
        f"https://www.virustotal.com/api/v3/"
        f"urls/{url_id}"
    )

    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }

    try:

        response = requests.get(
            api_url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        stats = (
            data["data"]["attributes"]
            ["last_analysis_stats"]
        )

        malicious = stats.get(
            "malicious",
            0
        )

        suspicious = stats.get(
            "suspicious",
            0
        )

        harmless = stats.get(
            "harmless",
            0
        )

        reputation = determine_reputation(
            malicious,
            suspicious
        )

        confidence_score = (
            calculate_confidence_score(
                malicious,
                suspicious,
                harmless
            )
        )

        return {
            "ioc_type": "url",
            "ioc_value": url_to_check,
            "reputation": reputation,
            "confidence_score": confidence_score,
            "malicious_detections": malicious,
            "suspicious_detections": suspicious,
            "harmless_detections": harmless,
            "source": "VirusTotal",
            "enriched_at": datetime.utcnow().isoformat()
        }

    except requests.RequestException as error:

        return {
            "ioc_type": "url",
            "ioc_value": url_to_check,
            "reputation": "unknown",
            "confidence_score": 0,
            "source": "SOARGuard Local Fallback",
            "error": str(error),
            "enriched_at": datetime.utcnow().isoformat()
        }


# ==================================================
# FILE HASH ENRICHMENT
# ==================================================

def enrich_hash_reputation(
    file_hash: str
) -> dict:
    """
    Enrich a file hash using VirusTotal.
    """

    # --------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------

    if not VIRUSTOTAL_API_KEY:

        return {
            "ioc_type": "hash",
            "ioc_value": file_hash,
            "reputation": "unknown",
            "confidence_score": 0,
            "source": (
                "SOARGuard Local Threat Intelligence"
            ),
            "enriched_at": datetime.utcnow().isoformat()
        }

    # --------------------------------------------------
    # VIRUSTOTAL API REQUEST
    # --------------------------------------------------

    url = (
        f"https://www.virustotal.com/api/v3/"
        f"files/{file_hash}"
    )

    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        stats = (
            data["data"]["attributes"]
            ["last_analysis_stats"]
        )

        malicious = stats.get(
            "malicious",
            0
        )

        suspicious = stats.get(
            "suspicious",
            0
        )

        harmless = stats.get(
            "harmless",
            0
        )

        reputation = determine_reputation(
            malicious,
            suspicious
        )

        confidence_score = (
            calculate_confidence_score(
                malicious,
                suspicious,
                harmless
            )
        )

        return {
            "ioc_type": "hash",
            "ioc_value": file_hash,
            "reputation": reputation,
            "confidence_score": confidence_score,
            "malicious_detections": malicious,
            "suspicious_detections": suspicious,
            "harmless_detections": harmless,
            "source": "VirusTotal",
            "enriched_at": datetime.utcnow().isoformat()
        }

    except requests.RequestException as error:

        return {
            "ioc_type": "hash",
            "ioc_value": file_hash,
            "reputation": "unknown",
            "confidence_score": 0,
            "source": "SOARGuard Local Fallback",
            "error": str(error),
            "enriched_at": datetime.utcnow().isoformat()
        }