TinyTelemetry v1.0 - Phase 1 Submission
========================================

DEMO VIDEO LINK
---------------
[INSERT YOUR VIDEO LINK HERE]

Please replace the placeholder above with your actual video link.
Ensure the video is set to "Anyone with the link can view".


PROJECT FILES
-------------
- docs/project-proposal.md    : Project proposal (max 3 pages)
- docs/mini-rfc.md            : Mini-RFC with sections 1-3
- README.md                   : Complete usage instructions
- src/server.py               : Collector server implementation
- src/client.py               : Sensor client implementation
- src/protocol.py             : Protocol encoding/decoding
- scripts/test_baseline.py    : Automated baseline test script


QUICK START
-----------
1. Install dependencies:
   pip install -r requirements.txt

2. Run automated baseline test:
   python scripts/test_baseline.py --duration 30

3. Or run manually:
   Terminal 1: python -m src.server
   Terminal 2: python -m src.client --device-id 1001 --duration 30


OUTPUT FILES
------------
- output/baseline_telemetry.csv   : CSV log with all received packets
- output/baseline_metrics.json    : Performance metrics


REQUIREMENTS
------------
- Python 3.7 or higher
- See requirements.txt for dependencies


CONTACT
-------
For questions or issues, please refer to the README.md file.
