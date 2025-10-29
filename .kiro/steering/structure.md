---
inclusion: always
---

# Project Structure

## Directory Layout

```
.
├── src/                    # Source code
│   ├── __init__.py        # Package initialization
│   ├── protocol.py        # Protocol encoding/decoding, constants, data structures
│   ├── client.py          # SensorClient implementation with CLI
│   ├── server.py          # CollectorServer implementation with CLI
│   └── metrics.py         # Metrics calculation and statistical analysis
│
├── tests/                  # Unit tests
│   ├── test_protocol.py   # Protocol encoding/decoding tests
│   ├── test_client.py     # Client logic tests
│   ├── test_server.py     # Server logic tests (duplicate, gap, reorder)
│   └── test_metrics.py    # Metrics calculation tests
│
├── scripts/                # Automation and testing scripts
│   ├── test_baseline.py   # Baseline test (no impairment)
│   ├── test_loss.sh       # Packet loss test (Linux, netem)
│   ├── test_delay.sh      # Delay/jitter test (Linux, netem)
│   ├── run_all_tests.py   # Master test runner with statistics
│   ├── generate_plots.py  # Visualization generation
│   └── generate_report.py # Summary report generator
│
├── docs/                   # Documentation
│   └── mini-rfc.md        # Protocol specification (≤3 pages)
│
├── output/                 # Generated artifacts
│   ├── *.csv              # Telemetry logs
│   ├── *.pcap             # Packet captures
│   ├── *.json             # Metrics and test results
│   ├── *.png              # Plots and visualizations
│   └── test_report.md     # Generated test summary
│
├── .kiro/                  # Kiro configuration
│   ├── specs/             # Project specifications
│   └── steering/          # AI assistant guidance (this file)
│
├── README.md               # Project overview, usage, build instructions
├── requirements.txt        # Python dependencies
└── .gitignore             # Git ignore patterns
```

## Module Organization

### src/protocol.py
- Protocol constants (VERSION, message types, sensor types, sizes)
- Data structures (`TelemetryPacket`, `SensorReading`)
- Binary encoding/decoding functions
- Validation logic

### src/client.py
- `SensorClient` class: main client implementation
- Reading generation (temperature, humidity, voltage)
- Batching logic
- UDP sending
- CLI with argparse

### src/server.py
- `CollectorServer` class: main server implementation
- `DeviceState` dataclass: per-device state tracking
- Packet reception and parsing
- Duplicate detection (sequence number tracking)
- Gap detection (missing sequences)
- Timestamp-based reordering buffer
- CSV logging
- CLI with argparse

### src/metrics.py
- `MetricsCalculator` class: compute performance metrics from logs
- `StatisticalAnalyzer` class: min/median/max calculations
- CPU profiling integration
- JSON output formatting

## Key Conventions

### File Naming
- Python modules: lowercase with underscores (`protocol.py`, `test_client.py`)
- Scripts: descriptive names with action (`test_baseline.py`, `generate_plots.py`)
- Output files: scenario and run number (`baseline_run1.pcap`, `telemetry.csv`)

### Code Organization
- One class per primary responsibility
- Dataclasses for data structures
- Functions for stateless operations
- CLI in `main()` function with `if __name__ == '__main__'` guard

### Testing
- Unit tests mirror source structure (`test_protocol.py` tests `protocol.py`)
- Integration tests in `scripts/` directory
- Mock sockets for network-independent testing
- Use pytest framework

### Configuration
- Command-line arguments for runtime configuration
- No configuration files (simplicity)
- Sensible defaults for all parameters
- Validation on startup

### Output Files
- All generated files go to `output/` directory
- CSV logs: one row per received packet
- Metrics: JSON format with nested structure
- Plots: PNG format with descriptive filenames

## Cross-Platform Considerations

- Use `pathlib.Path` for all file paths
- Use `socket` module (cross-platform)
- Avoid shell-specific commands in Python code
- Network impairment tests are Linux-only (document Windows alternatives)
- Test on both platforms before finalizing
