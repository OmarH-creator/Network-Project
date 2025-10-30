# 🎓 TinyTelemetry - Complete Beginner's Guide (Phase 1)

**Welcome!** This guide will walk you through EVERYTHING you need to know about TinyTelemetry, step by step, like you're 7 years old. No prior knowledge needed!

---

## 📚 Table of Contents

1. [What is TinyTelemetry?](#what-is-tinytelemetry)
2. [What You Need (Prerequisites)](#what-you-need)
3. [Installing Everything](#installing-everything)
4. [Understanding the Project Files](#understanding-the-project-files)
5. [Running Your First Test](#running-your-first-test)
6. [Understanding What Happened](#understanding-what-happened)
7. [Recording Your Demo Video](#recording-your-demo-video)
8. [Submitting Phase 1](#submitting-phase-1)
9. [Troubleshooting](#troubleshooting)

**💡 Tip:** For visual diagrams and illustrations, see `../Guides/simple-diagrams.md`!

**📚 All guides are in the `guides/` folder** - You're reading one now!

---

## 🤔 What is TinyTelemetry?

### The Simple Explanation

Imagine you have a thermometer in your room that measures temperature. Instead of you walking to the thermometer to check it, the thermometer **sends** the temperature to your phone automatically every few seconds.

TinyTelemetry is like that, but for computers!

### The Slightly Technical Explanation

TinyTelemetry is a **protocol** (a set of rules) that lets small sensors (like temperature sensors) send their readings to a central computer over the internet.

**Think of it like this:**
- **Sensor (Client)** = A thermometer that can talk
- **Collector (Server)** = A notebook that writes down what the thermometer says
- **Protocol** = The language they use to talk to each other

### What Makes TinyTelemetry Special?

1. **Super Small Messages**: Instead of sending "The temperature is 25 degrees", it sends tiny codes that mean the same thing but use less space
2. **Fire and Forget**: The sensor doesn't wait for a reply - it just sends and moves on (like throwing a paper airplane)
3. **Handles Mistakes**: If some messages get lost (like paper airplanes that don't reach), the notebook notices and writes "message missing"

---

## 🛠️ What You Need

### Required Software

1. **Python 3.7 or newer**
   - This is the programming language TinyTelemetry is written in
   - Think of it like the "engine" that makes everything work

2. **A Text Editor or IDE**
   - To view and edit code files
   - Examples: VS Code, Notepad++, or even regular Notepad

3. **A Terminal/Command Prompt**
   - This is where you type commands to run the program
   - Windows: Command Prompt or PowerShell
   - Mac/Linux: Terminal

4. **Internet Connection** (for installing packages)

### Optional (But Helpful)

1. **Screen Recording Software**
   - For recording your demo video
   - Windows: Xbox Game Bar (built-in), OBS Studio (free)
   - Mac: QuickTime Player (built-in), OBS Studio (free)

2. **YouTube or Google Drive Account**
   - To upload your demo video

---

## 💻 Installing Everything

### Step 1: Check if Python is Installed

**Windows:**
1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. Type: `python --version`
4. Press Enter

**Mac/Linux:**
1. Open Terminal
2. Type: `python3 --version`
3. Press Enter

**What You Should See:**
```
Python 3.7.0 (or higher)
```

**If you see an error:**
- Go to https://www.python.org/downloads/
- Download Python 3.7 or newer
- Install it (check "Add Python to PATH" during installation!)
- Restart your computer
- Try again

### Step 2: Navigate to Your Project Folder

**Windows:**
```cmd
cd C:\Users\YourName\Desktop\Network Project
```

**Mac/Linux:**
```bash
cd ~/Desktop/Network\ Project
```

**Tip:** You can drag the folder into the terminal window to auto-fill the path!

### Step 3: Install Required Packages

Type this command and press Enter:

```bash
pip install -r requirements.txt
```

**What this does:**
- Reads the `requirements.txt` file
- Installs all the packages TinyTelemetry needs
- Like downloading all the tools before building something

**What You Should See:**
```
Successfully installed matplotlib-3.x.x ...
```

**If you see an error:**
- Try: `pip3 install -r requirements.txt`
- Or: `python -m pip install -r requirements.txt`

### Step 4: Verify Installation

Type this command:

```bash
python -c "import matplotlib, socket, struct"
```

**If nothing happens (no error):** ✅ Success! Everything is installed!

**If you see an error:** ❌ Something went wrong. See [Troubleshooting](#troubleshooting)

---

## 📁 Understanding the Project Files

Let's look at what each file does. Think of it like understanding the parts of a toy before playing with it.

### Main Folders

```
Network Project/
├── src/                    ← The "brain" - main code
├── scripts/                ← The "helpers" - test scripts
├── docs/                   ← The "manual" - documentation
├── output/                 ← The "results" - where data is saved
└── requirements.txt        ← The "shopping list" - what to install
```

### Important Files Explained

#### 1. `src/server.py` - The Collector (Notebook)

**What it does:**
- Listens for messages from sensors
- Writes down everything it receives
- Detects if messages are missing or duplicated

**Think of it as:** A person sitting with a notebook, writing down everything they hear

**How to use it:**
```bash
python -m src.server
```

#### 2. `src/client.py` - The Sensor (Thermometer)

**What it does:**
- Pretends to be a temperature/humidity/voltage sensor
- Generates fake readings (like 25°C, 50% humidity)
- Sends readings to the server

**Think of it as:** A talking thermometer that shouts out temperatures

**How to use it:**
```bash
python -m src.client --device-id 1001 --duration 30
```

#### 3. `src/protocol.py` - The Language Rules

**What it does:**
- Defines how to encode messages (turn words into codes)
- Defines how to decode messages (turn codes back into words)

**Think of it as:** A dictionary that translates between English and "sensor language"

**You don't run this directly** - it's used by server.py and client.py

#### 4. `scripts/test_baseline.py` - The Automatic Tester

**What it does:**
- Starts the server automatically
- Starts a client automatically
- Runs a test
- Checks if everything worked correctly
- Gives you a PASS or FAIL grade

**Think of it as:** A robot teacher that runs your experiment and grades it

**How to use it:**
```bash
python scripts/test_baseline.py --duration 30
```

#### 5. `output/` Folder - Where Results Are Saved

**What's inside:**
- `*.csv` files - Spreadsheets with all the data
- `*.json` files - Reports with statistics
- `*.png` files - Graphs and charts (if you make them)

**Think of it as:** Your homework folder where all your results go

#### 6. `docs/` Folder - The Instruction Manuals

**What's inside:**
- `project-proposal.md` - Explains what you're building and why
- `mini-rfc.md` - The complete technical manual (9 sections)
- `demo-video-script.md` - Script for your video

**Think of it as:** The instruction booklet that came with a toy

---

## 🚀 Running Your First Test

Let's actually run TinyTelemetry! We'll do this in 3 ways, from easiest to most detailed.

### Method 1: The Super Easy Way (Automatic Test)

This is the **easiest** way. One command does everything!

**Step 1:** Open your terminal/command prompt

**Step 2:** Navigate to your project folder
```bash
cd "C:\Users\YourName\Desktop\Network Project"
```

**Step 3:** Run the automatic test
```bash
python scripts/test_baseline.py --duration 30
```

**Step 4:** Watch the magic happen!

**What You'll See:**
```
============================================================
BASELINE TEST
============================================================
Device ID: 1001
Interval: 1s
Duration: 30s
...
[1/4] Starting collector server...
[2/4] Waiting for server to be ready...
[3/4] Starting sensor client...
[4/4] Client completed. Stopping server...
...
[PASS] BASELINE TEST PASSED
```

**What Just Happened?**
1. The script started a server (the notebook)
2. The script started a client (the thermometer)
3. The client sent 30 messages (one per second for 30 seconds)
4. The server wrote them all down
5. The script checked if everything worked
6. You got a PASS! 🎉

**Where Are the Results?**
- Look in the `output/` folder
- You'll see `baseline_telemetry.csv` (the data)
- And `baseline_metrics.json` (the statistics)

---

### Method 2: The Manual Way (Two Terminals)

This way lets you see both the server and client running at the same time.

**Step 1:** Open TWO terminal windows (side by side is best)

**Step 2:** In Terminal 1 (Left), start the server:
```bash
cd "C:\Users\YourName\Desktop\Network Project"
python -m src.server
```

**What You'll See:**
```
CollectorServer initialized on port 5000
Logging to: output\telemetry.csv
CollectorServer running. Press Ctrl+C to stop.
```

**Step 3:** In Terminal 2 (Right), start the client:
```bash
cd "C:\Users\YourName\Desktop\Network Project"
python -m src.client --device-id 1001 --duration 30
```

**What You'll See:**
```
[INFO] Starting sensor client (device_id=1001)
[INFO] Server: localhost:5000
[INFO] Interval: 1s, Duration: 30s
[DATA] seq=0, timestamp=..., readings=3, bytes=28
[DATA] seq=1, timestamp=..., readings=3, bytes=28
...
```

**Step 4:** Watch both terminals!
- **Left (Server):** Shows "Initialized state for device 1001"
- **Right (Client):** Shows each message being sent

**Step 5:** After 30 seconds, the client stops automatically

**Step 6:** In Terminal 1 (Server), press `Ctrl+C` to stop the server

**What Just Happened?**
- You manually controlled both parts
- You could see them talking to each other in real-time
- The server saved everything to `output/telemetry.csv`

---

### Method 3: The Detailed Way (With Custom Settings)

This way lets you customize everything!

**Start the server with custom settings:**
```bash
python -m src.server --port 5000 --log-file output/my_test.csv
```

**Start the client with custom settings:**
```bash
python -m src.client --device-id 2001 --server-host localhost --server-port 5000 --interval 5 --duration 60 --batch-size 10
```

**What These Settings Mean:**
- `--device-id 2001` - This sensor's ID number (like a name tag)
- `--server-host localhost` - Where the server is (localhost = same computer)
- `--server-port 5000` - Which "door" to use (like an apartment number)
- `--interval 5` - Send a message every 5 seconds (instead of 1)
- `--duration 60` - Run for 60 seconds total
- `--batch-size 10` - Send 10 readings at once (instead of 1)

**Try Different Settings:**
```bash
# Fast sensor (every 1 second)
python -m src.client --device-id 1001 --interval 1 --duration 30

# Slow sensor (every 30 seconds)
python -m src.client --device-id 1002 --interval 30 --duration 120

# Batched sensor (10 readings per message)
python -m src.client --device-id 1003 --interval 1 --duration 60 --batch-size 10
```

---

## 🔍 Understanding What Happened

After running a test, let's look at the results!

### Looking at the CSV File

**Step 1:** Open `output/baseline_telemetry.csv` in Excel or a text editor

**What You'll See:**
```csv
device_id,seq,timestamp,arrival_time,msg_type,duplicate_flag,gap_flag,gap_size,reading_count
1001,0,1698765432,1698765432.123456,DATA,False,False,0,3
1001,1,1698765433,1698765433.125678,DATA,False,False,0,3
1001,2,1698765434,1698765434.127890,DATA,False,False,0,3
```

**What Each Column Means:**

| Column | What It Means | Example |
|--------|---------------|---------|
| `device_id` | Which sensor sent this | 1001 |
| `seq` | Message number (0, 1, 2, 3...) | 0 |
| `timestamp` | When the sensor sent it | 1698765432 |
| `arrival_time` | When the server received it | 1698765432.123456 |
| `msg_type` | Type of message | DATA or HEARTBEAT |
| `duplicate_flag` | Is this a duplicate? | False (usually) |
| `gap_flag` | Was a message missing before this? | False (usually) |
| `gap_size` | How many messages were missing | 0 (usually) |
| `reading_count` | How many sensor readings in this message | 3 |

**Reading the Data Like a Story:**
```
Row 1: Device 1001 sent message #0 at time 1698765432
       Server received it 0.123456 seconds later
       It was a DATA message with 3 readings
       No duplicates, no gaps - everything good!

Row 2: Device 1001 sent message #1 at time 1698765433
       (1 second after the first message)
       Everything still good!

Row 3: Device 1001 sent message #2...
       And so on...
```

### Looking at the JSON Metrics

**Step 1:** Open `output/baseline_metrics.json` in a text editor

**What You'll See:**
```json
{
  "test_scenario": "baseline",
  "duration_seconds": 30,
  "metrics": {
    "bytes_per_report": 9.33,
    "packets_received": 30,
    "packets_sent": 30,
    "duplicate_rate": 0.0,
    "sequence_gap_count": 0,
    "delivery_rate": 1.0
  }
}
```

**What Each Metric Means:**

| Metric | What It Means | Good Value |
|--------|---------------|------------|
| `bytes_per_report` | Average size of each reading | Lower is better (9.33 is great!) |
| `packets_received` | How many messages the server got | Should match packets_sent |
| `packets_sent` | How many messages the client sent | 30 (in this example) |
| `duplicate_rate` | Percentage of duplicate messages | 0.0 (0%) is perfect |
| `sequence_gap_count` | How many messages were lost | 0 is perfect |
| `delivery_rate` | Percentage of messages that arrived | 1.0 (100%) is perfect |

**Interpreting the Results:**
```
✅ delivery_rate = 1.0 means 100% of messages arrived (perfect!)
✅ duplicate_rate = 0.0 means no duplicates (perfect!)
✅ sequence_gap_count = 0 means no messages were lost (perfect!)
✅ bytes_per_report = 9.33 means very efficient (small messages!)
```

### What If Something Went Wrong?

**Example: A Message Was Lost**
```csv
device_id,seq,timestamp,arrival_time,msg_type,duplicate_flag,gap_flag,gap_size,reading_count
1001,0,1698765432,1698765432.123456,DATA,False,False,0,3
1001,1,1698765433,1698765433.125678,DATA,False,False,0,3
1001,3,1698765435,1698765435.127890,DATA,False,True,1,3
```

**Notice:** seq jumped from 1 to 3 (skipped 2!)
- `gap_flag` = True (yes, there's a gap)
- `gap_size` = 1 (one message is missing)

**This is OK!** TinyTelemetry is designed to handle lost messages. The server noticed and recorded it.

---

## 🎥 Recording Your Demo Video

Now for the fun part - showing off your work!

### What You Need to Show (5 Minutes Total)

**Minute 1 (0:00-1:00): Introduction**
- Say hello and introduce TinyTelemetry
- Show the project folder structure
- Explain what the protocol does (sensors sending data)

**Minute 2 (1:00-2:00): Protocol Explanation**
- Open `docs/mini-rfc.md`
- Show the header format (12 bytes)
- Show a sample message with hex dump
- Explain why binary is better than JSON

**Minutes 3-4 (2:00-4:00): Live Demo**
- Open two terminals side by side
- Start the server in one terminal
- Start the client in the other terminal
- Let it run for 10-15 seconds
- Show the messages being sent and received
- Stop both programs

**Minute 5 (4:00-5:00): Results**
- Open the CSV file in Excel or text editor
- Point out the columns (device_id, seq, etc.)
- Show that all messages arrived (no gaps)
- Run the automatic test: `python scripts/test_baseline.py --duration 15`
- Show the [PASS] result

### Recording Tips

**Before Recording:**
1. Close unnecessary programs
2. Clean up your desktop (optional but looks professional)
3. Practice once without recording
4. Have the commands ready in a text file to copy-paste

**During Recording:**
1. Speak clearly and not too fast
2. Explain what you're doing as you do it
3. If you make a mistake, just pause and continue (you can edit later)
4. Show your face (optional) or just screen record

**After Recording:**
1. Watch it once to make sure everything is visible
2. Check that audio is clear
3. Trim any long pauses (optional)

### Where to Upload

**Option 1: YouTube (Recommended)**
1. Go to https://youtube.com
2. Click "Create" → "Upload video"
3. Select your video file
4. Set visibility to "Unlisted" (not public, but anyone with link can view)
5. Add title: "TinyTelemetry v1.0 - Phase 1 Demo"
6. Click "Publish"
7. Copy the link (looks like: https://youtu.be/ABC123)

**Option 2: Google Drive**
1. Go to https://drive.google.com
2. Click "New" → "File upload"
3. Select your video file
4. Right-click the file → "Share"
5. Change to "Anyone with the link can view"
6. Copy the link

**Option 3: OneDrive (Windows)**
1. Save video to OneDrive folder
2. Right-click → "Share"
3. Set to "Anyone with the link can view"
4. Copy the link

### Adding the Link to Your Project

**Step 1:** Open `README.md` in a text editor

**Step 2:** Find this line:
```markdown
**Video Link:** [INSERT YOUR VIDEO LINK HERE]
```

**Step 3:** Replace it with your actual link:
```markdown
**Video Link:** [https://youtu.be/YOUR_VIDEO_ID](https://youtu.be/YOUR_VIDEO_ID)
```

**Step 4:** Do the same in `README.txt`

**Step 5:** Test the link in an incognito/private browser window to make sure it works!

---

## 📤 Submitting Phase 1

You're almost done! Let's package everything for submission.

### What to Submit

You need to submit these files/folders:

```
✅ docs/project-proposal.md (or PDF)
✅ docs/mini-rfc.md (or PDF)
✅ README.md (with your video link)
✅ README.txt (with your video link)
✅ src/ folder (all the code)
✅ scripts/ folder (all the test scripts)
✅ output/ folder (with at least one CSV file)
✅ requirements.txt
```

### Creating a ZIP File

**Windows:**
1. Select all the files and folders listed above
2. Right-click → "Send to" → "Compressed (zipped) folder"
3. Name it: `TinyTelemetry-Phase1-YourName.zip`

**Mac:**
1. Select all the files and folders
2. Right-click → "Compress Items"
3. Rename to: `TinyTelemetry-Phase1-YourName.zip`

**Linux:**
```bash
zip -r TinyTelemetry-Phase1-YourName.zip docs/ src/ scripts/ output/ README.md README.txt requirements.txt
```

### Final Checklist Before Submitting

- [ ] Video is uploaded and link is working
- [ ] Video link is in README.md
- [ ] Video link is in README.txt
- [ ] Ran the baseline test one more time (it passed)
- [ ] At least one CSV file is in output/ folder
- [ ] All files are in the ZIP
- [ ] ZIP file is named correctly

### Uploading to LMS

1. Log into your Learning Management System (LMS)
2. Find the Phase 1 assignment
3. Click "Upload" or "Submit"
4. Select your ZIP file
5. Add any comments if required
6. Click "Submit"
7. **IMPORTANT:** Verify the submission went through!

---

## 🆘 Troubleshooting

### Problem: "Python is not recognized"

**Solution:**
1. Python is not installed or not in PATH
2. Download from https://www.python.org/downloads/
3. During installation, CHECK the box "Add Python to PATH"
4. Restart your computer
5. Try again

### Problem: "No module named 'matplotlib'"

**Solution:**
```bash
pip install matplotlib
```

Or install everything:
```bash
pip install -r requirements.txt
```

### Problem: "Address already in use" (Port 5000)

**Solution:**
Another program is using port 5000.

**Option 1:** Use a different port
```bash
python -m src.server --port 5001
python -m src.client --server-port 5001
```

**Option 2:** Find and close the program using port 5000
- Windows: Open Task Manager, look for Python processes
- Mac/Linux: `lsof -i :5000` then `kill <PID>`

### Problem: Test fails with "delivery rate < 99%"

**Possible Causes:**
1. Network issues (firewall blocking)
2. Computer too slow (increase duration)
3. Antivirus blocking

**Solutions:**
- Try running as administrator
- Temporarily disable firewall (be careful!)
- Use a longer duration: `--duration 60`

### Problem: CSV file is empty

**Possible Causes:**
1. Server didn't receive any messages
2. Client didn't send any messages
3. Wrong port number

**Solutions:**
- Make sure both server and client use the same port
- Check firewall settings
- Try running the automatic test instead

### Problem: Can't find output files

**Solution:**
The `output/` folder might not exist.

Create it manually:
```bash
mkdir output
```

Or the files might be in a different location. Check where the server said it's logging:
```
Logging to: output\telemetry.csv
```

### Problem: Video is too large to upload

**Solutions:**
1. Compress the video using HandBrake (free software)
2. Record at lower resolution (720p instead of 1080p)
3. Use YouTube (no size limit)
4. Split into two parts if necessary

### Problem: "Permission denied" error

**Solution:**
You don't have permission to write to that folder.

**Windows:** Run Command Prompt as Administrator
**Mac/Linux:** Use `sudo` (but be careful!)

Or save to a different folder where you have permission:
```bash
python -m src.server --log-file C:\Users\YourName\Desktop\test.csv
```

---

## 🎉 Congratulations!

You've completed Phase 1! Here's what you accomplished:

✅ Installed Python and all required packages
✅ Understood what TinyTelemetry does
✅ Ran your first test successfully
✅ Looked at the results (CSV and JSON)
✅ Recorded a demo video
✅ Submitted everything to your instructor

### What You Learned

1. **Networking Basics**: How clients and servers communicate
2. **UDP Protocol**: Fire-and-forget messaging
3. **Binary Encoding**: Efficient data representation
4. **Testing**: How to validate a protocol
5. **Documentation**: How to write technical documents

### Next Steps (Phase 2)

In Phase 2, you'll probably:
- Test under bad network conditions (packet loss, delay)
- Measure performance metrics
- Create graphs and visualizations
- Write a final report

But for now, take a break and celebrate! 🎊

---

## 📞 Quick Reference Commands

**Install packages:**
```bash
pip install -r requirements.txt
```

**Run automatic test:**
```bash
python scripts/test_baseline.py --duration 30
```

**Start server manually:**
```bash
python -m src.server
```

**Start client manually:**
```bash
python -m src.client --device-id 1001 --duration 30
```

**Check Python version:**
```bash
python --version
```

**Navigate to project:**
```bash
cd "C:\Users\YourName\Desktop\Network Project"
```

---

## 📚 Additional Resources

**If you want to learn more:**

1. **Python Basics**: https://www.python.org/about/gettingstarted/
2. **UDP Protocol**: https://en.wikipedia.org/wiki/User_Datagram_Protocol
3. **Binary Encoding**: https://en.wikipedia.org/wiki/Binary_code
4. **IoT Protocols**: https://www.postscapes.com/internet-of-things-protocols/

**Project Documentation:**
- `README.md` - Main instructions
- `docs/mini-rfc.md` - Complete technical specification
- `docs/project-proposal.md` - Project overview
- `SUBMISSION_READY.md` - Submission checklist

---

**Good luck with your project! You've got this! 🚀**

*If you have questions, refer back to this guide or ask your instructor.*
