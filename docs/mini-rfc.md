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

---

**End of Specification**
