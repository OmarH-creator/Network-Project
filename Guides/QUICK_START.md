# ⚡ TinyTelemetry - 5-Minute Quick Start

**Goal:** Get TinyTelemetry running in 5 minutes or less!

---

## ✅ Prerequisites Check (30 seconds)

Open terminal and run:
```bash
python --version
```

**See Python 3.7+?** ✅ Continue!  
**See an error?** ❌ [Install Python](https://www.python.org/downloads/) first, then come back.

---

## 📥 Step 1: Install Packages (1 minute)

Navigate to your project folder:
```bash
cd "C:\Users\YourName\Desktop\Network Project"
```

Install requirements:
```bash
pip install -r requirements.txt
```

Wait for "Successfully installed..." message.

---

## 🚀 Step 2: Run Your First Test (2 minutes)

Run the automatic test:
```bash
python scripts/test_baseline.py --duration 30
```

**What you'll see:**
```
============================================================
BASELINE TEST
============================================================
[1/4] Starting collector server...
[2/4] Waiting for server to be ready...
[3/4] Starting sensor client...
[4/4] Client completed. Stopping server...
...
[PASS] BASELINE TEST PASSED
```

**Success!** ✅ Your test passed!

---

## 📊 Step 3: Check the Results (1 minute)

Open the output folder and look for:
- `baseline_telemetry.csv` - All the data
- `baseline_metrics.json` - Statistics

**Open the CSV in Excel or Notepad** to see the logged messages!

---

## 🎉 Done!

You just:
1. ✅ Installed TinyTelemetry
2. ✅ Ran a complete test
3. ✅ Generated results

**Next steps:**
- Read `HOW_TO_USE_FOR_DUMMIES.md` for detailed explanations
- Look at `docs/simple-diagrams.md` for visual guides
- Check `SUBMISSION_READY.md` for what to submit

---

## 🆘 Something Went Wrong?

**"Python is not recognized"**
→ Install Python from https://www.python.org/downloads/

**"No module named 'matplotlib'"**
→ Run: `pip install matplotlib`

**"Address already in use"**
→ Use different port: `python -m src.server --port 5001`

**Test failed**
→ Try again with longer duration: `python scripts/test_baseline.py --duration 60`

**Still stuck?**
→ See full troubleshooting in `HOW_TO_USE_FOR_DUMMIES.md`

---

## 📝 Quick Commands Reference

```bash
# Install packages
pip install -r requirements.txt

# Run automatic test (30 seconds)
python scripts/test_baseline.py --duration 30

# Run automatic test (60 seconds)
python scripts/test_baseline.py --duration 60

# Start server manually
python -m src.server

# Start client manually (in another terminal)
python -m src.client --device-id 1001 --duration 30

# Check Python version
python --version

# List output files
dir output        # Windows
ls output         # Mac/Linux
```

---

## 🎯 What to Do for Phase 1

1. ✅ Run the test (you just did this!)
2. ⏳ Record a 5-minute demo video
3. ⏳ Upload video and add link to README.md
4. ⏳ Submit all files to your instructor

**See `SUBMISSION_READY.md` for complete checklist!**

---

**You're off to a great start! 🚀**
