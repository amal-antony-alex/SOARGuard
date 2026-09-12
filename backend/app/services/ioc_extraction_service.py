import re


def clean_url(url: str) -> str:
    """
    Remove common punctuation that may appear
    at the end of a URL in a security log.
    """

    return url.rstrip(
        ".,;:!?)\"]}'"
    )


def extract_iocs(raw_log: str) -> dict:
    """
    Extract and normalize common Indicators
    of Compromise (IOCs) from a raw security log.
    """

    if not raw_log:
        return {
            "ips": [],
            "domains": [],
            "urls": [],
            "hashes": []
        }

    # --------------------------------------------------
    # IP ADDRESS EXTRACTION
    # --------------------------------------------------

    ip_pattern = (
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    )

    ips = sorted(
        set(
            re.findall(
                ip_pattern,
                raw_log
            )
        )
    )

    # --------------------------------------------------
    # URL EXTRACTION
    # --------------------------------------------------

    url_pattern = (
        r"https?://[^\s\"'<>]+"
    )

    raw_urls = re.findall(
        url_pattern,
        raw_log
    )

    urls = sorted(
        set(
            clean_url(url)
            for url in raw_urls
        )
    )

    # --------------------------------------------------
    # DOMAIN EXTRACTION
    # --------------------------------------------------

    domain_pattern = (
        r"\b(?:[a-zA-Z0-9-]+\.)+"
        r"[a-zA-Z]{2,}\b"
    )

    raw_domains = re.findall(
        domain_pattern,
        raw_log
    )

    domains = sorted(
        set(
            domain.lower()
            for domain in raw_domains
        )
    )

    # --------------------------------------------------
    # HASH EXTRACTION
    #
    # MD5      = 32 hexadecimal characters
    # SHA1     = 40 hexadecimal characters
    # SHA256   = 64 hexadecimal characters
    # --------------------------------------------------

    md5_pattern = (
        r"\b[a-fA-F0-9]{32}\b"
    )

    sha1_pattern = (
        r"\b[a-fA-F0-9]{40}\b"
    )

    sha256_pattern = (
        r"\b[a-fA-F0-9]{64}\b"
    )

    hashes = sorted(
        set(
            re.findall(
                md5_pattern,
                raw_log
            )
            +
            re.findall(
                sha1_pattern,
                raw_log
            )
            +
            re.findall(
                sha256_pattern,
                raw_log
            )
        )
    )

    return {
        "ips": ips,
        "domains": domains,
        "urls": urls,
        "hashes": hashes
    }