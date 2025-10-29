# TinyTelemetry v1.0

A lightweight, UDP-based telemetry protocol designed for constrained IoT sensors. TinyTelemetry enables periodic transmission of small sensor readings (temperature, humidity, voltage) from distributed sensor clients to a central collector server.

## 🎓 New to TinyTelemetry?

**Start here:** Check out the **[Guides/](Guides/)** folder for beginner-friendly tutorials!

- **[Guides/QUICK_START.md](Guides/QUICK_START.md)** - Get running in 5 minutes
- **[Guides/HOW_TO_USE_FOR_DUMMIES.md](Guides/HOW_TO_USE_FOR_DUMMIES.md)** - Complete beginner's guide
- **[Guides/FILE_GUIDE.md](Guides/FILE_GUIDE.md)** - What every file does

## Demo Video

A 5-minute demonstration of TinyTelemetry v1.0 is available here:

**Video Link:** [INSERT YOUR VIDEO LINK HERE]

*(Please replace the placeholder above with your actual video link. Ensure the video is set to "Anyone with the link can view")*

The demo covers:
- Protocol overview and message format
- Live client-server communication with multiple concurrent clients
- CSV logging with duplicate and gap detection
- Automated baseline testing with metrics

## Project Overview

TinyTelemetry v1.0 is an experimental protocol that prioritizes simplicity, bandwidth efficiency, and loss tolerance over guaranteed delivery. The system is designed for telemetry use cases where occasional data loss is acceptable, eliminating the need for complex retransmission mechanisms.

### Key Features

- **Minimal overhead**: Compact 12-byte binary header
- **Loss-tolerant**: Operates under 5% packet loss without retransmissions
- **Bandwidth efficient**: Optional batching reduces header overhead by up to 65%
- **Network resilient**: Handles delay (100ms), jitter (±10ms), and packet reordering
- **Cross-platform**: Pure Python implementation for Linux and Windows
- **Stateful collection**: Server detects duplicates, gaps, and reorders by timestamp

### Components

- **Sensor Client** (`src/client.py`): Simulates IoT sensors, generates readings, and transmits data packets
- **Collector Server** (`src/server.py`): Receives packets, maintains per-device state, and logs to CSV
- **Protocol Library** (`src/protocol.py`): Binary encoding/decoding and data structures
- **Metrics Calculator** (`src/metrics.py`): Performance analysis and statistical reporting

## Build Instructions

### Prerequisites

- **Python 3.7+** (for dataclasses support)
- **pip** (Python package manager)

### Installation

1. Clone or download the repository:
```bash
git clone <repository-url>
cd tinytelemetry
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python --version  # Should be 3.7 or higher
python -c "import matplotlib, socket, struct"  # Should not error
```

### Dependencies

The project uses primarily standard library modules with minimal external dependencies:

- `matplotlib` - For generating plots and visualizations
- `psutil` (optional) - For enhanced CPU profiling

All dependencies are cross-platform compatible.

## Usage Examples

### Starting the Collector Server

Basic usage with default settings (port 5000, logs to `output/telemetry.csv`):

```bash
python -m src.server
```

Custom configuration:

```bash
python -m src.server --port 5000 --log-file output/telemetry.csv --reorder-window 10 --reorder-timeout 2.0
```

**Options:**
- `--port`: UDP port to listen on (default: 5000)
- `--log-file`: Path to CSV log file (default: output/telemetry.csv)
- `--reorder-window`: Buffer size for packet reordering (default: 10)
- `--reorder-timeout`: Max time to buffer packets in seconds (default: 2.0)

### Starting a Sensor Client

Basic usage (1-second interval, 60-second duration, non-batched):

```bash
python -m src.client --device-id 1001 --server-host localhost --server-port 5000 --interval 1 --duration 60
```

With batching enabled (10 readings per packet):

```bash
python -m src.client --device-id 1001 --server-host localhost --server-port 5000 --interval 1 --duration 60 --batch-size 10
```

Custom sensor types (temperature and humidity only):

```bash
python -m src.client --device-id 1001 --server-host localhost --interval 5 --duration 120 --sensor-types temperature,humidity
```

**Options:**
- `--device-id`: Unique device identifier, 1-65535 (required)
- `--server-host`: Collector hostname or IP (default: localhost)
- `--server-port`: Collector UDP port (default: 5000)
- `--interval`: Reporting interval in seconds: 1, 5, or 30 (default: 1)
- `--duration`: Test duration in seconds (default: 60)
- `--batch-size`: Readings per packet, 1-37 (default: 1)
- `--sensor-types`: Comma-separated list: temperature, humidity, voltage (default: all)

### Running Multiple Clients

Simulate multiple sensors by running clients with different device IDs:

```bash
# Terminal 1: Start server
python -m src.server

# Terminal 2: Start client 1
python -m src.client --device-id 1001 --interval 1 --duration 60

# Terminal 3: Start client 2
python -m src.client --device-id 1002 --interval 5 --duration 60

# Terminal 4: Start client 3
python -m src.client --device-id 1003 --interval 1 --duration 60 --batch-size 10
```

## Running Tests

The project includes automated test scripts for validating protocol performance under various network conditions.

### Baseline Test (No Impairment)

Tests the protocol under ideal network conditions:

```bash
python scripts/test_baseline.py
```

This runs a 60-second test with 1-second reporting interval and verifies:
- ≥99% packet delivery
- Sequence numbers are in order
- No unexpected duplicates

### Packet Loss Test (Linux Only)

Tests the protocol under 5% random packet loss using Linux `tc` and `netem`:

```bash
sudo bash scripts/test_loss.sh
```

**Requirements:**
- Linux operating system
- Root/sudo privileges
- `tc` (traffic control) utility

This test verifies:
- Gap detection works correctly
- Duplicate rate ≤1%
- Server continues processing after packet loss

### Delay and Jitter Test (Linux Only)

Tests the protocol under 100ms ±10ms delay/jitter using `netem`:

```bash
sudo bash scripts/test_delay.sh
```

**Requirements:**
- Linux operating system
- Root/sudo privileges
- `tc` (traffic control) utility

This test verifies:
- Timestamp-based reordering works
- No buffer overruns
- No crashes under delayed packets

### Running All Tests with Statistics

Execute all test scenarios 5 times each and generate statistical summary:

```bash
python scripts/run_all_tests.py
```

This produces:
- Individual metrics for each run
- Statistical summary (min, median, max)
- Aggregated results in `output/test_results.json`

### Generating Plots

Create visualizations from test results:

```bash
python scripts/generate_plots.py
```

Generates:
- `output/bytes_per_report_vs_interval.png`: Bandwidth efficiency analysis
- `output/duplicate_rate_vs_loss.png`: Duplicate detection performance

## Batching Decision Explanation

### Why Batching?

Batching multiple sensor readings into a single packet significantly reduces bandwidth overhead:

| Batch Size | Packet Size | Overhead per Reading | Efficiency Gain |
|------------|-------------|---------------------|-----------------|
| 1 reading | 18 bytes | 72% | Baseline |
| 5 readings | 38 bytes | 40% | 44% improvement |
| 10 readings | 63 bytes | 21% | 71% improvement |
| 37 readings | 198 bytes | 7% | 90% improvement |

### Trade-offs

**Advantages:**
- Reduced header overhead (12 bytes amortized across multiple readings)
- Lower packet rate (fewer packets for same data volume)
- Reduced collision probability in high-density deployments
- Better bandwidth utilization

**Disadvantages:**
- Increased latency (must wait to accumulate readings)
- Larger packets more susceptible to corruption
- All readings in batch lost if packet is dropped

### Recommended Settings

- **Low-latency applications**: batch_size=1 (non-batched)
- **Bandwidth-constrained networks**: batch_size=10-20
- **High-density deployments**: batch_size=10-15 (balance efficiency and loss impact)
- **Maximum efficiency**: batch_size=37 (use only if latency is not critical)

### Implementation

The client maintains a reading buffer. When the buffer reaches the configured batch size, all buffered readings are encoded into a single DATA packet. The batch size is configurable via the `--batch-size` command-line argument.

## Field Packing Strategy

### Binary Encoding

TinyTelemetry uses compact binary encoding to minimize bandwidth usage. All fields are packed using Python's `struct` module with network byte order (big-endian).

**Header Encoding (12 bytes):**
```python
import struct
header = struct.pack('!BBHII', version, msg_type, device_id, seq_num, timestamp)
```

**Reading Encoding (5 bytes each):**
```python
reading = struct.pack('!Bf', sensor_type, value)
```

**Format Codes:**
- `!` = Network byte order (big-endian)
- `B` = Unsigned char (1 byte)
- `H` = Unsigned short (2 bytes)
- `I` = Unsigned int (4 bytes)
- `f` = Float (4 bytes, IEEE 754)

### Why Binary?

**Advantages over text-based formats (JSON, XML):**
- **Compact**: No text overhead, delimiters, or whitespace
- **Fast**: Binary operations are faster than text parsing
- **Deterministic**: Fixed-size fields enable precise bandwidth calculations
- **Cross-platform**: Network byte order ensures compatibility across architectures

**Size Comparison:**

| Format | Size (1 reading) | Size (10 readings) |
|--------|------------------|---------------------|
| TinyTelemetry (binary) | 18 bytes | 63 bytes |
| JSON (compact) | ~80 bytes | ~650 bytes |
| JSON (pretty) | ~120 bytes | ~1000 bytes |

Binary encoding provides **4-16x** size reduction compared to JSON.

## Cross-Platform Notes

### Linux

Full functionality including network impairment testing:

- All features supported
- Network impairment tests use `tc qdisc` with `netem`
- Packet capture with `tcpdump`
- Requires root/sudo for network impairment tests

### Windows

Core functionality with manual network impairment:

- Client and server fully supported
- Baseline tests work without modification
- Network impairment tests require manual setup:
  - Use [Clumsy](https://jagt.github.io/clumsy/) for packet loss/delay simulation
  - Use Wireshark/tshark for packet capture
- Automated impairment tests (test_loss.sh, test_delay.sh) are Linux-only

### Path Handling

The project uses `pathlib.Path` for cross-platform file path handling. All file operations work identically on Linux and Windows.

### Socket Programming

The implementation uses Python's standard `socket` module, which provides cross-platform UDP socket support. No platform-specific code is required for networking.

## Output Files

All generated files are stored in the `output/` directory:

### CSV Logs

**File:** `output/telemetry.csv`

Contains one row per received packet with the following columns:

- `device_id`: Sensor device identifier
- `seq`: Sequence number
- `timestamp`: Packet timestamp (Unix epoch seconds)
- `arrival_time`: Server arrival time (Unix epoch with microseconds)
- `msg_type`: DATA or HEARTBEAT
- `duplicate_flag`: True if duplicate packet detected
- `gap_flag`: True if sequence gap detected
- `gap_size`: Number of missing packets (0 if no gap)
- `reading_count`: Number of sensor readings in packet

**Example:**
```csv
device_id,seq,timestamp,arrival_time,msg_type,duplicate_flag,gap_flag,gap_size,reading_count
1001,0,1698765432,1698765432.123456,DATA,False,False,0,3
1001,1,1698765433,1698765433.125678,DATA,False,False,0,3
1001,3,1698765435,1698765435.128901,DATA,False,True,1,3
```

### Metrics JSON

**File:** `output/test_results.json`

Contains performance metrics and statistical analysis:

```json
{
  "test_scenario": "baseline",
  "duration_seconds": 60,
  "reporting_interval": 1,
  "batch_size": 1,
  "metrics": {
    "bytes_per_report": 18.0,
    "packets_received": 59,
    "packets_sent": 60,
    "duplicate_rate": 0.0,
    "sequence_gap_count": 1,
    "cpu_ms_per_report": 0.15
  },
  "statistics": {
    "min": {...},
    "median": {...},
    "max": {...}
  }
}
```

### Packet Captures (PCAP)

**Files:** `output/*.pcap`

Binary packet captures for offline analysis with Wireshark or tcpdump. Generated by test scripts for each scenario and run.

**Example files:**
- `baseline_run1.pcap`
- `baseline_run2.pcap`
- `loss_5pct_run1.pcap`
- `delay_100ms_run1.pcap`

**Analyzing with Wireshark:**
```bash
wireshark output/baseline_run1.pcap
```

**Analyzing with tcpdump:**
```bash
tcpdump -r output/baseline_run1.pcap -n
```

### Plots (PNG)

**Files:** `output/*.png`

Visualizations generated by `scripts/generate_plots.py`:

- `bytes_per_report_vs_interval.png`: Shows bandwidth efficiency across different reporting intervals
- `duplicate_rate_vs_loss.png`: Shows duplicate detection performance under various loss rates

## Protocol Specification

For detailed protocol specification including message formats, field layouts, and encoding details, see:

**[docs/mini-rfc.md](docs/mini-rfc-Full.md)**

## Project Structure

```
.
├── src/                    # Source code
│   ├── protocol.py        # Protocol encoding/decoding
│   ├── client.py          # Sensor client implementation
│   ├── server.py          # Collector server implementation
│   └── metrics.py         # Metrics calculation
│
├── scripts/                # Test automation
│   ├── test_baseline.py   # Baseline test
│   ├── test_loss.sh       # Packet loss test (Linux)
│   ├── test_delay.sh      # Delay/jitter test (Linux)
│   ├── run_all_tests.py   # Master test runner
│   └── generate_plots.py  # Visualization generator
│
├── docs/                   # Documentation
│   └── mini-rfc.md        # Protocol specification
│
├── output/                 # Generated artifacts
│   ├── *.csv              # Telemetry logs
│   ├── *.json             # Metrics
│   ├── *.pcap             # Packet captures
│   └── *.png              # Plots
│
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## License

This is an experimental protocol implementation for educational and research purposes.

## Contributing

This project is part of a research effort to evaluate lightweight telemetry protocols for IoT deployments. Contributions, feedback, and experimental results are welcome.
