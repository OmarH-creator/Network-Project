# Implementation Plan

This document outlines the step-by-step implementation tasks for the IoT Telemetry Protocol (TinyTelemetry v1.0). Each task builds incrementally on previous tasks and references specific requirements from the requirements document.

## Task List

- [x] 1. Set up project structure and core protocol definitions





  - Create directory structure: `src/`, `tests/`, `scripts/`, `docs/`, `output/`
  - Create `src/protocol.py` with protocol constants (version, message types, header size, max payload)
  - Create `src/__init__.py` for package initialization
  - Create `requirements.txt` with dependencies (if any beyond standard library)
  - Create `.gitignore` for Python project
  - _Requirements: 1.1, 1.2, 13.1, 13.2, 13.3_

- [x] 2. Implement binary protocol encoding and decoding




  - [x] 2.1 Create packet data structures


    - In `src/protocol.py`, define `TelemetryPacket` dataclass with all header fields
    - Define `SensorReading` dataclass with sensor_type and value fields
    - Define message type constants (DATA=0x01, HEARTBEAT=0x02)
    - Define sensor type constants (TEMPERATURE=0x01, HUMIDITY=0x02, VOLTAGE=0x03)
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 2.2 Implement header encoding


    - In `src/protocol.py`, create `encode_header()` function using `struct.pack('!BBHII', ...)`
    - Validate header size is exactly 12 bytes
    - Handle network byte order (big-endian) conversion
    - _Requirements: 3.1, 3.6_



  - [x] 2.3 Implement header decoding

    - In `src/protocol.py`, create `decode_header()` function using `struct.unpack('!BBHII', ...)`
    - Validate minimum packet size (12 bytes)
    - Return parsed header fields as dictionary or dataclass
    - _Requirements: 3.1, 3.6_



  - [x] 2.4 Implement payload encoding for DATA messages

    - In `src/protocol.py`, create `encode_data_payload()` function
    - Encode reading count (1 byte) followed by readings
    - Encode each reading using `struct.pack('!Bf', sensor_type, value)`
    - Validate total packet size ≤ 200 bytes


    - _Requirements: 5.1, 5.3, 6.1, 6.2_


  - [x] 2.5 Implement payload decoding for DATA messages


    - In `src/protocol.py`, create `decode_data_payload()` function
    - Parse reading count from first byte
    - Parse each reading (5 bytes each) into SensorReading objects
    - Validate payload size matches reading count
    - _Requirements: 5.3_

  - [ ]* 2.6 Write unit tests for encoding/decoding
    - Create `tests/test_protocol.py`
    - Test header encoding produces 12 bytes
    - Test header decoding matches original values
    - Test DATA payload encoding with single and multiple readings
    - Test payload size validation (200-byte limit)
    - Test round-trip encoding/decoding
    - _Requirements: 3.1, 6.1_

- [x] 3. Implement Sensor Client (SensorClient)




  - [x] 3.1 Create client configuration and initialization


    - Create `src/client.py` with `SensorClient` class
    - Add `__init__()` method accepting device_id, server_host, server_port, interval, duration, batch_size, sensor_types
    - Initialize UDP socket using `socket.socket(socket.AF_INET, socket.SOCK_DGRAM)`
    - Initialize sequence_number to 0
    - Initialize reading_buffer as empty list (for batching)
    - _Requirements: 1.1, 7.2, 13.4_

  - [x] 3.2 Implement sensor reading generation


    - In `src/client.py`, create `generate_reading()` method
    - Generate random values: temperature (15-30°C), humidity (30-80%), voltage (3.0-5.0V)
    - Return SensorReading object with appropriate sensor_type
    - Support generating multiple sensor types per call
    - _Requirements: 2.1_

  - [x] 3.3 Implement DATA message sending


    - In `src/client.py`, create `send_data()` method accepting list of readings
    - Encode header with msg_type=DATA, current timestamp, and sequence_number
    - Encode payload with readings
    - Send packet via UDP socket to server
    - Increment sequence_number after sending
    - Log sent packet details (timestamp, seq, reading count)
    - _Requirements: 2.1, 3.2, 3.3, 3.4, 3.5, 14.3_

  - [x] 3.4 Implement HEARTBEAT message sending


    - In `src/client.py`, create `send_heartbeat()` method
    - Encode header with msg_type=HEARTBEAT, current timestamp, and sequence_number
    - Send packet with no payload (12 bytes only)
    - Increment sequence_number after sending
    - Log sent heartbeat (timestamp, seq)
    - _Requirements: 2.2, 2.3_

  - [x] 3.5 Implement batching logic


    - In `src/client.py`, create `add_to_batch()` method
    - Accumulate readings in reading_buffer
    - When buffer reaches batch_size, call send_data() with buffered readings
    - Clear buffer after sending
    - Handle batch_size=1 as non-batched mode
    - _Requirements: 5.1, 5.2, 5.4_

  - [x] 3.6 Implement main client loop


    - In `src/client.py`, create `run()` method
    - Loop until duration expires
    - Generate readings at configured interval
    - If batching enabled, add to batch; otherwise send immediately
    - Send heartbeat if no data generated in interval
    - Handle graceful shutdown on Ctrl+C
    - _Requirements: 2.4, 7.1, 7.3, 14.2_

  - [x] 3.7 Add command-line interface for client


    - In `src/client.py`, add `main()` function with argparse
    - Accept arguments: --device-id, --server-host, --server-port, --interval, --duration, --batch-size, --sensor-types
    - Validate arguments (device_id > 0, interval in [1,5,30], etc.)
    - Create and run SensorClient instance
    - Add `if __name__ == '__main__'` block
    - _Requirements: 7.2, 13.1, 13.2, 13.3_

  - [ ]* 3.8 Write unit tests for client
    - Create `tests/test_client.py`
    - Test reading generation produces valid ranges
    - Test sequence number increments correctly
    - Test batching accumulates readings correctly
    - Test batch sends when size reached
    - Mock socket to test sending without network
    - _Requirements: 7.3_

- [x] 4. Implement Collector Server (CollectorServer)








 

  - [x] 4.1 Create server configuration and initialization



    - Create `src/server.py` with `CollectorServer` class
    - Add `__init__()` method accepting listen_port, log_file, reorder_window, reorder_timeout
    - Initialize UDP socket and bind to `('0.0.0.0', listen_port)`
    - Set socket option `SO_REUSEADDR` for quick restart
    - Initialize device_states dictionary (empty)
    - Initialize CSV log file with headers
    - _Requirements: 1.1, 8.2, 12.1, 12.2, 13.4_


  - [x] 4.2 Implement per-device state management

    - In `src/server.py`, create `DeviceState` dataclass
    - Include fields: device_id, last_seq, last_timestamp, total_packets, duplicate_count, gap_count, seen_sequences (set), reorder_buffer (list)
    - Create `get_or_create_device_state()` method
    - Initialize new device state on first packet from device
    - _Requirements: 8.1, 8.2, 8.3_


  - [x] 4.3 Implement packet reception and parsing

    - In `src/server.py`, create `receive_packet()` method
    - Receive UDP packet with `socket.recvfrom()`
    - Record arrival_time immediately upon receipt
    - Decode header using protocol.decode_header()
    - Validate header (version, message type, device_id > 0)
    - Decode payload based on message type
    - Return parsed packet and arrival_time, or None if invalid
    - _Requirements: 3.6, 12.4_


  - [x] 4.4 Implement duplicate detection

    - In `src/server.py`, create `check_duplicate()` method
    - Check if sequence_number exists in device_state.seen_sequences
    - If duplicate, increment device_state.duplicate_count and return True
    - If new, add to seen_sequences and return False
    - _Requirements: 9.1, 9.2, 9.3, 9.4_


  - [x] 4.5 Implement sequence gap detection

    - In `src/server.py`, create `detect_gap()` method
    - Calculate expected_seq = device_state.last_seq + 1
    - If received seq > expected_seq, calculate gap_size = seq - expected_seq
    - Increment device_state.gap_count by gap_size
    - Update device_state.last_seq to received seq
    - Return gap_size (0 if no gap)
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [x] 4.6 Implement timestamp-based reordering


    - In `src/server.py`, create `add_to_reorder_buffer()` method
    - Add packet to device_state.reorder_buffer as (seq, timestamp, data) tuple
    - Limit buffer size to reorder_window (default 10)
    - Create `flush_reorder_buffer()` method
    - Sort buffer by timestamp
    - Return sorted packets for logging
    - Clear buffer after flush
    - _Requirements: 11.1, 11.2, 11.3_

  - [x] 4.7 Implement CSV logging


    - In `src/server.py`, create `log_packet()` method
    - Write CSV row with fields: device_id, seq, timestamp, arrival_time, msg_type, duplicate_flag, gap_flag, gap_size, reading_count
    - Flush CSV file periodically (every 10 packets or 1 second)
    - Handle file write errors gracefully
    - _Requirements: 12.1, 12.2, 12.3, 12.4_


  - [x] 4.8 Implement main server loop

    - In `src/server.py`, create `run()` method
    - Loop indefinitely receiving packets
    - For each packet: parse → check duplicate → detect gap → buffer → log
    - Periodically flush reorder buffers (every reorder_timeout seconds)
    - Handle graceful shutdown on Ctrl+C
    - Print summary statistics on shutdown
    - _Requirements: 8.3, 14.3_


  - [x] 4.9 Add command-line interface for server

    - In `src/server.py`, add `main()` function with argparse
    - Accept arguments: --port, --log-file, --reorder-window, --reorder-timeout
    - Create and run CollectorServer instance
    - Add `if __name__ == '__main__'` block
    - _Requirements: 13.1, 13.2, 13.3_

  - [ ]* 4.10 Write unit tests for server
    - Create `tests/test_server.py`
    - Test device state initialization
    - Test duplicate detection with repeated sequences
    - Test gap detection with missing sequences
    - Test reordering with out-of-order timestamps
    - Mock socket to test receiving without network
    - Test CSV logging format
    - _Requirements: 9.4, 10.4, 11.3_

- [x] 5. Implement metrics collection and analysis




  - [x] 5.1 Create metrics calculator


    - Create `src/metrics.py` with `MetricsCalculator` class
    - Implement `calculate_from_csv()` method to read log file
    - Calculate bytes_per_report: (header_size + avg_payload_size)
    - Calculate packets_received: count of non-duplicate packets
    - Calculate duplicate_rate: duplicate_count / total_packets
    - Calculate sequence_gap_count: sum of all gaps
    - _Requirements: 18.1, 18.2, 18.3, 18.4_

  - [x] 5.2 Implement CPU profiling


    - In `src/metrics.py`, add `measure_cpu_time()` function
    - Use `time.process_time()` to measure CPU time
    - Calculate cpu_ms_per_report: total_cpu_time / packets_processed * 1000
    - Integrate with server to measure processing time
    - _Requirements: 18.5_

  - [x] 5.3 Implement statistical analysis


    - In `src/metrics.py`, create `StatisticalAnalyzer` class
    - Implement `calculate_statistics()` method accepting list of metric values
    - Calculate median using `statistics.median()`
    - Calculate min and max
    - Return dictionary with min, median, max
    - _Requirements: 19.1, 19.2, 19.3_

  - [x] 5.4 Create metrics output formatter


    - In `src/metrics.py`, create `save_metrics_json()` function
    - Accept metrics dictionary and output file path
    - Format as JSON with test scenario, duration, metrics, and statistics
    - Write to file with pretty printing (indent=2)
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_

  - [ ]* 5.5 Write unit tests for metrics
    - Create `tests/test_metrics.py`
    - Test metrics calculation with sample CSV data
    - Test statistical analysis with known values
    - Test JSON output format
    - _Requirements: 19.1, 19.2, 19.3_

- [x] 6. Create automated testing scripts





  - [x] 6.1 Create baseline test script

    - Create `scripts/test_baseline.py`
    - Start server in background process
    - Wait for server to be ready (1 second)
    - Start client with: interval=1s, duration=60s, batch_size=1
    - Wait for client to complete
    - Stop server gracefully
    - Calculate metrics from CSV log
    - Verify ≥99% packet delivery
    - Verify sequence numbers are in order
    - _Requirements: 15.1, 15.2, 15.3_


  - [x] 6.2 Create packet loss test script (Linux)

    - Create `scripts/test_loss.sh` (Bash script)
    - Apply netem: `sudo tc qdisc add dev lo root netem loss 5%`
    - Run baseline test script (reuse test_baseline.py with different params)
    - Remove netem: `sudo tc qdisc del dev lo root`
    - Calculate metrics from CSV log
    - Verify gap detection works
    - Verify duplicate_rate ≤1%
    - _Requirements: 16.1, 16.2, 16.3, 16.4_


  - [x] 6.3 Create delay/jitter test script (Linux)

    - Create `scripts/test_delay.sh` (Bash script)
    - Apply netem: `sudo tc qdisc add dev lo root netem delay 100ms 10ms`
    - Run baseline test script (reuse test_baseline.py with different params)
    - Remove netem: `sudo tc qdisc del dev lo root`
    - Calculate metrics from CSV log
    - Verify reordering works (check timestamps vs arrival times)
    - Verify no crashes (check exit code)
    - _Requirements: 17.1, 17.2, 17.3, 17.4_

  - [x] 6.4 Create master test runner


    - Create `scripts/run_all_tests.py`
    - Run each test scenario 5 times
    - Collect metrics from each run
    - Calculate statistical summary (min, median, max)
    - Save aggregated results to `output/test_results.json`
    - Print summary table to console
    - _Requirements: 14.1, 19.1, 19.2, 19.3, 19.4_

  - [x] 6.5 Add packet capture to test scripts


    - Modify test scripts to start tcpdump before tests
    - Capture command: `tcpdump -i lo -w output/{scenario}_run{n}.pcap udp port 5000`
    - Stop tcpdump after test completes
    - Ensure at least 2 pcap files per scenario
    - Add Windows alternative using Wireshark CLI (tshark) in comments
    - _Requirements: 14.4_

  - [x] 6.6 Create Windows-compatible test script


    - Create `scripts/test_baseline_windows.py`
    - Same logic as test_baseline.py but without netem
    - Add instructions in comments for using Clumsy manually
    - Ensure cross-platform path handling with pathlib
    - _Requirements: 13.1, 13.2, 13.3_

- [x] 7. Create visualization and reporting




  - [x] 7.1 Create plotting script


    - Create `scripts/generate_plots.py`
    - Use matplotlib to create plots
    - Plot 1: bytes_per_report vs reporting_interval (line plot)
    - Plot 2: duplicate_rate vs loss_percentage (line plot)
    - Save plots to `output/` directory as PNG files
    - _Requirements: 20.4_

  - [x] 7.2 Generate test data for plots


    - Modify `run_all_tests.py` to test multiple intervals (1s, 5s, 30s)
    - Modify loss test to test multiple loss rates (0%, 1%, 5%, 10%)
    - Collect metrics for each configuration
    - Save data in format suitable for plotting
    - _Requirements: 7.1, 7.3, 20.4_

  - [ ]* 7.3 Create summary report generator
    - Create `scripts/generate_report.py`
    - Read test_results.json
    - Generate markdown report with tables and statistics
    - Include plot images
    - Save to `output/test_report.md`
    - _Requirements: 19.4_

- [x] 8. Create project documentation





  - [x] 8.1 Write Mini-RFC document


    - Create `docs/mini-rfc.md`
    - Section 1: Introduction (protocol name, version, purpose)
    - Section 2: Protocol Architecture (components, communication model)
    - Section 3: Message Formats (header table, field sizes, encoding, message types)
    - Section 4: Batching Design (max batch size, rationale)
    - Section 5: Field Packing Strategy (binary encoding, struct format)
    - Ensure document is ≤3 pages when formatted
    - _Requirements: 20.1_

  - [x] 8.2 Write comprehensive README


    - Create `README.md` in project root
    - Section: Project Overview
    - Section: Build Instructions (Python version, dependencies)
    - Section: Usage Examples (client and server commands)
    - Section: Running Tests (baseline, loss, delay)
    - Section: Batching Decision Explanation
    - Section: Field Packing Strategy
    - Section: Cross-Platform Notes (Linux vs Windows)
    - Section: Output Files (CSV logs, metrics, pcaps, plots)
    - _Requirements: 20.5_

  - [x] 8.3 Create requirements.txt

    - List all Python dependencies with versions
    - Include: matplotlib (for plots), psutil (for CPU metrics, optional)
    - Ensure all dependencies are cross-platform
    - _Requirements: 13.1, 13.2, 13.3_

  - [x] 8.4 Add inline code documentation


    - Add docstrings to all classes and methods
    - Document function parameters and return values
    - Add comments for complex logic (e.g., gap detection, reordering)
    - Follow PEP 257 docstring conventions
    - _Requirements: 20.5_

- [x] 9. Final integration and validation






  - [x] 9.1 Run complete test suite

    - Execute `scripts/run_all_tests.py` on Linux
    - Verify all tests pass
    - Verify metrics are within expected ranges
    - Verify pcap files are generated
    - _Requirements: 14.1, 14.4, 15.1, 16.1, 17.1_


  - [x] 9.2 Validate cross-platform compatibility

    - Run client and server on Windows
    - Run baseline test on Windows
    - Verify CSV logs are identical format
    - Verify no platform-specific errors
    - _Requirements: 13.1, 13.2, 13.3_

  - [x] 9.3 Generate final deliverables


    - Run `generate_plots.py` to create visualizations
    - Verify plots show expected trends
    - Ensure all output files are in `output/` directory
    - Create archive with all deliverables
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_


  - [x] 9.4 Review and polish documentation

    - Proofread Mini-RFC for clarity and completeness
    - Proofread README for accuracy
    - Verify all commands in README work as documented
    - Check that Mini-RFC is ≤3 pages
    - _Requirements: 20.1, 20.5_
