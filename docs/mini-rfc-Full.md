# TinyTelemetry v1.0 Protocol Specification

**Status:** Experimental  
**Version:** 1.0  
**Date:** October 2025

## 1. Introduction

TinyTelemetry v1.0 is a lightweight, UDP-based application-layer protocol designed for constrained IoT sensors to transmit periodic telemetry data to a central collector. The protocol prioritizes simplicity, bandwidth efficiency, and loss tolerance over reliability guarantees.

### 1.1 Purpose

The protocol enables resource-constrained IoT devices (e.g., temperature, humidity, and voltage sensors) to efficiently transmit small sensor readings to a central collector over unreliable networks. The design assumes that occasional data loss is acceptable for telemetry use cases, eliminating the need for complex retransmission mechanisms.

### 1.2 Design Goals

- **Minimal overhead**: Compact binary encoding with 12-byte fixed header
- **Loss tolerance**: No per-packet retransmissions; designed to operate under 5% packet loss
- **Bandwidth efficiency**: Optional batching to reduce header overhead
- **Simplicity**: Stateless clients, straightforward encoding/decoding
- **Cross-platform**: Pure UDP/IP implementation compatible with Linux and Windows

## 2. Protocol Architecture

### 2.1 System Components

The TinyTelemetry system consists of two primary components:

- **Sensor Client**: Simulates IoT sensors, generates readings, encodes packets, and transmits via UDP
- **Collector Server**: Receives packets, maintains per-device state, detects duplicates and gaps, reorders by timestamp, and logs to CSV

### 2.2 Communication Model

- **Transport**: UDP/IP (default port 5000, configurable)
- **Direction**: Unidirectional (client → server)
- **Reliability**: Fire-and-forget; no acknowledgments or retransmissions
- **State**: Stateless clients with monotonic sequence counters; stateful server for duplicate detection and gap analysis

### 2.3 Packet Flow

```
Sensor Client                    Collector Server
     |                                  |
     |  1. Generate readings            |
     |  2. Encode packet                |
     |  3. Send UDP packet              |
     |--------------------------------->|
     |                                  |  4. Receive & parse
     |                                  |  5. Check duplicate
     |                                  |  6. Detect gaps
     |                                  |  7. Reorder by timestamp
     |                                  |  8. Log to CSV
```

## 3. Message Formats

### 3.1 Protocol Header

All packets begin with a fixed 12-byte header in network byte order (big-endian):

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    Version    |  Msg Type     |          Device ID            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Timestamp (seconds)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

**Field Specifications:**

| Field | Offset | Size | Type | Description |
|-------|--------|------|------|-------------|
| Version | 0 | 1 byte | uint8 | Protocol version (0x01 for v1.0) |
| Msg Type | 1 | 1 byte | uint8 | Message type: 0x01=DATA, 0x02=HEARTBEAT |
| Device ID | 2 | 2 bytes | uint16 | Unique sensor identifier (1-65535) |
| Sequence Number | 4 | 4 bytes | uint32 | Monotonic counter per device (0 to 4,294,967,295) |
| Timestamp | 8 | 4 bytes | uint32 | Unix epoch time in seconds |

**Encoding:** All multi-byte fields use big-endian (network byte order).

### 3.2 DATA Message

DATA messages carry one or more sensor readings. The payload format is:

```
[Header: 12 bytes][Count: 1 byte][Reading 1: 5 bytes]...[Reading N: 5 bytes]
```

**Reading Format (5 bytes each):**

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Sensor Type  |                  Value (float32)              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| Field | Size | Type | Description |
|-------|------|------|-------------|
| Sensor Type | 1 byte | uint8 | 0x01=Temperature (°C), 0x02=Humidity (%), 0x03=Voltage (V) |
| Value | 4 bytes | float32 | IEEE 754 single-precision floating point |

**Payload Structure:**
- Byte 0: Reading count (1-37)
- Bytes 1-5: First reading
- Bytes 6-10: Second reading (if present)
- ...

**Maximum Payload:** 200 bytes total (including header)

### 3.3 HEARTBEAT Message

HEARTBEAT messages indicate device liveness when no new data is available. They consist of the 12-byte header only (no payload).

```
[Header: 12 bytes]
```

Clients send HEARTBEAT messages at configured reporting intervals when no DATA is generated.

## 4. Batching Design

### 4.1 Rationale

Batching multiple sensor readings into a single packet reduces header overhead and packet rate, improving bandwidth efficiency and reducing collision probability in high-density deployments.

**Overhead Analysis:**
- **Non-batched (1 reading/packet):** 12 + 1 + 5 = 18 bytes → 72% overhead
- **Batched (10 readings/packet):** 12 + 1 + 50 = 63 bytes → 21% overhead per reading
- **Maximum batch (37 readings/packet):** 12 + 1 + 185 = 198 bytes → 7% overhead per reading

### 4.2 Maximum Batch Size

**Calculation:**
```
Max readings = (MAX_PAYLOAD - HEADER_SIZE - COUNT_BYTE) / READING_SIZE
             = (200 - 12 - 1) / 5
             = 37 readings
```

### 4.3 Trade-offs

- **Larger batches:** Better bandwidth efficiency, higher latency (must wait to accumulate readings)
- **Smaller batches:** Lower latency, more overhead, higher packet rate
- **Default:** batch_size=1 (non-batched) for simplicity; configurable up to 37

### 4.4 Implementation

Clients maintain a reading buffer. When the buffer reaches the configured batch size, all buffered readings are encoded into a single DATA packet and transmitted. The batch size is configurable via command-line argument (--batch-size).

## 5. Field Packing Strategy

### 5.1 Binary Encoding

TinyTelemetry uses compact binary encoding to minimize bandwidth usage. All fields are packed using the Python `struct` module with network byte order.

**Header Encoding:**
```python
struct.pack('!BBHII', version, msg_type, device_id, seq_num, timestamp)
```

**Reading Encoding:**
```python
struct.pack('!Bf', sensor_type, value)
```

Format codes:
- `!` = Network byte order (big-endian)
- `B` = Unsigned char (1 byte)
- `H` = Unsigned short (2 bytes)
- `I` = Unsigned int (4 bytes)
- `f` = Float (4 bytes, IEEE 754)

### 5.2 Advantages

- **Deterministic size:** Fixed-size fields enable precise bandwidth calculations
- **Fast encoding/decoding:** Binary operations are faster than text parsing
- **Compact representation:** No text overhead (e.g., JSON, XML)
- **Cross-platform:** Network byte order ensures compatibility across architectures

### 5.3 Size Efficiency

| Component | Size | Notes |
|-----------|------|-------|
| Header | 12 bytes | Fixed for all packets |
| Reading count | 1 byte | Only in DATA messages |
| Per reading | 5 bytes | 1 byte type + 4 bytes value |
| HEARTBEAT | 12 bytes | Header only |
| DATA (1 reading) | 18 bytes | 12 + 1 + 5 |
| DATA (10 readings) | 63 bytes | 12 + 1 + 50 |
| DATA (37 readings) | 198 bytes | Maximum size |

## 4. Communication Procedures

### 4.1 Session Start

TinyTelemetry uses a sessionless model. There is no explicit connection establishment or handshake.

**Client Startup Sequence:**
1. Client initializes with device_id, server address, and configuration parameters
2. Client sets sequence number to 0
3. Client begins periodic transmission immediately

**Server Startup Sequence:**
1. Server binds to UDP port (default 5000)
2. Server enters listening state
3. Upon receiving first packet from a device, server initializes per-device state

**First Packet Handling:**
```
Client (device_id=1001)          Server
        |                           |
        | seq=0, DATA packet        |
        |-------------------------->|
        |                           | - Create DeviceState(1001)
        |                           | - Set last_seq = 0
        |                           | - Initialize reorder buffer
        |                           | - Log packet to CSV
```

### 4.2 Normal Data Exchange

**Periodic Transmission:**
1. Client generates sensor readings at configured interval (1s, 5s, or 30s)
2. Client encodes readings into DATA packet with incremented sequence number
3. Client sends UDP packet to server (fire-and-forget)
4. Server receives packet, checks for duplicates/gaps, reorders if needed, logs to CSV

**Example Exchange:**
```
Time    Client Action                    Server Action
----    -------------                    -------------
T+0s    Send seq=0, temp=25.0°C         Receive seq=0, log
T+1s    Send seq=1, temp=25.1°C         Receive seq=1, log
T+2s    Send seq=2, temp=25.2°C         Receive seq=2, log
T+3s    Send seq=3, temp=25.3°C         (packet lost)
T+4s    Send seq=4, temp=25.4°C         Receive seq=4, detect gap, log
```

### 4.3 Batching Mode

When batching is enabled (batch_size > 1):

1. Client accumulates readings in buffer
2. When buffer reaches batch_size, encode all readings into single DATA packet
3. Send packet with current sequence number
4. Clear buffer and continue

**Batched Exchange Example:**
```
Time    Client Action                           Server Action
----    -------------                           -------------
T+0s    Generate reading 1, buffer it          -
T+1s    Generate reading 2, buffer it          -
T+2s    Generate reading 3, buffer full        -
        Send seq=0 with 3 readings             Receive seq=0, log 3 readings
T+3s    Generate reading 4, buffer it          -
T+4s    Generate reading 5, buffer it          -
T+5s    Generate reading 6, buffer full        -
        Send seq=1 with 3 readings             Receive seq=1, log 3 readings
```

### 4.4 Error Handling

**Duplicate Detection:**
- Server maintains last_seq for each device
- If received seq ≤ last_seq, mark as duplicate
- Log duplicate with duplicate_flag=True
- Do not update device state

**Gap Detection:**
- If received seq > last_seq + 1, gap detected
- Calculate gap_size = seq - last_seq - 1
- Log packet with gap_flag=True and gap_size
- Update last_seq to received seq

**Out-of-Order Packets:**
- Server maintains reorder buffer (default size: 10 packets)
- Packets buffered for up to 2 seconds (configurable)
- Packets flushed from buffer in timestamp order
- If buffer full, oldest packet flushed regardless of timestamp

**Malformed Packets:**
- If packet size < 12 bytes, discard silently
- If version != 0x01, discard and log error
- If msg_type invalid, discard and log error
- If DATA packet has reading_count = 0, discard

### 4.5 Session Termination

**Client Shutdown:**
1. Client completes configured duration
2. Client stops generating readings
3. Client exits (no explicit shutdown message)

**Server Shutdown:**
1. Server receives SIGINT (Ctrl+C)
2. Server flushes all reorder buffers
3. Server closes CSV log file
4. Server exits

**No explicit teardown protocol** - sessionless design means either party can stop at any time.

## 5. Reliability & Performance Features

### 5.1 Loss Tolerance Strategy

TinyTelemetry is designed to operate without retransmissions. The protocol accepts packet loss as inherent to UDP and focuses on detection rather than recovery.

**Design Rationale:**
- Telemetry data is time-series: next reading supersedes previous
- Retransmissions add complexity and latency
- For periodic data, missing one sample is acceptable
- Target: operate reliably under ≤5% packet loss

**Loss Detection Mechanisms:**
1. **Sequence gaps:** Server detects missing sequence numbers
2. **Gap logging:** All gaps recorded in CSV for analysis
3. **No recovery:** Server does not request retransmission

### 5.2 Duplicate Handling

**Duplicate Sources:**
- Network-level duplication (rare in UDP)
- Application-level retries (not used in TinyTelemetry)
- Testing scenarios with intentional duplication

**Duplicate Detection:**
```python
if packet.seq_num <= device_state.last_seq:
    mark_as_duplicate()
    log_but_do_not_process()
```

**Duplicate Rate Metric:**
```
duplicate_rate = duplicate_count / total_packets_received
```

Target: <1% duplicate rate under normal conditions

### 5.3 Reordering Strategy

**Problem:** UDP does not guarantee in-order delivery. Packets may arrive out of sequence due to network path variations.

**Solution:** Timestamp-based reordering buffer

**Algorithm:**
1. Incoming packet placed in reorder buffer
2. Buffer sorted by timestamp (not sequence number)
3. Packets held for up to reorder_timeout seconds (default: 2.0s)
4. Packets flushed when:
   - Timeout expires
   - Buffer reaches max size (default: 10 packets)
   - Packet is oldest in buffer and timeout reached

**Configuration:**
- `--reorder-window`: Maximum buffer size (default: 10)
- `--reorder-timeout`: Maximum hold time in seconds (default: 2.0)

**Trade-offs:**
- Larger buffer: Better reordering, more memory
- Longer timeout: Better reordering, higher latency
- Smaller buffer/timeout: Lower latency, less reordering

### 5.4 Batching for Efficiency

**Bandwidth Overhead Reduction:**

| Batch Size | Packet Size | Overhead per Reading | Efficiency Gain |
|------------|-------------|---------------------|-----------------|
| 1 | 18 bytes | 72% | Baseline |
| 5 | 38 bytes | 40% | 44% improvement |
| 10 | 63 bytes | 21% | 71% improvement |
| 37 | 198 bytes | 7% | 90% improvement |

**Latency Trade-off:**
- Non-batched (batch_size=1): Immediate transmission, 72% overhead
- Batched (batch_size=10): Wait for 10 readings, 21% overhead
- Maximum batch (batch_size=37): Wait for 37 readings, 7% overhead

**Recommendation:** batch_size=10 provides good balance (71% efficiency gain with acceptable latency)

### 5.5 No Timers or Retransmission

**Deliberate Design Choice:**
- No RTO (Retransmission Timeout) calculation needed
- No RTT estimation required
- No congestion control
- No flow control

**Justification:**
- Simplifies client implementation (critical for constrained devices)
- Reduces power consumption (no ACK waiting)
- Appropriate for loss-tolerant telemetry use case
- Server-side complexity acceptable (more resources available)

### 5.6 Performance Metrics

**Key Metrics Tracked:**
1. **Delivery Rate:** packets_received / packets_sent
2. **Duplicate Rate:** duplicate_count / total_packets
3. **Gap Count:** Total missing sequence numbers detected
4. **Bytes per Report:** Average packet size
5. **CPU Time:** Processing time per packet (optional)

**Target Performance:**
- Delivery rate: ≥99% (baseline), ≥95% (5% loss)
- Duplicate rate: <1%
- Sequence gaps: Detected and logged accurately
- Bytes per report: 18 bytes (non-batched), 63 bytes (batch_size=10)

## 6. Experimental Evaluation Plan

### 6.1 Test Scenarios

**Baseline (No Impairment):**
- Purpose: Validate protocol under ideal conditions
- Expected: ≥99% delivery, sequence numbers in order
- Command: `python scripts/test_baseline.py --duration 60`

**Packet Loss (5%):**
- Purpose: Validate loss tolerance and gap detection
- Network condition: 5% random packet loss
- Expected: ≥95% delivery, gaps detected correctly
- Linux command: `sudo bash scripts/test_loss.sh`
- Windows: Manual testing with Clumsy tool

**Delay and Jitter (100ms ±10ms):**
- Purpose: Validate reordering mechanism
- Network condition: 100ms delay with ±10ms jitter
- Expected: Packets reordered by timestamp, no crashes
- Linux command: `sudo bash scripts/test_delay.sh`
- Windows: Manual testing with Clumsy tool

### 6.2 Metrics Collection

**Automated Metrics:**
- CSV logs: All received packets with metadata
- JSON metrics: Calculated performance statistics
- PCAP files: Network-level packet captures (optional)

**Metrics Calculated:**
```python
from src.metrics import MetricsCalculator

calculator = MetricsCalculator()
metrics = calculator.calculate_from_csv('output/telemetry.csv')

print(f"Delivery rate: {metrics.delivery_rate:.2%}")
print(f"Duplicate rate: {metrics.duplicate_rate:.2%}")
print(f"Sequence gaps: {metrics.sequence_gap_count}")
print(f"Bytes per report: {metrics.bytes_per_report:.2f}")
```

### 6.3 Network Impairment Simulation

**Linux (using tc and netem):**

Packet loss (5%):
```bash
sudo tc qdisc add dev lo root netem loss 5%
# Run test
sudo tc qdisc del dev lo root
```

Delay and jitter (100ms ±10ms):
```bash
sudo tc qdisc add dev lo root netem delay 100ms 10ms
# Run test
sudo tc qdisc del dev lo root
```

**Windows (using Clumsy):**
1. Download Clumsy from https://jagt.github.io/clumsy/
2. Run as Administrator
3. Filter: `udp.DstPort == 5000`
4. Enable "Drop" with 5% probability for packet loss
5. Enable "Lag" with 100ms for delay testing

**Cross-Platform Alternative:**
- Use virtual machines or containers with network namespaces
- Docker with network emulation plugins
- Cloud instances with configurable network policies

### 6.4 Automated Test Execution

**Master Test Runner:**
```bash
python scripts/run_all_tests.py --runs 5 --duration 60
```

This script:
1. Runs each scenario 5 times
2. Collects metrics from each run
3. Calculates statistical summary (min, median, max)
4. Saves aggregated results to `output/test_results.json`

**Statistical Analysis:**
```python
from src.metrics import StatisticalAnalyzer

analyzer = StatisticalAnalyzer()
stats = analyzer.calculate_statistics(delivery_rates)

print(f"Min: {stats['min']:.2%}")
print(f"Median: {stats['median']:.2%}")
print(f"Max: {stats['max']:.2%}")
```

### 6.5 Visualization

**Generate Plots:**
```bash
python scripts/generate_plots.py
```

Produces:
- `bytes_per_report_vs_interval.png`: Bandwidth efficiency across intervals
- `duplicate_rate_vs_loss.png`: Duplicate detection under packet loss

## 7. Example Use Case Walkthrough

### 7.1 Scenario Description

A temperature sensor (device_id=1001) transmits readings every 1 second for 10 seconds to a collector server on localhost:5000.

### 7.2 Step-by-Step Trace

**T=0s: Server Startup**
```
$ python -m src.server --port 5000 --log-file output/example.csv
CollectorServer initialized on port 5000
Logging to: output/example.csv
CollectorServer running. Press Ctrl+C to stop.
```

**T=1s: Client Startup**
```
$ python -m src.client --device-id 1001 --interval 1 --duration 10
[INFO] Starting sensor client (device_id=1001)
[INFO] Server: localhost:5000
[INFO] Interval: 1s, Duration: 10s, Batch: 1
```

**T=1s: First Packet Sent**
```
Client generates:
- Temperature: 25.0°C
- Humidity: 50.0%
- Voltage: 5.0V

Encodes packet:
- Version: 0x01
- MsgType: 0x01 (DATA)
- DeviceID: 1001 (0x03E9)
- SeqNum: 0
- Timestamp: 1698765432
- ReadingCount: 3
- Readings: [temp=25.0, humid=50.0, volt=5.0]

Packet size: 28 bytes
Hex: 01 01 03 E9 00 00 00 00 65 4A 2B 18 03 01 41 C8 00 00 02 42 48 00 00 03 40 A0 00 00

Sends UDP packet to localhost:5000
[DATA] seq=0, timestamp=1698765432, readings=3, bytes=28
```

**T=1s: Server Receives First Packet**
```
Server receives 28 bytes from 127.0.0.1:xxxxx
Parses header: version=1, msg_type=DATA, device_id=1001, seq=0
Device 1001 not in state table
Initialized state for device 1001
Parses 3 readings: temp=25.0, humid=50.0, volt=5.0
No duplicate (first packet)
No gap (first packet)
Logs to CSV:
1001,0,1698765432,1698765432.123456,DATA,False,False,0,3
```

**T=2s: Second Packet**
```
Client: [DATA] seq=1, timestamp=1698765433, readings=3, bytes=28
Server: Received seq=1, last_seq=0, no gap, no duplicate
CSV: 1001,1,1698765433,1698765433.125678,DATA,False,False,0,3
```

**T=3s: Third Packet**
```
Client: [DATA] seq=2, timestamp=1698765434, readings=3, bytes=28
Server: Received seq=2, last_seq=1, no gap, no duplicate
CSV: 1001,2,1698765434,1698765434.127890,DATA,False,False,0,3
```

**T=4s: Fourth Packet (LOST)**
```
Client: [DATA] seq=3, timestamp=1698765435, readings=3, bytes=28
(Packet lost in network - simulated)
Server: (no packet received)
```

**T=5s: Fifth Packet (Gap Detected)**
```
Client: [DATA] seq=4, timestamp=1698765436, readings=3, bytes=28
Server: Received seq=4, last_seq=2, GAP DETECTED
        gap_size = 4 - 2 - 1 = 1
        Logs with gap_flag=True
CSV: 1001,4,1698765436,1698765436.130123,DATA,False,True,1,3
```

**T=6s-10s: Remaining Packets**
```
T=6s: seq=5, no gap
T=7s: seq=6, no gap
T=8s: seq=7, no gap
T=9s: seq=8, no gap
T=10s: seq=9, no gap
```

**T=11s: Client Completes**
```
[INFO] Duration 10s reached, stopping...
Client exits
```

**T=12s: Server Shutdown**
```
^C (Ctrl+C pressed)
Shutting down...
Server exits
```

### 7.3 CSV Log Output

```csv
device_id,seq,timestamp,arrival_time,msg_type,duplicate_flag,gap_flag,gap_size,reading_count
1001,0,1698765432,1698765432.123456,DATA,False,False,0,3
1001,1,1698765433,1698765433.125678,DATA,False,False,0,3
1001,2,1698765434,1698765434.127890,DATA,False,False,0,3
1001,4,1698765436,1698765436.130123,DATA,False,True,1,3
1001,5,1698765437,1698765437.132345,DATA,False,False,0,3
1001,6,1698765438,1698765438.134567,DATA,False,False,0,3
1001,7,1698765439,1698765439.136789,DATA,False,False,0,3
1001,8,1698765440,1698765440.138901,DATA,False,False,0,3
1001,9,1698765441,1698765441.141023,DATA,False,False,0,3
```

### 7.4 Metrics Summary

```
Packets sent: 10
Packets received: 9
Delivery rate: 90.0%
Duplicate rate: 0.0%
Sequence gaps: 1 (seq=3 missing)
Bytes per report: 9.33 bytes/reading (28 bytes / 3 readings)
```

### 7.5 PCAP Excerpt (if captured)

```
Frame 1: 42 bytes on wire (336 bits), 42 bytes captured (336 bits)
Ethernet II, Src: 00:00:00:00:00:00, Dst: 00:00:00:00:00:00
Internet Protocol Version 4, Src: 127.0.0.1, Dst: 127.0.0.1
User Datagram Protocol, Src Port: 54321, Dst Port: 5000
Data (28 bytes):
0000   01 01 03 e9 00 00 00 00 65 4a 2b 18 03 01 41 c8   ........eJ+...A.
0010   00 00 02 42 48 00 00 03 40 a0 00 00               ...BH...@...
```

## 8. Limitations & Future Work

### 8.1 Current Limitations

**1. No Encryption or Authentication**
- All data transmitted in plaintext
- No device authentication mechanism
- Vulnerable to spoofing and eavesdropping
- **Impact:** Unsuitable for sensitive data or untrusted networks
- **Mitigation:** Use VPN or add DTLS layer in future version

**2. No Congestion Control**
- Fixed transmission rate regardless of network conditions
- Could contribute to network congestion
- **Impact:** May cause packet loss in congested networks
- **Mitigation:** Implement adaptive rate control based on loss detection

**3. Limited Error Recovery**
- No retransmission mechanism
- Gaps are detected but not filled
- **Impact:** Data loss is permanent
- **Mitigation:** Acceptable for telemetry; critical data needs different protocol

**4. Fixed Maximum Packet Size (200 bytes)**
- Limits batch size to 37 readings
- Cannot transmit larger payloads
- **Impact:** Not suitable for image data or large sensor arrays
- **Mitigation:** Implement fragmentation/reassembly for larger payloads

**5. Timestamp Resolution (1 second)**
- Unix epoch seconds only, no milliseconds
- Insufficient for high-frequency sampling
- **Impact:** Cannot distinguish events within same second
- **Mitigation:** Use 64-bit millisecond timestamps in v2.0

**6. No Flow Control**
- Server cannot signal client to slow down
- **Impact:** Server buffer overflow possible under high load
- **Mitigation:** Implement backpressure mechanism or rate limiting

**7. Single Server Architecture**
- No load balancing or failover
- Single point of failure
- **Impact:** Server downtime means data loss
- **Mitigation:** Implement server clustering or client-side buffering

**8. Limited Sensor Types**
- Only 3 predefined sensor types (temperature, humidity, voltage)
- No extensibility mechanism
- **Impact:** Cannot add new sensor types without protocol change
- **Mitigation:** Reserve sensor type range for custom types

### 8.2 Future Enhancements

**Phase 2 (Security):**
- Add DTLS support for encryption
- Implement HMAC-based authentication
- Add device registration/provisioning mechanism

**Phase 3 (Reliability):**
- Optional selective retransmission for critical readings
- Implement forward error correction (FEC)
- Add application-level acknowledgments for important events

**Phase 4 (Scalability):**
- Server clustering with load balancing
- Horizontal scaling support
- Multi-collector architecture

**Phase 5 (Features):**
- Compression support (e.g., delta encoding for time-series)
- Configurable QoS levels per device
- Support for actuator commands (bidirectional communication)
- Event-driven transmission (threshold-based alerts)

### 8.3 Known Issues

**Issue #1: Reorder Buffer Memory Usage**
- Large reorder windows consume memory
- No upper bound on total buffered data
- **Workaround:** Configure smaller reorder_window

**Issue #2: CSV Log File Growth**
- Unbounded log file size
- No log rotation mechanism
- **Workaround:** Manually rotate logs or use external log management

**Issue #3: Windows Network Impairment Testing**
- Automated tests require Linux
- Manual testing with Clumsy is tedious
- **Workaround:** Use Linux VM or WSL2 for testing

### 8.4 Performance Bottlenecks

**Identified Bottlenecks:**
1. CSV file I/O (synchronous writes)
2. Reorder buffer sorting (O(n log n) per packet)
3. Single-threaded server (no parallelism)

**Optimization Opportunities:**
1. Batch CSV writes (buffer multiple rows)
2. Use priority queue for reorder buffer
3. Multi-threaded server with worker pool
4. Binary log format instead of CSV

### 8.5 Comparison with Alternatives

| Feature | TinyTelemetry | MQTT | CoAP | HTTP/REST |
|---------|---------------|------|------|-----------|
| Transport | UDP | TCP | UDP | TCP |
| Overhead | 12 bytes | 2+ bytes | 4 bytes | 100+ bytes |
| Reliability | None | QoS 0-2 | CON/NON | TCP |
| Complexity | Low | Medium | Medium | High |
| Broker Required | No | Yes | No | No |
| Best For | Periodic telemetry | Pub/sub | Request/response | APIs |

**TinyTelemetry Advantages:**
- Simpler than MQTT (no broker)
- Lower overhead than CoAP (fixed header)
- Much lower overhead than HTTP
- Optimized for periodic push telemetry

**TinyTelemetry Disadvantages:**
- No reliability options (unlike MQTT QoS)
- No request/response pattern (unlike CoAP)
- No standardization (unlike MQTT/CoAP)

## 9. References

### 9.1 RFCs and Standards

1. **RFC 768** - User Datagram Protocol (UDP)
   - https://www.rfc-editor.org/rfc/rfc768.html
   - Foundation for TinyTelemetry transport layer

2. **RFC 7252** - The Constrained Application Protocol (CoAP)
   - https://www.rfc-editor.org/rfc/rfc7252.html
   - Inspiration for compact binary encoding

3. **RFC 8949** - Concise Binary Object Representation (CBOR)
   - https://www.rfc-editor.org/rfc/rfc8949.html
   - Alternative encoding scheme considered

4. **IEEE 754** - Floating-Point Arithmetic Standard
   - Used for sensor value encoding (float32)

### 9.2 Related Protocols

1. **MQTT (Message Queuing Telemetry Transport)**
   - https://mqtt.org/
   - Comparison protocol for telemetry use cases

2. **CoAP (Constrained Application Protocol)**
   - https://coap.technology/
   - Alternative for IoT communication

3. **LoRaWAN**
   - https://lora-alliance.org/
   - Long-range IoT protocol for comparison

### 9.3 Tools and Libraries

1. **Python struct module**
   - https://docs.python.org/3/library/struct.html
   - Binary encoding/decoding

2. **Linux tc (Traffic Control)**
   - https://man7.org/linux/man-pages/man8/tc.8.html
   - Network impairment simulation

3. **netem (Network Emulator)**
   - https://wiki.linuxfoundation.org/networking/netem
   - Packet loss, delay, jitter simulation

4. **Wireshark**
   - https://www.wireshark.org/
   - Packet capture and analysis

5. **Clumsy (Windows)**
   - https://jagt.github.io/clumsy/
   - Network condition simulation for Windows

### 9.4 Academic References

1. Bormann, C., Ersue, M., & Keranen, A. (2014). "Terminology for Constrained-Node Networks." RFC 7228.

2. Shelby, Z., Hartke, K., & Bormann, C. (2014). "The Constrained Application Protocol (CoAP)." RFC 7252.

3. Dunkels, A., Gronvall, B., & Voigt, T. (2004). "Contiki - a lightweight and flexible operating system for tiny networked sensors." IEEE LCN.

### 9.5 Implementation References

1. **Python Socket Programming**
   - https://docs.python.org/3/library/socket.html
   - UDP socket implementation

2. **Python argparse**
   - https://docs.python.org/3/library/argparse.html
   - Command-line interface

3. **Python csv module**
   - https://docs.python.org/3/library/csv.html
   - CSV logging implementation

4. **matplotlib**
   - https://matplotlib.org/
   - Visualization and plotting

---

**End of Specification**
