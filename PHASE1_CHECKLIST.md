# Phase 1 Deliverables Checklist

Use this checklist to verify all Phase 1 requirements are met before submission.

---

## ✅ Required Deliverables

### 1. Project Proposal (max 3 pages)

- [x] **File created:** `docs/project-proposal.md`
- [x] **Assigned scenario included:** IoT Telemetry Protocol
- [x] **Short motivation included:** Why TinyTelemetry is needed
- [x] **Proposed protocol approach included:** Loss-tolerant UDP design
- [x] **Page count:** ~3 pages (within limit)
- [ ] **Reviewed for clarity:** Read through and ensure it's clear
- [ ] **Ready to upload:** PDF or Markdown format acceptable

**Action:** Review `docs/project-proposal.md` and export to PDF if required by LMS.

---

### 2. Mini-RFC Draft (Sections 1-3)

- [x] **File created:** `docs/mini-rfc.md`
- [x] **Section 1 - Introduction:** Purpose, design goals, scope
- [x] **Section 2 - Protocol Architecture:** System components, communication model
- [x] **Section 3 - Message Formats:** Header table and field specifications
- [x] **Header table present:** 12-byte header with all fields documented
- [x] **Sample messages included:** Hex dumps with explanations
- [x] **Page count:** ~2.2 pages (under 3-page limit)

**Action:** No changes needed. File is complete.

---

### 3. Working Prototype

- [x] **Server implemented:** `src/server.py`
- [x] **Client implemented:** `src/client.py`
- [x] **Protocol library:** `src/protocol.py`
- [x] **UDP communication working:** Fire-and-forget model
- [x] **DATA messages working:** Sensor readings transmitted
- [x] **HEARTBEAT messages working:** Liveness indication (Note: called HEARTBEAT, not INIT)
- [x] **Multiple clients supported:** Server handles concurrent devices
- [x] **Code runs locally:** Tested on Windows (and should work on Linux)

**Action:** Test one more time to ensure everything works:
```bash
# Terminal 1
python -m src.server

# Terminal 2
python -m src.client --device-id 1001 --duration 30
```

---

### 4. README with Instructions

- [x] **File exists:** `README.md`
- [x] **Build instructions included:** Prerequisites and installation steps
- [x] **Run instructions included:** How to start server and client
- [x] **Usage examples included:** Multiple scenarios documented
- [x] **Clear and comprehensive:** Easy to follow
- [ ] **Demo video link added:** PLACEHOLDER - needs your actual link
- [ ] **Video link tested:** Verify it works in incognito/private browser

**Action:** 
1. Record your demo video (use `docs/demo-video-script.md` as guide)
2. Upload to YouTube (unlisted) or Google Drive
3. Replace `[INSERT YOUR VIDEO LINK HERE]` in README.md with actual link
4. Test the link in a private/incognito browser window

---

### 5. Demo Video (5 minutes)

- [ ] **Video recorded:** 5-minute demonstration
- [ ] **Content covers:**
  - [ ] Protocol overview and message format
  - [ ] Live server startup
  - [ ] Client sending DATA packets
  - [ ] Multiple concurrent clients (optional but impressive)
  - [ ] CSV logs generated
  - [ ] Automated baseline test running
- [ ] **Uploaded online:** YouTube, Google Drive, or similar
- [ ] **Access set correctly:** "Anyone with the link can view"
- [ ] **Link added to README:** In the Demo Video section
- [ ] **Link tested:** Works in incognito browser

**Action:** Follow the script in `docs/demo-video-script.md` to record your video.

**Suggested platforms:**
- **YouTube:** Upload as "Unlisted" video
- **Google Drive:** Upload and set sharing to "Anyone with the link"
- **OneDrive:** Similar sharing settings
- **Vimeo:** Free account with privacy settings

---

### 6. Automated Baseline Test Script

- [x] **Script exists:** `scripts/test_baseline.py`
- [x] **Runs automatically:** No manual intervention needed
- [x] **Starts server:** Automatically launches collector
- [x] **Starts client:** Automatically launches sensor
- [x] **Generates logs:** CSV file created in `output/`
- [x] **Calculates metrics:** Performance metrics computed
- [x] **Validation included:** Checks for ≥99% delivery and sequence order
- [x] **Works on your platform:** Tested on Windows

**Action:** Run one final test to verify:
```bash
python scripts/test_baseline.py --duration 30
```

Expected output:
- Server starts
- Client runs for 30 seconds
- Test completes with [PASS] indicators
- Files created: `output/baseline_telemetry.csv` and `output/baseline_metrics.json`

---

## 📋 Submission Checklist

Before uploading to LMS, verify:

- [ ] **Project proposal** (docs/project-proposal.md) - reviewed and ready
- [ ] **Mini-RFC** (docs/mini-rfc.md) - sections 1-3 complete
- [ ] **Source code** - all files in src/ directory
- [ ] **README** - with demo video link added
- [ ] **Demo video link** - tested and working
- [ ] **Baseline test script** - runs successfully
- [ ] **Sample logs** - at least one CSV file in output/ directory

---

## 🎯 Grading Criteria Alignment

### Proposal Clarity
- [x] Clear problem statement and motivation
- [x] Well-defined protocol approach
- [x] Feasibility demonstrated

### Initial Message Format Correctness
- [x] Header table with all required fields
- [x] Field sizes and types specified
- [x] Sample messages with hex dumps
- [x] Binary encoding documented

### Code Runs Locally
- [x] Server starts without errors
- [x] Client connects and sends data
- [x] No crashes or exceptions
- [x] Cross-platform compatible (Python 3.7+)

### Logs Present
- [x] CSV logs generated automatically
- [x] All required fields present (device_id, seq, timestamp, etc.)
- [x] Duplicate and gap detection visible in logs

### Demo Video Link
- [ ] **PENDING:** Need to record and upload video
- [ ] Link in README.md
- [ ] Accessible with "anyone with the link"

### Prototype Demonstrates Core Functionality
- [x] UDP communication working
- [x] Binary protocol encoding/decoding
- [x] DATA messages with sensor readings
- [x] Server receives and logs packets
- [x] Duplicate detection implemented
- [x] Gap detection implemented
- [x] Multiple clients supported

---

## 📝 Quick Start for Final Verification

Run these commands in sequence to verify everything works:

```bash
# 1. Clean previous outputs
rm output/*.csv output/*.json

# 2. Run automated baseline test
python scripts/test_baseline.py --duration 30

# 3. Verify output files exist
ls output/

# 4. Check CSV log has data
head output/baseline_telemetry.csv

# 5. Check metrics JSON
cat output/baseline_metrics.json
```

If all commands succeed, your prototype is ready!

---

## 🎬 Next Steps

1. **Record demo video** using `docs/demo-video-script.md`
2. **Upload video** to YouTube/Google Drive
3. **Add link** to README.md
4. **Test link** in incognito browser
5. **Final review** of all documents
6. **Package for submission** (ZIP or as specified by instructor)
7. **Upload to LMS**

---

## ✨ Bonus Points (Optional)

If you have extra time, consider adding:

- [ ] Screenshots in README showing the system running
- [ ] Diagram of protocol architecture
- [ ] Performance comparison table (TinyTelemetry vs JSON)
- [ ] Multiple test scenarios in demo video
- [ ] Code comments and docstrings review

---

**Good luck with your Phase 1 submission!**
