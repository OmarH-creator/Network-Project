# 📊 TinyTelemetry - Simple Visual Diagrams

These diagrams help you understand how TinyTelemetry works!

---

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR COMPUTER                            │
│                                                             │
│  ┌──────────────┐                    ┌──────────────┐      │
│  │   SENSOR     │                    │  COLLECTOR   │      │
│  │   (Client)   │                    │   (Server)   │      │
│  │              │                    │              │      │
│  │  Generates   │   UDP Messages     │  Receives    │      │
│  │  readings    │ ─────────────────> │  & logs      │      │
│  │              │   (Fire & Forget)  │  data        │      │
│  │              │                    │              │      │
│  └──────────────┘                    └──────────────┘      │
│       ↓                                      ↓              │
│  src/client.py                          src/server.py      │
│                                                             │
│                                         ┌──────────────┐   │
│                                         │ output/      │   │
│                                         │ telemetry.csv│   │
│                                         └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**What This Shows:**
- Both client and server run on your computer (localhost)
- Client sends messages to server
- Server saves everything to a CSV file
- They communicate using UDP (like throwing paper airplanes)

---

## 📦 Message Structure

### Simple View

```
┌─────────────────────────────────────────────────────┐
│                    ONE MESSAGE                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐  ┌──────────────────────────────┐   │
│  │  HEADER  │  │         PAYLOAD              │   │
│  │ 12 bytes │  │  (sensor readings)           │   │
│  │          │  │  1 to 37 readings            │   │
│  └──────────┘  └──────────────────────────────┘   │
│                                                     │
│  Who sent it?   What data?                         │
│  When?          Temperature? Humidity?             │
│  Message #?                                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Detailed Header (12 bytes)

```
Byte:    0        1        2-3      4-7          8-11
      ┌────────┬────────┬────────┬──────────┬──────────┐
      │Version │MsgType │DeviceID│ SeqNum   │Timestamp │
      │  0x01  │ 0x01   │  1001  │    0     │1698765432│
      └────────┴────────┴────────┴──────────┴──────────┘
         1 byte  1 byte  2 bytes   4 bytes    4 bytes

What each field means:
- Version: Which version of protocol (always 1)
- MsgType: DATA (0x01) or HEARTBEAT (0x02)
- DeviceID: Which sensor (like a name tag)
- SeqNum: Message number (0, 1, 2, 3...)
- Timestamp: When it was sent (Unix time)
```

### Complete DATA Message Example

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA MESSAGE (28 bytes)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HEADER (12 bytes)                                          │
│  ┌──┬──┬────┬────────┬──────────┐                          │
│  │01│01│03E9│00000000│654A2B18  │                          │
│  └──┴──┴────┴────────┴──────────┘                          │
│   V  M  Dev   Seq       Time                                │
│                                                             │
│  COUNT (1 byte)                                             │
│  ┌──┐                                                       │
│  │03│  ← 3 readings in this message                        │
│  └──┘                                                       │
│                                                             │
│  READING 1 (5 bytes)                                        │
│  ┌──┬────────┐                                              │
│  │01│41C80000│  ← Temperature: 25.0°C                      │
│  └──┴────────┘                                              │
│   T   Value                                                 │
│                                                             │
│  READING 2 (5 bytes)                                        │
│  ┌──┬────────┐                                              │
│  │02│42480000│  ← Humidity: 50.0%                          │
│  └──┴────────┘                                              │
│                                                             │
│  READING 3 (5 bytes)                                        │
│  ┌──┬────────┐                                              │
│  │03│40A00000│  ← Voltage: 5.0V                            │
│  └──┴────────┘                                              │
│                                                             │
│  Total: 12 + 1 + 5 + 5 + 5 = 28 bytes                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Communication Flow

### Normal Operation (Everything Works)

```
Time    Client                          Server
────────────────────────────────────────────────────────────
T+0s    Start up                        Start up
        device_id = 1001                Listening on port 5000
        seq = 0                         
        
T+1s    Generate readings:              
        - temp = 25.0°C                 
        - humid = 50.0%                 
        - volt = 5.0V                   
        
        Encode into packet              
        seq = 0                         
        
        Send UDP packet ──────────────> Receive packet
                                        Parse header
                                        device_id = 1001
                                        seq = 0
                                        
                                        New device! Initialize state
                                        last_seq = 0
                                        
                                        Log to CSV:
                                        1001,0,...,DATA,False,False,0,3
        
T+2s    Generate readings               
        seq = 1                         
        
        Send UDP packet ──────────────> Receive packet
                                        seq = 1
                                        last_seq was 0
                                        No gap! ✓
                                        
                                        Update: last_seq = 1
                                        Log to CSV:
                                        1001,1,...,DATA,False,False,0,3
        
T+3s    Generate readings               
        seq = 2                         
        
        Send UDP packet ──────────────> Receive packet
                                        seq = 2
                                        No gap! ✓
                                        
                                        Log to CSV:
                                        1001,2,...,DATA,False,False,0,3
```

### When a Message Gets Lost

```
Time    Client                          Server
────────────────────────────────────────────────────────────
T+1s    seq = 0                         
        Send ──────────────────────────> Receive seq=0 ✓
                                        last_seq = 0
        
T+2s    seq = 1                         
        Send ──────────────────────────> Receive seq=1 ✓
                                        last_seq = 1
        
T+3s    seq = 2                         
        Send ─────────X                 (packet lost!)
                     Lost!              
                                        (nothing received)
        
T+4s    seq = 3                         
        Send ──────────────────────────> Receive seq=3
                                        Wait! last_seq was 1
                                        Now we got 3
                                        Gap detected! ⚠️
                                        
                                        gap_size = 3 - 1 - 1 = 1
                                        
                                        Log to CSV:
                                        1001,3,...,DATA,False,True,1,3
                                                        ↑    ↑
                                                      gap  size
                                        
                                        Update: last_seq = 3
```

---

## 📊 Batching Comparison

### Non-Batched (batch_size = 1)

```
Every 1 second, send 1 reading:

T+0s: ┌────────────┬─────┐
      │ Header(12) │ R1  │ = 18 bytes
      └────────────┴─────┘
      
T+1s: ┌────────────┬─────┐
      │ Header(12) │ R2  │ = 18 bytes
      └────────────┴─────┘
      
T+2s: ┌────────────┬─────┐
      │ Header(12) │ R3  │ = 18 bytes
      └────────────┴─────┘

Total: 54 bytes for 3 readings
Overhead: 36 bytes of headers (67%)
```

### Batched (batch_size = 3)

```
Every 3 seconds, send 3 readings:

T+3s: ┌────────────┬─────┬─────┬─────┐
      │ Header(12) │ R1  │ R2  │ R3  │ = 28 bytes
      └────────────┴─────┴─────┴─────┘

Total: 28 bytes for 3 readings
Overhead: 13 bytes (46%)
Savings: 26 bytes (48% less!)
```

**Why Batching is Better:**
- Fewer packets sent (less network traffic)
- Less overhead (more efficient)
- But: Higher latency (must wait to accumulate readings)

---

## 🗂️ Project File Structure

```
Network Project/
│
├── 📁 src/                          ← Main code (the brain)
│   ├── 📄 __init__.py              ← Makes this a Python package
│   ├── 📄 protocol.py              ← Encoding/decoding rules
│   ├── 📄 client.py                ← Sensor simulator
│   ├── 📄 server.py                ← Collector server
│   └── 📄 metrics.py               ← Statistics calculator
│
├── 📁 scripts/                      ← Test automation (helpers)
│   ├── 📄 test_baseline.py         ← Automatic test runner
│   ├── 📄 test_loss.sh             ← Packet loss test (Linux)
│   ├── 📄 test_delay.sh            ← Delay test (Linux)
│   ├── 📄 run_all_tests.py         ← Run all tests
│   └── 📄 generate_plots.py        ← Make graphs
│
├── 📁 docs/                         ← Documentation (manuals)
│   ├── 📄 project-proposal.md      ← What & why
│   ├── 📄 mini-rfc.md              ← Complete specification
│   ├── 📄 demo-video-script.md     ← Video guide
│   └── 📄 simple-diagrams.md       ← This file!
│
├── 📁 output/                       ← Results (homework folder)
│   ├── 📄 *.csv                    ← Data logs
│   ├── 📄 *.json                   ← Metrics
│   └── 📄 *.png                    ← Graphs
│
├── 📄 README.md                     ← Main instructions
├── 📄 README.txt                    ← Simple instructions
├── 📄 requirements.txt              ← What to install
├── 📄 HOW_TO_USE_FOR_DUMMIES.md    ← Beginner's guide
├── 📄 PHASE1_CHECKLIST.md          ← Submission checklist
└── 📄 SUBMISSION_READY.md          ← Final checklist
```

---

## 🎯 How Data Flows Through the System

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA FLOW                       │
└─────────────────────────────────────────────────────────────┘

1. SENSOR GENERATES DATA
   ┌──────────────┐
   │ Temperature  │
   │ Humidity     │ ← Random values generated
   │ Voltage      │
   └──────────────┘
          ↓
          
2. CLIENT ENCODES DATA
   ┌──────────────┐
   │ Binary       │
   │ Encoding     │ ← Convert to bytes
   │ (struct)     │
   └──────────────┘
          ↓
          
3. UDP TRANSMISSION
   ┌──────────────┐
   │   Network    │
   │   (UDP)      │ ← Send over network
   │              │
   └──────────────┘
          ↓
          
4. SERVER RECEIVES
   ┌──────────────┐
   │ Parse Header │
   │ Check Device │ ← Decode and validate
   │ Check Seq    │
   └──────────────┘
          ↓
          
5. DUPLICATE CHECK
   ┌──────────────┐
   │ Is seq ≤     │
   │ last_seq?    │ ← Compare sequence numbers
   │              │
   └──────────────┘
      ↓         ↓
     Yes       No
      ↓         ↓
   Duplicate  Continue
      ↓         ↓
          
6. GAP CHECK
   ┌──────────────┐
   │ Is seq >     │
   │ last_seq+1?  │ ← Check for missing messages
   │              │
   └──────────────┘
      ↓         ↓
     Yes       No
      ↓         ↓
    Gap!     No gap
      ↓         ↓
          
7. REORDER BUFFER
   ┌──────────────┐
   │ Add to       │
   │ buffer       │ ← Sort by timestamp
   │ Sort by time │
   └──────────────┘
          ↓
          
8. LOG TO CSV
   ┌──────────────┐
   │ Write row    │
   │ to CSV file  │ ← Save to disk
   │              │
   └──────────────┘
          ↓
          
9. METRICS CALCULATION
   ┌──────────────┐
   │ Calculate    │
   │ statistics   │ ← Analyze performance
   │ Save JSON    │
   └──────────────┘
```

---

## 🔢 Size Comparison: Binary vs JSON

### TinyTelemetry (Binary)

```
┌─────────────────────────────────────┐
│  Binary Message (28 bytes)          │
├─────────────────────────────────────┤
│  01 01 03 E9 00 00 00 00 65 4A 2B  │
│  18 03 01 41 C8 00 00 02 42 48 00  │
│  00 03 40 A0 00 00                  │
└─────────────────────────────────────┘
         28 bytes total
```

### JSON (Text-Based)

```
┌─────────────────────────────────────┐
│  JSON Message (~150 bytes)          │
├─────────────────────────────────────┤
│  {                                  │
│    "version": 1,                    │
│    "msg_type": "DATA",              │
│    "device_id": 1001,               │
│    "seq_num": 0,                    │
│    "timestamp": 1698765432,         │
│    "readings": [                    │
│      {"type": "temp", "value": 25.0}│
│      {"type": "humid", "value": 50.0│
│      {"type": "volt", "value": 5.0} │
│    ]                                │
│  }                                  │
└─────────────────────────────────────┘
        ~150 bytes total

Binary is 5.4x smaller! 🎉
```

---

## 📈 Test Results Visualization

### Perfect Test (No Errors)

```
Packets Sent vs Received:

Sent:     ████████████████████████████████ 30 packets
Received: ████████████████████████████████ 30 packets

Delivery Rate: 100% ✓
Duplicates: 0 ✓
Gaps: 0 ✓
```

### Test with Packet Loss

```
Packets Sent vs Received:

Sent:     ████████████████████████████████ 30 packets
Received: ███████████████████████████░░░░░ 27 packets
                                    ↑
                                  3 lost

Delivery Rate: 90%
Duplicates: 0 ✓
Gaps: 3 (detected) ✓
```

---

## 🎓 Learning Path

```
┌─────────────────────────────────────────────────────────┐
│              YOUR LEARNING JOURNEY                      │
└─────────────────────────────────────────────────────────┘

Week 1: Understanding
├─ What is a protocol?
├─ What is UDP?
├─ Why binary encoding?
└─ Read documentation

Week 2: Installation
├─ Install Python
├─ Install packages
├─ Test installation
└─ Run first test

Week 3: Experimentation
├─ Run manual tests
├─ Try different settings
├─ Look at CSV files
└─ Understand metrics

Week 4: Documentation
├─ Read Mini-RFC
├─ Read proposal
├─ Understand design choices
└─ Prepare for demo

Week 5: Demo & Submission
├─ Record demo video
├─ Upload video
├─ Package files
└─ Submit! 🎉
```

---

## 🎯 Key Concepts Summary

```
┌────────────────────────────────────────────────────────┐
│  CONCEPT          │  SIMPLE EXPLANATION                │
├────────────────────────────────────────────────────────┤
│  Protocol         │  Rules for communication           │
│  UDP              │  Fast but unreliable messaging     │
│  Binary Encoding  │  Data as numbers, not text         │
│  Sequence Number  │  Message counter (0, 1, 2, 3...)   │
│  Duplicate        │  Same message received twice       │
│  Gap              │  Missing message detected          │
│  Batching         │  Sending multiple readings at once │
│  Fire-and-Forget  │  Send and don't wait for reply     │
│  Stateless Client │  Client doesn't remember much      │
│  Stateful Server  │  Server remembers everything       │
└────────────────────────────────────────────────────────┘
```

---

**These diagrams should help you understand TinyTelemetry better!**

*Refer back to these whenever you need a visual reminder of how things work.*
