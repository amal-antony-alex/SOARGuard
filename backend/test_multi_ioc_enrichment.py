from app.services.ioc_extraction_service import (
    extract_iocs
)

from app.services.multi_ioc_enrichment_service import (
    enrich_all_iocs
)


sample_log = """
Connection detected from 8.8.8.8.

Suspicious domain:

example.com

Suspicious URL:

http://example.com/test

File hash:

44d88612fea8a8f36de82e1278abb02f
"""


extracted_iocs = extract_iocs(
    sample_log
)

print("Extracted IOCs:")
print(extracted_iocs)

print("\nEnrichment Results:")

enrichment_results = enrich_all_iocs(
    extracted_iocs
)

print(enrichment_results)