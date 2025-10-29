# TinyTelemetry v1.0 - Project Proposal

**Course:** Network Protocols  
**Phase:** 1 - Prototype  
**Date:** October 2025  
**Assigned Scenario:** IoT Telemetry Protocol

---

## 1. Scenario and Motivation

### 1.1 Assigned Scenario

The TinyTelemetry project addresses the challenge of efficient data collection from resource-constrained IoT sensors in distributed deployments. The scenario involves multiple low-power sensors (temperature, humidity, voltage) periodically transmitting small telemetry readings to a central collector over unreliable networks.

### 1.2 Problem Statement

Traditional protocols like HTTP/REST or MQTT introduce significant overhead for simple telemetry use cases:

- **HTTP/REST**: Text-based encoding (JSON/XML) wastes bandwidth; TCP connection overhead is excessive for periodic small messages
- **MQTT**: Requires broker infrastructure; QoS mechanisms add complexity unnecessary for loss-tolerant telemetry
- **CoAP**: Better suited for request-response patterns rather than periodic push telemetry

For IoT sensors transmitting small readings every 1-30 seconds, these protocols result in 70-90% bandwidth overhead, drain battery life faster, and require complex state management.

### 1.3 Motivation

IoT deployments are growing rapidly, with billions of sensors expected in smart cities, industrial monitoring, and environmental sensing. A lightweight protocol optimized specifically for periodic telemetry can:

1. **Reduce bandwidth consumption** by 4-16x compared to JSON-based protocols
2. **Extend battery life** through minimal processing and transmission overhead
3. **Simplify implementation** on resource-constrained microcontrollers
4. **Tolerate packet loss** gracefully without complex retransmission logic
5. **Scale efficiently** to thousands of sensors per collector

The motivation is to demonstrate that a purpose-built protocol can significantly outperform general-purpose alternatives for this specific use case.

---

## 2. Proposed Protocol Approach

### 2.1 Core Design Principles

**Loss-Tolerant by Design**  
Unlike TCP-based protocols, TinyTelemetry embraces UDP's fire-and-forget model. For telemetry data where the next reading supersedes the previous one, occasional packet loss (up to 5%) is acceptable. This eliminates retransmission overhead and simplifies client implementation.

**Compact Binary Encoding**  
All messages use fixed-size binary fields with network byte order (big-endian). A 12-byte header carries essential metadata (version, message type, device ID, sequence number, timestamp), while sensor readings pack into 5 bytes each (1-byte type + 4-byte float32 value).

**Stateless Clients, Stateful Server**  
Clients maintain only a monotonic sequence counter and require no acknowledgment handling. The server maintains per-device state to detect duplicates, identify gaps, and reorder packets by timestamp. This asymmetric design keeps client complexity minimal while enabling robust collection.

**Optional Batching**  
Clients can batch multiple readings into a single packet (up to 37 readings per 200-byte packet). This reduces header overhead from 72% (non-batched) to 7% (maximum batch), allowing flexible trade-offs between latency and efficiency.

### 2.2 Protocol Architecture

```
┌─────────────────┐                    ┌──────────────────┐
│  Sensor Client  │                    │ Collector Server │
│                 │                    │                  │
│ • Generate      │                    │ • Receive UDP    │
│   readings      │                    │ • Parse packets  │
│ • Encode binary │   UDP Packets      │ • Detect dups    │
│ • Send UDP      │ ─────────────────> │ • Detect gaps    │
│ • No ACKs       │   (Fire & Forget)  │ • Reorder by TS  │
│                 │                    │ • Log to CSV     │
└─────────────────┘                    └──────────────────┘
```

**Key Components:**

1. **Sensor Client** (src/client.py)
   - Simulates IoT sensors generating temperature, humidity, and voltage readings
   - Encodes readings into binary DATA packets
   - Transmits via UDP at configurable intervals (1s, 5s, 30s)
   - Supports batching (1-37 readings per packet)

2. **Collector Server** (src/server.py)
   - Listens on UDP port (default 5000)
   - Maintains per-device state (last sequence, reorder buffer)
   - Detects duplicate packets using sequence numbers
   - Identifies gaps (missing sequences)
   - Reorders out-of-order packets by timestamp
   - Logs all received data to CSV

3. **Protocol Library** (src/protocol.py)
   - Binary encoding/decoding using Python struct module
   - Data structures (TelemetryPacket, SensorReading)
   - Constants (message types, sensor types, sizes)

### 2.3 Message Types

**DATA Message (0x01)**  
Carries one or more sensor readings. Used for normal telemetry transmission.

**HEARTBEAT Message (0x02)**  
Indicates device liveness when no new data is available. Contains header only (no payload).

### 2.4 Network Assumptions

- **Transport:** UDP/IP (port 5000 default)
- **Packet Loss:** Designed to operate under ≤5% random loss
- **Delay/Jitter:** Handles up to 100ms ±10ms variation
- **Reordering:** Timestamp-based reordering with configurable buffer
- **Duplicates:** Sequence-based detection and filtering

---

## 3. Protocol Message Format

### 3.1 Header Structure (12 bytes)

All packets begin with a fixed 12-byte header:

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
| Msg Type | 1 | 1 byte | uint8 | 0x01=DATA, 0x02=HEARTBEAT |
| Device ID | 2 | 2 bytes | uint16 | Unique sensor identifier (1-65535) |
| Sequence Number | 4 | 4 bytes | uint32 | Monotonic counter per device |
| Timestamp | 8 | 4 bytes | uint32 | Unix epoch time in seconds |

**Encoding:** Big-endian (network byte order)  
**Python struct format:** `!BBHII`

### 3.2 DATA Message Payload

DATA messages append a reading count byte followed by sensor readings:

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

**Python struct format:** `!Bf`

### 3.3 Sample Messages

**Example 1: DATA packet with 1 temperature reading**

```
Hex: 01 01 03 E9 00 00 00 00 65 4A 2B 18 01 41 C8 00 00

Breakdown:
01          - Version (1)
01          - Message Type (DATA)
03 E9       - Device ID (1001)
00 00 00 00 - Sequence Number (0)
65 4A 2B 18 - Timestamp (1698765592)
01          - Reading Count (1)
01          - Sensor Type (Temperature)
41 C8 00 00 - Value (25.0°C as float32)

Total size: 18 bytes
```

**Example 2: DATA packet with 3 readings (batched)**

```
Hex: 01 01 03 E9 00 00 00 01 65 4A 2B 19 03 01 41 C8 00 00 02 42 48 00 00 03 40 A0 00 00

Breakdown:
01          - Version (1)
01          - Message Type (DATA)
03 E9       - Device ID (1001)
00 00 00 01 - Sequence Number (1)
65 4A 2B 19 - Timestamp (1698765593)
03          - Reading Count (3)
01 41 C8 00 00 - Temperature: 25.0°C
02 42 48 00 00 - Humidity: 50.0%
03 40 A0 00 00 - Voltage: 5.0V

Total size: 28 bytes
```

**Example 3: HEARTBEAT packet**

```
Hex: 01 02 03 E9 00 00 00 02 65 4A 2B 1A

Breakdown:
01          - Version (1)
02          - Message Type (HEARTBEAT)
03 E9       - Device ID (1001)
00 00 00 02 - Sequence Number (2)
65 4A 2B 1A - Timestamp (1698765594)

Total size: 12 bytes (header only)
```

---

## 4. Implementation Plan

### 4.1 Phase 1 Deliverables (Current)

- ✅ Working UDP client and server
- ✅ Binary protocol encoding/decoding
- ✅ DATA and HEARTBEAT message support
- ✅ Sequence-based duplicate detection
- ✅ Gap detection (missing packets)
- ✅ Timestamp-based reordering
- ✅ CSV logging with metadata
- ✅ Automated baseline test script
- ✅ Mini-RFC (sections 1-3)
- ✅ README with usage instructions

### 4.2 Phase 2 Goals (Future)

- Network impairment testing (packet loss, delay, jitter)
- Performance metrics calculation (delivery rate, duplicate rate, gaps)
- Statistical analysis across multiple test runs
- Visualization (plots of bandwidth efficiency, loss tolerance)
- Cross-platform validation (Linux and Windows)
- Comprehensive test suite with automated reporting

### 4.3 Success Criteria

**Functional Requirements:**
- Client successfully sends DATA packets with sensor readings
- Server receives, parses, and logs packets correctly
- Duplicate detection works (same sequence number)
- Gap detection works (missing sequence numbers)
- Reordering works (out-of-order packets sorted by timestamp)

**Performance Requirements:**
- ≥99% packet delivery under ideal conditions (baseline test)
- Bandwidth overhead ≤20% with batching (batch_size=10)
- Server handles multiple concurrent clients
- No crashes or data corruption under normal operation

**Testing Requirements:**
- Baseline test runs successfully and generates logs
- CSV output contains all required fields
- Metrics can be calculated from logs
- Code runs on both Linux and Windows

---

## 5. Expected Outcomes

### 5.1 Technical Outcomes

1. **Functional prototype** demonstrating lightweight telemetry protocol over UDP
2. **Quantitative analysis** of bandwidth efficiency vs. JSON-based alternatives
3. **Performance characterization** under various network conditions
4. **Validation** of loss-tolerant design approach for telemetry use cases

### 5.2 Learning Outcomes

1. Understanding UDP socket programming and datagram handling
2. Experience with binary protocol design and encoding
3. Knowledge of network impairment effects (loss, delay, jitter)
4. Skills in protocol testing and performance measurement
5. Insight into trade-offs between reliability and efficiency

### 5.3 Deliverables Summary

- **Code:** Python implementation (client, server, protocol library)
- **Documentation:** Mini-RFC, README, project proposal
- **Tests:** Automated baseline test script with logging
- **Demo:** 5-minute video demonstrating core functionality
- **Data:** CSV logs and metrics from test runs

---

## 6. Conclusion

TinyTelemetry v1.0 demonstrates that a purpose-built protocol can significantly outperform general-purpose alternatives for IoT telemetry. By embracing UDP's simplicity, using compact binary encoding, and designing for loss tolerance, the protocol achieves 4-16x bandwidth reduction compared to JSON-based approaches while maintaining simplicity suitable for resource-constrained devices.

The Phase 1 prototype successfully implements core functionality (DATA/HEARTBEAT messages, duplicate detection, gap detection, reordering) and provides a foundation for comprehensive testing and validation in subsequent phases.

---

**End of Proposal**
