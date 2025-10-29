# IoT Telemetry Protocol - Design Document

## Overview

The IoT Telemetry Protocol (ITP) is a lightweight, UDP-based application-layer protocol designed for constrained IoT sensors to transmit periodic telemetry data to a central collector. The protocol prioritizes simplicity, bandwidth efficiency, and loss tolerance over reliability guarantees.

**Key Design Principles:**
- Loss-tolerant by design (no retransmissions)
- Compact binary encoding (≤12 byte header)
- Stateful server for duplicate detection and gap analysis
- Optional batching for bandwidth optimization
- Cross-platform Python 3 implementation

**Protocol Name:** TinyTelemetry v1.0

## Architecture

### System Components

```
┌─────────────────┐                    ┌─────────────────┐
│  Sensor Client  │                    │ Collector Server│
│                 │                    │                 │
│  - Generate     │    UDP Packets     │  - Receive      │
│    readings     │ ─────────────────> │    packets      │
│  - Batch (opt)  │                    │  - Deduplicate  │
│  - Encode       │                    │  - Detect gaps  │
│  - Send         │                    │  - Reorder      │
│                 │                    │  - Log to CSV   │
└─────────────────┘                    └─────────────────┘
```

### Communication Model

1. **Unidirectional Flow:** Sensors send data to collector; no acknowledgments
2. **Stateless Client:** Each packet is independent; client maintains only sequence counter
3. **Stateful Server:** Maintains per-device state for duplicate detection and gap analysis
4. **Fire-and-Forget:** No retransmission or reliability mechanisms

### Network Layer

- **Transport:** UDP/IP
- **Default Ports:** 
  - Server listening port: 5000 (configurable)
  - Client ephemeral ports: OS-assigned
- **Packet Size:** Maximum 200 bytes application payload (header + data)

## Components and Interfaces

### 1. Protocol Header Format

**Header Size:** 12 bytes (fixed)

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

| Field | Size | Type | Description |
|-------|------|------|-------------|
| Version | 1 byte | uint8 | Protocol version (0x01 for v1.0) |
| Msg Type | 1 byte | uint8 | 0x01=DATA, 0x02=HEARTBEAT |
| Device ID | 2 bytes | uint16 | Unique sensor identifier (1-65535) |
| Sequence Number | 4 bytes | uint32 | Monotonic counter per device |
| Timestamp | 4 bytes | uint32 | Unix epoch seconds |

**Encoding:** Big-endian (network byte order) for all multi-byte fields

**Design Rationale:**
- 12 bytes total keeps overhead minimal (6% for 200-byte packets)
- 32-bit sequence number supports 4.2 billion packets before wraparound
- 32-bit timestamp (seconds) is sufficient for telemetry use cases
- 16-bit device ID supports up to 65,535 sensors

### 2. Message Types

#### DATA Message

**Structure:**
```
[Header: 12 bytes][Payload: variable]
```

**Payload Format (per reading):**
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Sensor Type  |                  Value (float)                |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| Field | Size | Type | Description |
|-------|------|------|-------------|
| Sensor Type | 1 byte | uint8 | 0x01=Temperature, 0x02=Humidity, 0x03=Voltage |
| Value | 4 bytes | float32 | Sensor reading value |

**Total per reading:** 5 bytes

**Batching:**
- Maximum batch size: N = 37 readings per packet
- Calculation: (200 - 12) / 5 = 37.6 → 37 readings
- First byte after header indicates reading count (1 byte)
- Actual max batch: (200 - 12 - 1) / 5 = 37 readings

**Batched DATA Payload:**
```
[Header: 12 bytes][Count: 1 byte][Reading 1: 5 bytes]...[Reading N: 5 bytes]
```

#### HEARTBEAT Message

**Structure:**
```
[Header: 12 bytes][No payload]
```

**Purpose:** Indicate device liveness when no new sensor data is available

**Timing:** Sent at configured reporting interval when no DATA is sent

### 3. Sensor Client (SensorClient)

**Responsibilities:**
- Generate simulated sensor readings (temperature, humidity, voltage)
- Maintain per-device sequence counter
- Encode messages according to protocol specification
- Send DATA or HEARTBEAT at configured intervals
- Support batching mode (optional)

**Configuration Parameters:**
- `device_id`: Unique sensor identifier
- `server_host`: Collector IP address
- `server_port`: Collector UDP port
- `interval`: Reporting interval (1s, 5s, or 30s)
- `duration`: Test duration in seconds
- `batch_size`: Number of readings per packet (1-37, default=1)
- `sensor_types`: List of sensor types to simulate

**State:**
- `sequence_number`: uint32, initialized to 0, incremented per packet
- `reading_buffer`: List of pending readings (for batching)

**Main Loop:**
```python
while not expired:
    if should_send_data():
        readings = generate_readings(sensor_types)
        if batch_mode:
            buffer.append(readings)
            if len(buffer) >= batch_size or timeout:
                send_data_packet(buffer)
                buffer.clear()
        else:
            send_data_packet(readings)
    else:
        send_heartbeat_packet()
    
    sleep(interval)
```

### 4. Collector Server (CollectorServer)

**Responsibilities:**
- Receive UDP packets on configured port
- Parse and validate protocol headers
- Maintain per-device state
- Detect and suppress duplicates
- Detect sequence gaps
- Reorder packets by timestamp
- Log all packets to CSV
- Calculate and report metrics

**Per-Device State:**
```python
{
    'device_id': int,
    'last_seq': int,           # Last processed sequence number
    'last_timestamp': int,     # Last packet timestamp
    'total_packets': int,      # Total packets received
    'duplicate_count': int,    # Duplicate packets detected
    'gap_count': int,          # Total missing packets
    'seen_sequences': set,     # Set of received sequence numbers (for dup detection)
    'reorder_buffer': []       # List of (seq, timestamp, data) tuples
}
```

**Packet Processing Pipeline:**
```
Receive UDP → Parse Header → Validate → Check Duplicate → 
Detect Gap → Update State → Buffer for Reorder → Log to CSV
```

**Duplicate Detection Algorithm:**
```python
if seq_num in device_state['seen_sequences']:
    mark_as_duplicate()
    log_and_discard()
else:
    device_state['seen_sequences'].add(seq_num)
    process_packet()
```

**Gap Detection Algorithm:**
```python
expected_seq = device_state['last_seq'] + 1
if seq_num > expected_seq:
    gap_size = seq_num - expected_seq
    device_state['gap_count'] += gap_size
    log_gap(gap_size)
device_state['last_seq'] = seq_num
```

**Reordering Strategy:**
- Maintain a sliding window buffer (size: 10 packets)
- Buffer packets for up to 2 seconds
- Flush buffer periodically, sorted by timestamp
- Trade-off: Small buffer limits reordering capability but reduces memory usage

**Configuration Parameters:**
- `listen_port`: UDP port to bind (default: 5000)
- `log_file`: CSV output file path
- `reorder_window`: Buffer size for reordering (default: 10)
- `reorder_timeout`: Max time to buffer packets (default: 2s)

## Data Models

### Packet Structure (In-Memory)

```python
@dataclass
class TelemetryPacket:
    version: int
    msg_type: int  # 1=DATA, 2=HEARTBEAT
    device_id: int
    sequence_number: int
    timestamp: int
    readings: List[SensorReading]  # Empty for HEARTBEAT
    
@dataclass
class SensorReading:
    sensor_type: int  # 1=Temperature, 2=Humidity, 3=Voltage
    value: float
```

### CSV Log Format

**File:** `telemetry_log.csv`

**Columns:**
```
device_id,seq,timestamp,arrival_time,msg_type,duplicate_flag,gap_flag,gap_size,reading_count
```

**Example:**
```csv
device_id,seq,timestamp,arrival_time,msg_type,duplicate_flag,gap_flag,gap_size,reading_count
1001,0,1698765432,1698765432.123,DATA,False,False,0,1
1001,1,1698765433,1698765433.125,DATA,False,False,0,1
1001,3,1698765435,1698765435.128,DATA,False,True,1,1
```

### Metrics Output Format

**File:** `metrics.json`

```json
{
    "test_scenario": "baseline",
    "duration_seconds": 60,
    "reporting_interval": 1,
    "batch_size": 1,
    "metrics": {
        "bytes_per_report": 17.0,
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

## Error Handling

### Client Error Scenarios

| Error | Handling Strategy |
|-------|-------------------|
| Socket creation failure | Log error, exit with code 1 |
| Invalid configuration | Validate on startup, exit with code 2 |
| Send failure (network unreachable) | Log warning, continue (loss-tolerant) |
| Sequence number overflow | Wrap around to 0 (acceptable for telemetry) |

### Server Error Scenarios

| Error | Handling Strategy |
|-------|-------------------|
| Socket bind failure | Log error, exit with code 1 |
| Malformed packet | Log warning, discard packet, continue |
| Invalid header version | Log warning, discard packet, continue |
| CSV write failure | Log error, buffer in memory, retry |
| Buffer overflow (reordering) | Flush oldest packets, log warning |

### Validation Rules

**Header Validation:**
- Version must be 0x01
- Message type must be 0x01 or 0x02
- Device ID must be > 0
- Packet size must be ≤ 200 bytes

**Payload Validation:**
- DATA messages must have at least 1 reading
- Reading count must match payload size
- Sensor type must be 0x01, 0x02, or 0x03

## Testing Strategy

### Unit Tests

**Client Tests:**
- `test_header_encoding()`: Verify correct binary encoding
- `test_sequence_increment()`: Verify sequence counter increments
- `test_batching()`: Verify correct batching of multiple readings
- `test_payload_size_limit()`: Verify 200-byte limit enforcement

**Server Tests:**
- `test_header_parsing()`: Verify correct binary decoding
- `test_duplicate_detection()`: Verify duplicates are detected
- `test_gap_detection()`: Verify gaps are detected correctly
- `test_reordering()`: Verify timestamp-based reordering
- `test_csv_logging()`: Verify correct CSV output format

### Integration Tests

**Test Scenarios (Automated Scripts):**

1. **Baseline Test** (`test_baseline.sh` / `test_baseline.py`)
   - No network impairment
   - 60-second duration, 1-second interval
   - Verify ≥99% packet delivery
   - Verify sequence order

2. **Loss Test** (`test_loss.sh` / `test_loss.py`)
   - 5% random packet loss (netem)
   - 60-second duration, 1-second interval
   - Verify gap detection
   - Verify duplicate rate ≤1%

3. **Delay/Jitter Test** (`test_delay.sh` / `test_delay.py`)
   - 100ms ±10ms delay (netem)
   - 60-second duration, 1-second interval
   - Verify reordering works
   - Verify no crashes

**Test Execution:**
```bash
# Linux (using netem)
./scripts/run_all_tests.sh

# Windows (manual, using Clumsy for development)
python scripts/run_baseline_test.py
```

### Performance Tests

**Metrics Collection:**
- Run each test 5 times
- Calculate median, min, max for each metric
- Generate plots:
  - `bytes_per_report` vs `reporting_interval`
  - `duplicate_rate` vs `loss_percentage`

**Profiling:**
- Use `cProfile` for CPU profiling
- Use `psutil` for memory monitoring
- Measure per-packet processing time

### Packet Capture

**Requirements:**
- Capture at least 2 pcap files per test scenario
- Use `tcpdump` (Linux) or Wireshark (Windows)
- Filter: `udp port 5000`

**Example:**
```bash
tcpdump -i lo -w baseline_run1.pcap udp port 5000
```

## Implementation Notes

### Cross-Platform Considerations

**Socket Programming:**
- Use Python's `socket` module (cross-platform)
- Bind to `0.0.0.0` for server (works on both OS)
- Use `socket.SO_REUSEADDR` for quick restart

**File Paths:**
- Use `pathlib.Path` for cross-platform path handling
- Use forward slashes in config files

**Process Management:**
- Use `subprocess` module for running tests
- Handle Ctrl+C gracefully with signal handlers

**Network Impairment:**
- Linux: Use `tc qdisc` with `netem`
- Windows: Document Clumsy usage for development only
- Grading will be done on Linux

### Batching Design Decision

**Chosen Batch Size:** N = 10 (configurable, max 37)

**Rationale:**
- Balance between bandwidth efficiency and latency
- 10 readings = 12 + 1 + 50 = 63 bytes (31.5% overhead)
- 1 reading = 12 + 1 + 5 = 18 bytes (72% overhead)
- Allows 6x reduction in packet rate for same data volume
- Still well under 200-byte limit (63 bytes)
- Reduces collision probability in high-density deployments

**Trade-offs:**
- Larger batches: Better efficiency, higher latency
- Smaller batches: Lower latency, more overhead
- Default to batch_size=1 for simplicity, allow configuration

### Field Packing Strategy

**Binary Encoding:**
- Use Python `struct` module
- Format string: `!BBHII` for header (network byte order)
- Format string: `!Bf` for each reading

**Advantages:**
- Compact representation (no text overhead)
- Fast encoding/decoding
- Deterministic size calculation

**Example:**
```python
import struct

# Encode header
header = struct.pack('!BBHII', version, msg_type, device_id, seq_num, timestamp)

# Encode reading
reading = struct.pack('!Bf', sensor_type, value)
```

## Security Considerations

**Out of Scope for Phase 1:**
- Authentication
- Encryption
- Integrity checks (checksums)

**Future Enhancements:**
- Add HMAC for message authentication
- Add optional CRC16 checksum field
- Consider DTLS for encrypted transport

## Performance Targets

| Metric | Target |
|--------|--------|
| Packet processing latency | < 1ms per packet |
| CPU usage (server) | < 5% on modern CPU |
| Memory usage (server) | < 50MB for 100 devices |
| Throughput | 1000 packets/second |

## Appendix: Protocol State Machine

### Client State Machine

```
┌─────────┐
│  INIT   │
└────┬────┘
     │
     ▼
┌─────────────┐     Timer      ┌──────────────┐
│   IDLE      │ ─────────────> │  GENERATING  │
└─────────────┘                └──────┬───────┘
     ▲                                │
     │                                ▼
     │                         ┌─────────────┐
     │                         │  ENCODING   │
     │                         └──────┬──────┘
     │                                │
     │                                ▼
     │                         ┌─────────────┐
     └─────────────────────────│   SENDING   │
                               └─────────────┘
```

### Server State Machine (Per Packet)

```
┌──────────┐
│ RECEIVE  │
└────┬─────┘
     │
     ▼
┌──────────┐     Invalid     ┌──────────┐
│  PARSE   │ ──────────────> │ DISCARD  │
└────┬─────┘                 └──────────┘
     │ Valid
     ▼
┌──────────┐     Duplicate   ┌──────────┐
│  CHECK   │ ──────────────> │   LOG    │
└────┬─────┘                 └──────────┘
     │ New
     ▼
┌──────────┐
│  BUFFER  │
└────┬─────┘
     │
     ▼
┌──────────┐
│   LOG    │
└──────────┘
```
