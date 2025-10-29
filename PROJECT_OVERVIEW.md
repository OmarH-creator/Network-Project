# 📋 TinyTelemetry v1.0 - Project Overview

**A complete guide to your project structure and documentation**

---

## 🎯 What is This Project?

TinyTelemetry v1.0 is a lightweight UDP-based protocol for IoT sensor telemetry. It allows small sensors to efficiently send temperature, humidity, and voltage readings to a central collector.

**Key Features:**
- Compact 12-byte binary header
- Fire-and-forget UDP messaging
- Duplicate and gap detection
- Timestamp-based reordering
- Optional batching for efficiency

---

## 📂 Project Structure

```
TinyTelemetry/
│
├── 🚀 START_HERE.md               ← New? Start here!
├── 📖 README.md                    ← Main documentation
├── 📋 PROJECT_OVERVIEW.md          ← This file
│
├── 📁 Guides/                      ← All beginner guides
│   ├── README.md                   ← Guides index
│   ├── QUICK_START.md              ← 5-minute setup
│   ├── HOW_TO_USE_FOR_DUMMIES.md  ← Complete tutorial
│   ├── FILE_GUIDE.md               ← File navigation
│   ├── simple-diagrams.md          ← Visual diagrams
│   ├── SUBMISSION_READY.md         ← Final checklist
│   └── PHASE1_CHECKLIST.md         ← Detailed verification
│
├── 📁 docs/                        ← Technical documentation
│   ├── project-proposal.md         ← Phase 1 required (3 pages)
│   ├── mini-rfc.md                 ← Phase 1 required (9 sections)
│   ├── demo-video-script.md        ← Video recording guide
│   └── simple-diagrams.md          ← Visual diagrams
│
├── 📁 src/                         ← Source code
│   ├── protocol.py                 ← Encoding/decoding
│   ├── client.py                   ← Sensor simulator
│   ├── server.py                   ← Collector server
│   └── metrics.py                  ← Statistics calculator
│
├── 📁 scripts/                     ← Test automation
│   ├── test_baseline.py            ← Automatic test
│   ├── run_all_tests.py            ← Run all tests
│   ├── generate_plots.py           ← Create graphs
│   ├── test_loss.sh                ← Packet loss (Linux)
│   └── test_delay.sh               ← Delay test (Linux)
│
├── 📁 output/                      ← Generated results
│   ├── *.csv                       ← Telemetry logs
│   ├── *.json                      ← Metrics
│   └── *.png                       ← Graphs
│
├── 📄 requirements.txt             ← Python packages
└── 📄 README.txt                   ← Simple readme
```

---

## 🎓 Documentation Guide

### For Beginners

**Start here:** [START_HERE.md](START_HERE.md)

Then explore the **[Guides/](Guides/)** folder:

| Guide | Purpose | Time |
|-------|---------|------|
| [Guides/QUICK_START.md](Guides/QUICK_START.md) | Get running fast | 5 min |
| [Guides/HOW_TO_USE_FOR_DUMMIES.md](Guides/HOW_TO_USE_FOR_DUMMIES.md) | Complete tutorial | 30 min |
| [Guides/FILE_GUIDE.md](Guides/FILE_GUIDE.md) | File navigation | 10 min |
| [Guides/simple-diagrams.md](Guides/simple-diagrams.md) | Visual diagrams | 15 min |
| [Guides/SUBMISSION_READY.md](Guides/SUBMISSION_READY.md) | Final checklist | 15 min |
| [Guides/PHASE1_CHECKLIST.md](Guides/PHASE1_CHECKLIST.md) | Detailed verification | 20 min |

### For Technical Details

**Technical documentation:** [docs/](docs/) folder

| Document | Purpose | Required for Phase 1 |
|----------|---------|---------------------|
| [docs/project-proposal.md](docs/project-proposal.md) | Project overview | ✅ Yes (3 pages) |
| [docs/mini-rfc.md](docs/mini-rfc.md) | Complete specification | ✅ Yes (9 sections) |
| [docs/demo-video-script.md](docs/demo-video-script.md) | Video guide | ✅ Yes (for demo) |
| [Guides/simple-diagrams.md](Guides/simple-diagrams.md) | Visual diagrams | ❌ No (but helpful) |

---

## 🚀 Quick Start Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Automatic Test
```bash
python scripts/test_baseline.py --duration 30
```

### Run Server Manually
```bash
python -m src.server
```

### Run Client Manually
```bash
python -m src.client --device-id 1001 --duration 30
```

---

## 📦 Phase 1 Deliverables

### Required Files

✅ **Documentation:**
- `docs/project-proposal.md` (or PDF)
- `docs/mini-rfc.md` (or PDF)
- `README.md` (with video link)
- `README.txt` (with video link)

✅ **Code:**
- `src/` folder (all Python files)
- `scripts/` folder (all test scripts)
- `requirements.txt`

✅ **Results:**
- `output/` folder (at least one CSV file)

✅ **Demo:**
- 5-minute video (uploaded online)
- Link added to README.md and README.txt

### Optional But Helpful

📄 All files in `Guides/` folder
📄 `START_HERE.md`
📄 `PROJECT_OVERVIEW.md` (this file)

---

## 🎯 Learning Path

### Week 1: Setup & Understanding
1. Read [START_HERE.md](START_HERE.md)
2. Follow [Guides/QUICK_START.md](Guides/QUICK_START.md)
3. Read [Guides/HOW_TO_USE_FOR_DUMMIES.md](Guides/HOW_TO_USE_FOR_DUMMIES.md)
4. Look at [Guides/simple-diagrams.md](Guides/simple-diagrams.md)

### Week 2: Experimentation
1. Run manual tests (server + client)
2. Try different settings
3. Examine CSV logs
4. Understand metrics

### Week 3: Documentation Review
1. Read [docs/project-proposal.md](docs/project-proposal.md)
2. Read [docs/mini-rfc.md](docs/mini-rfc.md)
3. Understand design decisions
4. Review code files

### Week 4: Demo Preparation
1. Read [docs/demo-video-script.md](docs/demo-video-script.md) or [Guides/simple-diagrams.md](Guides/simple-diagrams.md)
2. Practice running demo
3. Set up recording
4. Do practice recording

### Week 5: Submission
1. Record demo video
2. Upload and add link
3. Review [Guides/SUBMISSION_READY.md](Guides/SUBMISSION_READY.md)
4. Check [Guides/PHASE1_CHECKLIST.md](Guides/PHASE1_CHECKLIST.md)
5. Package and submit

---

## 🎬 Demo Video Requirements

**Length:** 5 minutes

**Content:**
1. Introduction (30 sec) - What is TinyTelemetry?
2. Protocol explanation (1 min) - Show message format
3. Live demo (1.5 min) - Run server and client
4. Results (1 min) - Show CSV logs
5. Automated test (45 sec) - Run baseline test

**Upload to:**
- YouTube (unlisted)
- Google Drive
- OneDrive

**Add link to:**
- `README.md`
- `README.txt`

**Guide:** [docs/demo-video-script.md](docs/demo-video-script.md)

---

## 🔧 Common Tasks

### Running Tests

**Automatic test (recommended):**
```bash
python scripts/test_baseline.py --duration 30
```

**Manual test:**
```bash
# Terminal 1
python -m src.server

# Terminal 2
python -m src.client --device-id 1001 --duration 30
```

### Viewing Results

**CSV logs:**
- Open `output/baseline_telemetry.csv` in Excel or text editor

**Metrics:**
- Open `output/baseline_metrics.json` in text editor

### Generating Plots

```bash
python scripts/generate_plots.py
```

---

## 🆘 Troubleshooting

### Installation Issues

**"Python is not recognized"**
→ Install from https://www.python.org/downloads/
→ Check "Add Python to PATH" during installation

**"No module named 'matplotlib'"**
→ Run: `pip install -r requirements.txt`

### Runtime Issues

**"Address already in use"**
→ Use different port: `python -m src.server --port 5001`

**Test fails**
→ Try longer duration: `python scripts/test_baseline.py --duration 60`

**CSV file empty**
→ Check firewall settings
→ Ensure server and client use same port

### Full Troubleshooting Guide

See [Guides/HOW_TO_USE_FOR_DUMMIES.md](Guides/HOW_TO_USE_FOR_DUMMIES.md) - Section "Troubleshooting"

---

## 📊 Key Metrics

**What to look for in results:**

| Metric | Good Value | What It Means |
|--------|-----------|---------------|
| Delivery Rate | ≥99% | Percentage of messages received |
| Duplicate Rate | 0% | No duplicate messages |
| Sequence Gaps | 0 | No missing messages |
| Bytes per Report | ~9-18 | Efficient message size |

---

## 🎓 Key Concepts

| Concept | Simple Explanation |
|---------|-------------------|
| **Protocol** | Rules for communication |
| **UDP** | Fast but unreliable messaging |
| **Binary Encoding** | Data as numbers, not text |
| **Sequence Number** | Message counter (0, 1, 2...) |
| **Duplicate** | Same message twice |
| **Gap** | Missing message |
| **Batching** | Multiple readings in one message |
| **Fire-and-Forget** | Send without waiting for reply |

---

## 📚 Additional Resources

### In This Project

- [Guides/](Guides/) - All beginner guides
- [docs/](docs/) - Technical documentation
- [README.md](README.md) - Main instructions

### External Resources

- Python: https://www.python.org/
- UDP Protocol: https://en.wikipedia.org/wiki/User_Datagram_Protocol
- Binary Encoding: https://en.wikipedia.org/wiki/Binary_code

---

## ✅ Pre-Submission Checklist

- [ ] Python 3.7+ installed
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] Test runs successfully
- [ ] CSV log file exists in `output/`
- [ ] Demo video recorded (5 minutes)
- [ ] Video uploaded (YouTube/Google Drive)
- [ ] Video link added to README.md
- [ ] Video link added to README.txt
- [ ] Video link tested (works in incognito browser)
- [ ] All required files present
- [ ] Files packaged (ZIP or as specified)

**Full checklist:** [Guides/SUBMISSION_READY.md](Guides/SUBMISSION_READY.md)

---

## 🎉 You're Ready!

Everything you need is organized and ready:

1. **Beginner guides** → [Guides/](Guides/) folder
2. **Technical docs** → [docs/](docs/) folder
3. **Working code** → [src/](src/) folder
4. **Test scripts** → [scripts/](scripts/) folder

**Start with [START_HERE.md](START_HERE.md) and follow the Guides!**

**Good luck with Phase 1! 🚀**

---

## 📞 Need Help?

1. Check [Guides/HOW_TO_USE_FOR_DUMMIES.md](Guides/HOW_TO_USE_FOR_DUMMIES.md)
2. Look at [Guides/FILE_GUIDE.md](Guides/FILE_GUIDE.md)
3. Review [Guides/simple-diagrams.md](Guides/simple-diagrams.md)
4. Ask your instructor

**You've got this!** 💪
