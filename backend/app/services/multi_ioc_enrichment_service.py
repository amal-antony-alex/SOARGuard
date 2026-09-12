from app.services.threat_intelligence_service import (
    enrich_ip_reputation,
    enrich_domain_reputation,
    enrich_url_reputation,
    enrich_hash_reputation
)


def enrich_all_iocs(extracted_iocs: dict) -> dict:
    """
    Enrich all IOC types extracted from
    a security log.
    """

    results = {
        "ips": [],
        "domains": [],
        "urls": [],
        "hashes": []
    }

    # Enrich IPs
    for ip_address in extracted_iocs.get("ips", []):
        results["ips"].append(
            enrich_ip_reputation(ip_address)
        )

    # Enrich Domains
    for domain in extracted_iocs.get(
        "domains",
        []
    ):
        results["domains"].append(
            enrich_domain_reputation(domain)
        )

    # Enrich URLs
    for url in extracted_iocs.get("urls", []):
        results["urls"].append(
            enrich_url_reputation(url)
        )

    # Enrich Hashes
    for file_hash in extracted_iocs.get(
        "hashes",
        []
    ):
        results["hashes"].append(
            enrich_hash_reputation(file_hash)
        )

    return results
