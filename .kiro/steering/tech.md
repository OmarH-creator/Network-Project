---
inclusion: always
---

# Technology Stack

## Language & Runtime

- **Python 3**: Cross-platform implementation using standard library
- **Minimum Version**: Python 3.7+ (for dataclasses support)

## Core Libraries

- `socket`: UDP networking (standard library)
- `struct`: Binary protocol encoding/decoding (standard library)
- `dataclasses`: Protocol data structures (standard library)
- `argparse`: Command-line interfaces (standard library)
- `csv`: Telemetry logging (standard library)
- `json`: Metrics output (standard library)
- `pathlib`: Cross-platform file paths (standard library)
- `subprocess`: Test automation (standard library)
- `matplotlib`: Visualization and plotting
- `psutil`: CPU profiling (optional)

## Protocol Specifications

- **Transport**: UDP/IP (port 5000 default, configurable)
- **Header Size**: 12 bytes fixed (binary, big-endian)
- **Max Payload**: 200 bytes (including header)
- **Encoding**: Binary using `struct.pack('!BBHII', ...)` for header
- **Message Types**: DATA (0x01), HEARTBEAT (0x02)

## Network Testing Tools

- **Linux**: `tc qdisc` with `netem` for packet loss, delay, jitter simulation
- **Packet Capture**: `tcpdump` (Linux) or `tshark` (Windows)
- **Windows**: Clumsy (manual testing only, not automated)

## Common Commands

### Running the System

```bash
# Start collector server
python src/server.py --port 5000 --log-file output/telemetry.csv

# Start sensor client
python src/client.py --device-id 1001 --server-host localhost --server-port 5000 --interval 1 --duration 60

# With batching enabled
python src/client.py --device-id 1001 --server-host localhost --server-port 5000 --interval 1 --duration 60 --batch-size 10
```

### Running Tests

```bash
# Baseline test (no impairment)
python scripts/test_baseline.py

# Packet loss test (Linux only, requires sudo)
sudo bash scripts/test_loss.sh

# Delay/jitter test (Linux only, requires sudo)
sudo bash scripts/test_delay.sh

# Run all tests with statistical analysis
python scripts/run_all_tests.py

# Generate plots
python scripts/generate_plots.py
```

### Packet Capture

```bash
# Linux
sudo tcpdump -i lo -w output/capture.pcap udp port 5000

# Windows (requires Wireshark)
tshark -i Loopback -w output/capture.pcap -f "udp port 5000"
```

### Unit Tests

```bash
# Run all unit tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_protocol.py

# With coverage
python -m pytest --cov=src tests/
```

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov

# Verify installation
python --version  # Should be 3.7+
python -c "import socket, struct, dataclasses"  # Should not error
```

## Build/Deployment Notes

- No compilation required (Python interpreted)
- No external services or databases needed
- All state maintained in memory (server) or CSV files (logs)
- Network impairment tests require root/admin privileges on Linux
