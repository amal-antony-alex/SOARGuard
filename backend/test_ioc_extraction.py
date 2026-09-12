from app.services.ioc_extraction_service import (
    extract_iocs
)


sample_log = """
Suspicious connection detected from 185.220.101.10.

The endpoint contacted:

http://malicious-example.com/payload

Additional communication was detected with
evil-domain.net.

Suspicious file hash:

44d88612fea8a8f36de82e1278abb02f
"""


result = extract_iocs(
    sample_log
)

print(result)