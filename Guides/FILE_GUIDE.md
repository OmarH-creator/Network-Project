# 📂 TinyTelemetry - Complete File Guide

**What every file does and when to use it!**

---

## 🎯 Files You Need to Read

### For Getting Started

| File | What It Is | When to Read |
|------|-----------|--------------|
| `QUICK_START.md` | 5-minute setup guide | **START HERE!** First time setup |
| `HOW_TO_USE_FOR_DUMMIES.md` | Complete beginner's guide | After quick start, for details |
| `README.md` | Main instructions | When you need usage examples |

### For Understanding

| File | What It Is | When to Read |
|------|-----------|--------------|
| `docs/simple-diagrams.md` | Visual diagrams | When you want to see how it works |
| `docs/project-proposal.md` | What & why | For understanding the project goals |
| `docs/mini-rfc.md` | Complete technical spec | For deep technical details |

### For Submission

| File | What It Is | When to Use |
|------|-----------|-------------|
| `SUBMISSION_READY.md` | Final checklist | Before submitting Phase 1 |
| `PHASE1_CHECKLIST.md` | Detailed checklist | To verify all requirements |
| `docs/demo-video-script.md` | Video recording guide | When recording your demo |

---

## 🔧 Files You Need to Run

### Main Code (src/ folder)

| File | What It Does | How to Run |
|------|-------------|------------|
| `src/server.py` | Collector server | `python -m src.server` |
| `src/client.py` | Sensor simulator | `python -m src.client --device-id 1001` |
| `src/protocol.py` | Encoding/decoding | (Used by server and client) |
| `src/metrics.py` | Statistics calculator | (Used by test scripts) |

### Test Scripts (scripts/ folder)

| File | What It Does | How to Run |
|------|-------------|------------|
| `scripts/test_baseline.py` | Automatic test | `python scripts/test_baseline.py` |
| `scripts/run_all_tests.py` | Run all tests | `python scripts/run_all_tests.py` |
| `scripts/generate_plots.py` | Make graphs | `python scripts/generate_plots.py` |
| `scripts/test_loss.sh` | Packet loss test | `sudo bash scripts/test_loss.sh` (Linux only) |
| `scripts/test_delay.sh` | Delay test | `sudo bash scripts/test_delay.sh` (Linux only) |

---

## 📊 Files That Are Generated

### Output Files (output/ folder)

| File Pattern | What It Contains | How to View |
|-------------|------------------|-------------|
| `*.csv` | Telemetry data logs | Excel, Notepad, any text editor |
| `*.json` | Performance metrics | Notepad, any text editor |
| `*.png` | Graphs and charts | Image viewer |
| `*.pcap` | Network packet captures | Wireshark (optional) |

**Example files you'll see:**
- `baseline_telemetry.csv` - Data from baseline test
- `baseline_metrics.json` - Statistics from baseline test
- `test_results.json` - Aggregated results from multiple tests

---

## 📝 Configuration Files

| File | What It Does | Should You Edit? |
|------|-------------|------------------|
| `requirements.txt` | Lists required packages | ❌ No, unless adding new packages |
| `README.txt` | Simple text readme | ✅ Yes, add your video link |
| `.gitignore` | Git ignore patterns | ❌ No need to edit |

---

## 📚 Documentation Files (docs/ folder)

### Phase 1 Required Documents

| File | Purpose | Page Limit | Status |
|------|---------|-----------|--------|
| `docs/project-proposal.md` | Project overview | 3 pages | ✅ Complete |
| `docs/mini-rfc.md` | Technical specification | No limit | ✅ Complete (9 sections) |

### Helper Documents

| File | Purpose |
|------|---------|
| `docs/demo-video-script.md` | Guide for recording demo |
| `docs/simple-diagrams.md` | Visual explanations |

---

## 🎯 Files by Use Case

### "I want to run a quick test"
1. `QUICK_START.md` - Read this first
2. Run: `python scripts/test_baseline.py --duration 30`
3. Check: `output/baseline_telemetry.csv`

### "I want to understand how it works"
1. `HOW_TO_USE_FOR_DUMMIES.md` - Complete guide
2. `docs/simple-diagrams.md` - Visual diagrams
3. `docs/mini-rfc.md` - Technical details

### "I want to record my demo video"
1. `docs/demo-video-script.md` - Follow this script
2. Record using the commands shown
3. Upload and add link to `README.md`

### "I want to submit Phase 1"
1. `SUBMISSION_READY.md` - Final checklist
2. `PHASE1_CHECKLIST.md` - Detailed verification
3. Package files and submit

### "Something went wrong"
1. `HOW_TO_USE_FOR_DUMMIES.md` - See Troubleshooting section
2. Check error message
3. Try suggested solutions

---

## 📦 What to Submit for Phase 1

### Required Files

```
✅ docs/project-proposal.md (or PDF)
✅ docs/mini-rfc.md (or PDF)
✅ README.md (with video link)
✅ README.txt (with video link)
✅ src/ folder (all Python files)
✅ scripts/ folder (all test scripts)
✅ output/ folder (at least one CSV file)
✅ requirements.txt
```

### Optional But Helpful

```
📄 HOW_TO_USE_FOR_DUMMIES.md
📄 QUICK_START.md
📄 docs/simple-diagrams.md
📄 SUBMISSION_READY.md
📄 PHASE1_CHECKLIST.md
```

---

## 🗂️ Complete File Tree

```
Network Project/
│
├── 📄 README.md                          ← Main instructions (EDIT: add video link)
├── 📄 README.txt                         ← Simple readme (EDIT: add video link)
├── 📄 requirements.txt                   ← Package list (don't edit)
│
├── 📁 guides/                            ← Beginner's guides folder
│   ├── 📄 README.md                      ← Guides index (START HERE!)
│   ├── 📄 QUICK_START.md                 ← 5-minute setup guide
│   ├── 📄 HOW_TO_USE_FOR_DUMMIES.md     ← Complete beginner's guide
│   ├── 📄 FILE_GUIDE.md                  ← This file!
│   ├── 📄 SUBMISSION_READY.md            ← Final checklist
│   └── 📄 PHASE1_CHECKLIST.md            ← Detailed checklist
│
├── 📁 src/                               ← Main code
│   ├── 📄 __init__.py
│   ├── 📄 protocol.py                    ← Encoding/decoding
│   ├── 📄 client.py                      ← Sensor simulator
│   ├── 📄 server.py                      ← Collector server
│   └── 📄 metrics.py                     ← Statistics
│
├── 📁 scripts/                           ← Test automation
│   ├── 📄 test_baseline.py               ← Automatic test (USE THIS!)
│   ├── 📄 run_all_tests.py               ← Run all tests
│   ├── 📄 generate_plots.py              ← Make graphs
│   ├── 📄 test_loss.sh                   ← Packet loss (Linux)
│   ├── 📄 test_delay.sh                  ← Delay test (Linux)
│   └── 📄 README.md                      ← Scripts documentation
│
├── 📁 docs/                              ← Documentation
│   ├── 📄 project-proposal.md            ← Phase 1 required
│   ├── 📄 mini-rfc.md                    ← Phase 1 required
│   ├── 📄 demo-video-script.md           ← Video guide
│   └── 📄 simple-diagrams.md             ← Visual diagrams
│
├── 📁 output/                            ← Generated results
│   ├── 📄 baseline_telemetry.csv         ← Test data
│   ├── 📄 baseline_metrics.json          ← Statistics
│   ├── 📄 test_results.json              ← Aggregated results
│   └── 📄 *.png                          ← Graphs (if generated)
│
└── 📁 .kiro/                             ← Kiro IDE config (ignore)
    └── specs/                            ← Project specs (ignore)
```

---

## 🎓 Reading Order for Beginners

### Day 1: Getting Started
1. `QUICK_START.md` (5 minutes)
2. Run your first test
3. Look at `output/baseline_telemetry.csv`

### Day 2: Understanding
1. `HOW_TO_USE_FOR_DUMMIES.md` (30 minutes)
2. `docs/simple-diagrams.md` (15 minutes)
3. Try running manual tests (server + client)

### Day 3: Deep Dive
1. `docs/project-proposal.md` (15 minutes)
2. `docs/mini-rfc.md` - Sections 1-3 (20 minutes)
3. Experiment with different settings

### Day 4: Preparation
1. `docs/demo-video-script.md` (10 minutes)
2. Practice running the demo
3. Prepare your recording setup

### Day 5: Demo & Submission
1. Record your demo video
2. Upload and add link to README.md
3. `SUBMISSION_READY.md` - Final checklist
4. Submit!

---

## 🔍 Finding Specific Information

### "How do I install Python?"
→ `HOW_TO_USE_FOR_DUMMIES.md` - Section "Installing Everything"

### "How do I run a test?"
→ `QUICK_START.md` or `HOW_TO_USE_FOR_DUMMIES.md` - Section "Running Your First Test"

### "What does this error mean?"
→ `HOW_TO_USE_FOR_DUMMIES.md` - Section "Troubleshooting"

### "How do I record the demo?"
→ `docs/demo-video-script.md`

### "What do I submit?"
→ `SUBMISSION_READY.md` - Section "What to Submit"

### "How does the protocol work?"
→ `docs/simple-diagrams.md` for visuals
→ `docs/mini-rfc.md` for technical details

### "What are all these CSV columns?"
→ `HOW_TO_USE_FOR_DUMMIES.md` - Section "Understanding What Happened"

### "How do I use batching?"
→ `README.md` - Section "Batching Decision Explanation"
→ `docs/simple-diagrams.md` - "Batching Comparison"

---

## 💡 Pro Tips

1. **Start with QUICK_START.md** - Get running in 5 minutes
2. **Keep HOW_TO_USE_FOR_DUMMIES.md open** - Reference it often
3. **Use docs/simple-diagrams.md** - Visual learner? This is for you!
4. **Check SUBMISSION_READY.md early** - Know what you need to do
5. **Save your test outputs** - You'll need at least one CSV file

---

## 🆘 Quick Help

**Can't find a file?**
- Use your file explorer's search function
- All files are in the "Network Project" folder

**Don't know which file to read?**
- Start with `QUICK_START.md`
- Then read `HOW_TO_USE_FOR_DUMMIES.md`

**Need to submit but don't know what?**
- Check `SUBMISSION_READY.md`
- Follow the checklist

**Want to understand the protocol?**
- Read `docs/simple-diagrams.md` first (visual)
- Then read `docs/mini-rfc.md` (technical)

---

**This guide should help you navigate all the files! 📂**

*Bookmark this page for quick reference!*
