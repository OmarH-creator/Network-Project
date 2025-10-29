# TinyTelemetry v1.0 - Test Scripts

This directory contains automated test scripts for validating the TinyTelemetry protocol under various network conditions.

## Overview

The test suite includes:
- **Baseline tests**: Validate protocol under ideal conditions
- **Packet loss tests**: Validate loss tolerance (5% loss, Linux only)
- **Delay/jitter tests**: Validate reordering (100ms ±10ms, Linux only)
- **Master test runner**: Run all scenarios with statistical analysis
- **Windows-compatible tests**: Baseline testing on Windows

## Quick Start

### Windows

```bash
# Run baseline test (5 seconds)
python scripts/test_baseline_windows.py --duration 5

# Run baseline test with packet capture (requires Wireshark/tshark)
python scripts/test_baseline_windows.py --duration 60 --enable-pcap

# For network impairment testing on Windows, see Clumsy instructions below
```

### Linux

```bash
# Run baseline test
python scripts/test_baseline.py --duration 60

# Run packet loss test (requires sudo)
sudo bash scripts/test_loss.sh

# Run delay/jitter test (requires sudo)
sudo bash scripts/test_delay.sh

# Run all tests with statistical analysis (requires sudo)
python scripts/run_all_tests.py --runs 5 --duration 60
```

## Test Scripts

### 1. test_baseline.py

Runs a baseline test with no network impairment to validate the protocol under ideal conditions.

**Usage:**
```bash
python scripts/test_baseline.py [OPTIONS]
```

**Options:**
- `--device-id`: Device identifier (default: 1001)
- `--interval`: Reporting interval in seconds (1, 5, or 30, default: 1)
- `--duration`: Test duration in seconds (default: 60)
- `--batch-size`: Number of readings per packet (default: 1)
- `--server-port`: Server UDP port (default: 5000)
- `--log-file`: Path to CSV log file (default: output/baseline_telemetry.csv)
- `--output-json`: Path to metrics JSON file (default: output/baseline_metrics.json)
- `--enable-pcap`: Enable packet capture (requires tcpdump/tshark)
- `--pcap-file`: Path to pcap file (default: output/baseline_capture.pcap)

**Example:**
```bash
# Run 30-second test with batching
python scripts/test_baseline.py --duration 30 --batch-size 10

# Run with packet capture
python scripts/test_baseline.py --duration 60 --enable-pcap
```

**Expected Results:**
- ≥99% packet delivery
- Sequence numbers in order
- No gaps or duplicates

### 2. test_loss.sh (Linux only)

Runs a test with 5% packet loss using Linux netem to validate loss tolerance and gap detection.

**Requirements:**
- Linux operating system
- Root/sudo privileges
- Python 3.7+

**Usage:**
```bash
sudo bash scripts/test_loss.sh [DEVICE_ID] [INTERVAL] [DURATION] [BATCH_SIZE] [SERVER_PORT]
```

**Parameters:**
- `DEVICE_ID`: Device identifier (default: 1001)
- `INTERVAL`: Reporting interval in seconds (default: 1)
- `DURATION`: Test duration in seconds (default: 60)
- `BATCH_SIZE`: Readings per packet (default: 1)
- `SERVER_PORT`: Server UDP port (default: 5000)

**Example:**
```bash
# Run with defaults
sudo bash scripts/test_loss.sh

# Run 30-second test
sudo bash scripts/test_loss.sh 1001 1 30 1 5000
```

**Expected Results:**
- Gap detection works (gaps detected)
- Duplicate rate ≤1%
- Packet capture saved to output/loss_capture.pcap

### 3. test_delay.sh (Linux only)

Runs a test with 100ms ±10ms delay/jitter using Linux netem to validate reordering capabilities.

**Requirements:**
- Linux operating system
- Root/sudo privileges
- Python 3.7+

**Usage:**
```bash
sudo bash scripts/test_delay.sh [DEVICE_ID] [INTERVAL] [DURATION] [BATCH_SIZE] [SERVER_PORT]
```

**Parameters:** Same as test_loss.sh

**Example:**
```bash
# Run with defaults
sudo bash scripts/test_delay.sh

# Run 30-second test
sudo bash scripts/test_delay.sh 1001 1 30 1 5000
```

**Expected Results:**
- Reordering works (out-of-order packets handled)
- No crashes or buffer overrun
- Packet capture saved to output/delay_capture.pcap

### 4. run_all_tests.py

Master test runner that executes all test scenarios multiple times, collects metrics, and calculates statistical summaries.

**Usage:**
```bash
# Linux (all tests)
python scripts/run_all_tests.py --runs 5 --duration 60

# Windows (baseline only)
python scripts/run_all_tests.py --runs 5 --duration 60 --baseline-only

# Generate data for plotting (multiple intervals and loss rates)
python scripts/run_all_tests.py --runs 5 --duration 60 --test-intervals --test-loss-rates
```

**Options:**
- `--runs`: Number of times to run each scenario (default: 5)
- `--duration`: Duration of each test run in seconds (default: 60)
- `--baseline-only`: Run only baseline tests (skip loss and delay)
- `--test-intervals`: Test multiple reporting intervals (1s, 5s, 30s) for plotting
- `--test-loss-rates`: Test multiple loss rates (0%, 1%, 5%, 10%) for plotting

**Output:**
- Individual run results: `output/baseline_run{N}_*.csv/json`
- Aggregated results: `output/test_results.json`
- Packet captures: `output/*_run{1,2}_capture.pcap` (first 2 runs per scenario)

**Example:**
```bash
# Run all tests 5 times with 60-second duration
sudo python scripts/run_all_tests.py --runs 5 --duration 60

# Quick test with 3 runs of 30 seconds each
sudo python scripts/run_all_tests.py --runs 3 --duration 30

# Generate comprehensive data for plotting (takes longer)
sudo python scripts/run_all_tests.py --runs 5 --duration 60 --test-intervals --test-loss-rates
```

### 5. generate_plots.py

Generates visualizations from test results for analysis and reporting.

**Usage:**
```bash
python scripts/generate_plots.py [OPTIONS]
```

**Options:**
- `--results-file`: Path to test results JSON file (default: output/test_results.json)
- `--output-dir`: Directory to save plot PNG files (default: output)

**Generated Plots:**
1. `bytes_per_report_vs_interval.png`: Shows protocol efficiency across different reporting intervals
2. `duplicate_rate_vs_loss.png`: Shows duplicate detection performance under various packet loss conditions

**Example:**
```bash
# Generate plots from test results
python scripts/generate_plots.py

# Use custom results file
python scripts/generate_plots.py --results-file output/custom_results.json --output-dir plots
```

**Requirements:**
- Test data must be generated first using `run_all_tests.py` with `--test-intervals` and/or `--test-loss-rates` flags
- matplotlib must be installed: `pip install matplotlib`

**Workflow:**
```bash
# 1. Generate test data with multiple configurations
sudo python scripts/run_all_tests.py --runs 5 --duration 60 --test-intervals --test-loss-rates

# 2. Generate plots
python scripts/generate_plots.py

# 3. View plots
# Windows: start output\bytes_per_report_vs_interval.png
# Linux: xdg-open output/bytes_per_report_vs_interval.png
```

### 6. test_baseline_windows.py

Windows-compatible baseline test script with instructions for manual network impairment testing using Clumsy.

**Usage:**
```bash
python scripts/test_baseline_windows.py [OPTIONS]
```

**Options:** Same as test_baseline.py, plus:
- `--scenario-name`: Test scenario name (default: windows_baseline)

**Example:**
```bash
# Run baseline test
python scripts/test_baseline_windows.py --duration 60

# Run with packet capture (requires Wireshark)
python scripts/test_baseline_windows.py --duration 60 --enable-pcap
```

## Network Impairment on Windows (Clumsy)

For packet loss and delay/jitter testing on Windows, use Clumsy manually:

### Setup

1. Download Clumsy: https://jagt.github.io/clumsy/
2. Run as Administrator
3. Configure filters and impairments

### Packet Loss Test (5%)

1. In Clumsy:
   - Filter: `udp and udp.DstPort == 5000`
   - Enable "Drop" with 5% probability
   - Click "Start"
2. Run test: `python scripts/test_baseline_windows.py --duration 60 --scenario-name loss`
3. Click "Stop" in Clumsy when done

### Delay/Jitter Test (100ms ±10ms)

1. In Clumsy:
   - Filter: `udp and udp.DstPort == 5000`
   - Enable "Lag" with:
     - Inbound: 100ms
     - Jitter: 10ms
   - Click "Start"
2. Run test: `python scripts/test_baseline_windows.py --duration 60 --scenario-name delay`
3. Click "Stop" in Clumsy when done

## Packet Capture

### Linux

Packet capture uses `tcpdump` (usually pre-installed):

```bash
# Automatic (via test scripts)
python scripts/test_baseline.py --enable-pcap

# Manual
sudo tcpdump -i lo -w output/manual_capture.pcap udp port 5000
```

### Windows

Packet capture uses `tshark` (part of Wireshark):

1. Download Wireshark: https://www.wireshark.org/download.html
2. Install with "TShark" component
3. Add Wireshark directory to PATH (e.g., `C:\Program Files\Wireshark`)
4. Use `--enable-pcap` flag:

```bash
# Automatic (via test scripts)
python scripts/test_baseline_windows.py --enable-pcap

# Manual
tshark -i Loopback -w output/manual_capture.pcap -f "udp port 5000"
```

## Output Files

All test outputs are saved to the `output/` directory:

### CSV Logs
- Format: `{scenario}_telemetry.csv` or `{scenario}_run{N}_telemetry.csv`
- Contains: device_id, seq, timestamp, arrival_time, msg_type, duplicate_flag, gap_flag, gap_size, reading_count

### Metrics JSON
- Format: `{scenario}_metrics.json` or `{scenario}_run{N}_metrics.json`
- Contains: test configuration, metrics (bytes_per_report, packets_received, etc.), validation results

### Packet Captures
- Format: `{scenario}_capture.pcap` or `{scenario}_run{N}_capture.pcap`
- Can be analyzed with Wireshark or tcpdump

### Aggregated Results
- File: `output/test_results.json`
- Contains: Statistical summaries (min, median, max) for all scenarios

## Troubleshooting

### "Server failed to start"
- Check if port 5000 is already in use
- Try a different port: `--server-port 5001`

### "tcpdump not found" (Linux)
- Install: `sudo apt-get install tcpdump` (Debian/Ubuntu)
- Or: `sudo yum install tcpdump` (RHEL/CentOS)

### "tshark not found" (Windows)
- Install Wireshark with TShark component
- Add to PATH: `C:\Program Files\Wireshark`

### "This script must be run as root" (Linux)
- Use sudo: `sudo bash scripts/test_loss.sh`
- Or run as root user

### Packet capture not working
- Linux: Ensure tcpdump is installed and you have sudo privileges
- Windows: Ensure Wireshark/tshark is installed and in PATH
- Check firewall settings

## Example Workflow

### Complete Test Suite (Linux)

```bash
# 1. Run baseline test
python scripts/test_baseline.py --duration 60 --enable-pcap

# 2. Run packet loss test
sudo bash scripts/test_loss.sh

# 3. Run delay/jitter test
sudo bash scripts/test_delay.sh

# 4. Run all tests with statistics (5 runs each)
sudo python scripts/run_all_tests.py --runs 5 --duration 60

# 5. Check results
cat output/test_results.json
ls -lh output/*.pcap
```

### Quick Validation (Windows)

```bash
# 1. Run baseline test
python scripts/test_baseline_windows.py --duration 30

# 2. Check results
type output\windows_baseline_metrics.json
```

## Visualization and Plotting

The test suite can generate comprehensive data for visualization by testing multiple configurations:

### Generate Plot Data

```bash
# Test multiple intervals (1s, 5s, 30s) and loss rates (0%, 1%, 5%, 10%)
sudo python scripts/run_all_tests.py --runs 5 --duration 60 --test-intervals --test-loss-rates

# This will create output/test_results.json with data for both plots
```

### Create Plots

```bash
# Generate visualizations
python scripts/generate_plots.py

# Output:
# - output/bytes_per_report_vs_interval.png
# - output/duplicate_rate_vs_loss.png
```

### Plot Descriptions

**bytes_per_report_vs_interval.png**
- Shows how protocol efficiency (bytes per report) varies with reporting interval
- Lower values indicate better efficiency (less overhead)
- Useful for understanding batching benefits

**duplicate_rate_vs_loss.png**
- Shows duplicate detection rate under various packet loss conditions
- Should remain ≤1% even with 5-10% packet loss
- Validates duplicate suppression effectiveness

## Additional Resources

- Protocol specification: `docs/mini-rfc.md`
- Project README: `README.md`
- Metrics module: `src/metrics.py`
- Example usage: `scripts/example_metrics_usage.py`
- Plot generator: `scripts/generate_plots.py`
