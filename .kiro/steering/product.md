---
inclusion: always
---

# Product Overview

TinyTelemetry v1.0 is a lightweight, UDP-based telemetry protocol designed for constrained IoT sensors. The system enables periodic transmission of small sensor readings (temperature, humidity, voltage) from distributed sensor clients to a central collector server.

## Core Characteristics

- **Loss-tolerant by design**: No retransmissions, optimized for telemetry use cases where occasional data loss is acceptable
- **Bandwidth efficient**: Compact 12-byte binary header, optional batching to reduce overhead
- **Stateful collection**: Server maintains per-device state for duplicate detection and gap analysis
- **Network resilience**: Designed to operate under packet loss (5%), delay (100ms), and jitter (±10ms)
- **Cross-platform**: Runs on both Linux and Windows

## Key Components

- **SensorClient**: Simulates IoT sensors, generates readings, encodes and transmits data packets
- **CollectorServer**: Receives packets, detects duplicates/gaps, reorders by timestamp, logs to CSV
- **Testing Framework**: Automated scripts with network impairment simulation for validation

## Use Case

Experimental validation of lightweight telemetry protocols for resource-constrained IoT deployments where simplicity and efficiency are prioritized over guaranteed delivery.
