# Requirements Document

## Introduction

This document specifies the requirements for a custom lightweight telemetry protocol designed for constrained IoT sensors. The protocol enables periodic transmission of small sensor readings (temperature, humidity, voltage) to a central collector over UDP. The system must be cross-platform (Linux/Windows), loss-tolerant, and experimentally validated under various network conditions using network impairment simulation.

## Glossary

- **TelemetrySystem**: The complete IoT telemetry system including sensor clients and collector server
- **SensorClient**: The client application that simulates IoT sensors and sends telemetry data
- **CollectorServer**: The server application that receives, processes, and logs telemetry data
- **DataPacket**: A UDP packet containing one or more sensor readings with protocol header
- **HeartbeatPacket**: A UDP packet indicating device liveness when no new data is available
- **SequenceNumber**: A monotonically increasing counter per device to detect loss and duplicates
- **BatchingMode**: Optional mode where multiple sensor readings are grouped into a single packet
- **NetworkImpairment**: Simulated network conditions (loss, delay, jitter) using Linux netem or Windows Clumsy

## Requirements

### Requirement 1: UDP Transport Layer

**User Story:** As a system architect, I want the protocol to use UDP as the primary transport, so that the system remains lightweight and suitable for constrained IoT devices.

#### Acceptance Criteria

1. THE TelemetrySystem SHALL use UDP sockets for all telemetry data transmission
2. THE TelemetrySystem SHALL use UDP port numbers configurable via command-line arguments or configuration files
3. WHERE administrative control channels are implemented, THE TelemetrySystem SHALL document the justification for any TCP usage in the Mini-RFC

### Requirement 2: Message Type Support

**User Story:** As a protocol designer, I want to support distinct message types for data and heartbeats, so that the collector can differentiate between actual readings and liveness indicators.

#### Acceptance Criteria

1. THE SensorClient SHALL support a DATA message type that carries one or more sensor readings
2. THE SensorClient SHALL support a HEARTBEAT message type sent periodically when no new data is available
3. THE TelemetrySystem SHALL encode the message type in the protocol header using at least 1 bit or 1 byte
4. THE CollectorServer SHALL process DATA and HEARTBEAT messages according to their respective types

### Requirement 3: Compact Binary Header

**User Story:** As a protocol designer, I want a compact binary header format, so that bandwidth usage is minimized for constrained IoT devices.

#### Acceptance Criteria

1. THE TelemetrySystem SHALL implement a binary protocol header with maximum size of 12 bytes
2. THE TelemetrySystem SHALL include a Device ID field in every message header
3. THE TelemetrySystem SHALL include a Sequence Number field in every message header
4. THE TelemetrySystem SHALL include a Timestamp field in every message header
5. THE TelemetrySystem SHALL include a Message Type field in every message header
6. THE TelemetrySystem SHALL document the complete header layout with field sizes and byte offsets in the Mini-RFC

### Requirement 4: Loss Tolerance

**User Story:** As a system designer, I want the protocol to be loss-tolerant without per-packet retransmission, so that the system remains simple and efficient for telemetry use cases.

#### Acceptance Criteria

1. THE TelemetrySystem SHALL NOT implement per-packet retransmission mechanisms
2. THE TelemetrySystem SHALL tolerate at least 5 percent packet loss without application failure
3. THE CollectorServer SHALL continue processing subsequent packets after detecting packet loss

### Requirement 5: Optional Batching Mode

**User Story:** As a protocol designer, I want to support optional batching of multiple readings into a single packet, so that bandwidth efficiency can be improved when appropriate.

#### Acceptance Criteria

1. WHERE batching mode is enabled, THE SensorClient SHALL group up to N sensor readings into a single DataPacket
2. THE TelemetrySystem SHALL define the maximum batch size N and document the justification in the Mini-RFC
3. THE CollectorServer SHALL correctly parse and extract individual readings from batched DataPackets
4. THE TelemetrySystem SHALL support both batched and non-batched operation modes

### Requirement 6: Payload Size Constraint

**User Story:** As a protocol implementer, I want to enforce a maximum payload size, so that packets remain suitable for constrained networks.

#### Acceptance Criteria

1. THE TelemetrySystem SHALL limit the UDP application payload to a maximum of 200 bytes
2. WHEN a batched message would exceed 200 bytes, THE SensorClient SHALL split the readings across multiple packets
3. THE TelemetrySystem SHALL document the payload size calculation including header and data in the Mini-RFC

### Requirement 7: Configurable Reporting Intervals

**User Story:** As a test engineer, I want configurable reporting intervals, so that I can evaluate protocol performance under different traffic patterns.

#### Acceptance Criteria

1. THE SensorClient SHALL support reporting intervals of 1 second, 5 seconds, and 30 seconds
2. THE SensorClient SHALL accept the reporting interval as a command-line argument or configuration parameter
3. WHEN the reporting interval is configured, THE SensorClient SHALL send DATA or HEARTBEAT messages at the specified periodicity

### Requirement 8: Per-Device State Management

**User Story:** As a collector operator, I want the server to maintain per-device state, so that packet loss and duplicates can be detected for each sensor independently.

#### Acceptance Criteria

1. THE CollectorServer SHALL maintain state for each unique Device ID including last sequence number and timestamps
2. THE CollectorServer SHALL initialize device state upon receiving the first packet from a new Device ID
3. THE CollectorServer SHALL update device state upon successfully processing each packet

### Requirement 9: Duplicate Suppression

**User Story:** As a collector operator, I want duplicate packets to be detected and suppressed, so that sensor readings are not double-counted.

#### Acceptance Criteria

1. WHEN a packet with a previously seen sequence number for a device is received, THE CollectorServer SHALL mark it as a duplicate
2. THE CollectorServer SHALL NOT process duplicate packets for data aggregation or analysis
3. THE CollectorServer SHALL log duplicate packets with a duplicate_flag set to true
4. WHEN operating under 5 percent loss conditions, THE CollectorServer SHALL maintain a duplicate rate of 1 percent or less

### Requirement 10: Sequence Gap Detection

**User Story:** As a system operator, I want the collector to detect and report sequence gaps, so that packet loss can be monitored and analyzed.

#### Acceptance Criteria

1. WHEN a received sequence number is greater than the expected next sequence number, THE CollectorServer SHALL detect a sequence gap
2. THE CollectorServer SHALL calculate the number of missing packets based on the sequence gap size
3. THE CollectorServer SHALL log sequence gaps with a gap_flag set to true and record the gap count
4. THE CollectorServer SHALL continue processing subsequent packets after detecting a gap

### Requirement 11: Timestamp-Based Reordering

**User Story:** As a data analyst, I want delayed packets to be reordered by timestamp, so that analysis reflects the actual temporal order of sensor readings.

#### Acceptance Criteria

1. WHEN packets arrive out of order, THE CollectorServer SHALL reorder them by timestamp for analysis purposes
2. THE CollectorServer SHALL maintain a reordering buffer to handle delayed packets
3. WHILE operating under delay and jitter conditions (100ms ±10ms), THE CollectorServer SHALL correctly reorder packets without buffer overrun or crash

### Requirement 12: Comprehensive Logging

**User Story:** As a test engineer, I want all received data logged to CSV with detailed metadata, so that protocol performance can be analyzed offline.

#### Acceptance Criteria

1. THE CollectorServer SHALL log all received packets to a CSV file
2. THE CollectorServer SHALL include the following fields in each CSV log entry: device_id, seq, timestamp, arrival_time, duplicate_flag, gap_flag
3. THE CollectorServer SHALL flush log entries to disk periodically to prevent data loss
4. THE CollectorServer SHALL include timestamps with millisecond or microsecond precision

### Requirement 13: Cross-Platform Compatibility

**User Story:** As a developer, I want the code to run on both Linux and Windows with minimal changes, so that the system is accessible to all team members and graders.

#### Acceptance Criteria

1. THE TelemetrySystem SHALL be implemented in Python 3 or another cross-platform language
2. THE TelemetrySystem SHALL run on Linux without modification
3. THE TelemetrySystem SHALL run on Windows without modification
4. THE TelemetrySystem SHALL use platform-independent socket APIs and file I/O operations

### Requirement 14: Reproducible Experiments

**User Story:** As a researcher, I want experiments to be reproducible with deterministic results, so that performance claims can be verified.

#### Acceptance Criteria

1. THE TelemetrySystem SHALL provide automated scripts to run all test scenarios
2. WHERE randomization is used, THE TelemetrySystem SHALL accept a deterministic seed as a parameter
3. THE TelemetrySystem SHALL log all sent and received packets with timestamps and relevant metadata
4. THE TelemetrySystem SHALL generate pcap traces for at least two runs per test scenario

### Requirement 15: Baseline Test Scenario

**User Story:** As a test engineer, I want to validate the protocol under ideal network conditions, so that baseline performance can be established.

#### Acceptance Criteria

1. WHEN running the baseline test with no network impairment for 60 seconds at 1-second intervals, THE CollectorServer SHALL receive at least 99 percent of transmitted packets
2. WHEN running the baseline test, THE CollectorServer SHALL verify that sequence numbers are in order
3. THE TelemetrySystem SHALL provide an automated script to execute the baseline test scenario

### Requirement 16: Packet Loss Test Scenario

**User Story:** As a test engineer, I want to validate the protocol under 5% packet loss, so that loss tolerance can be verified.

#### Acceptance Criteria

1. WHEN running the loss test with 5 percent random packet loss using netem, THE CollectorServer SHALL detect sequence gaps
2. WHEN running the loss test, THE CollectorServer SHALL correctly suppress duplicate packets
3. WHEN running the loss test, THE CollectorServer SHALL maintain a duplicate rate of 1 percent or less
4. THE TelemetrySystem SHALL provide an automated script to execute the loss test scenario using netem

### Requirement 17: Delay and Jitter Test Scenario

**User Story:** As a test engineer, I want to validate the protocol under delay and jitter conditions, so that reordering logic can be verified.

#### Acceptance Criteria

1. WHEN running the delay test with 100ms ±10ms jitter using netem, THE CollectorServer SHALL correctly reorder packets by timestamp
2. WHEN running the delay test, THE CollectorServer SHALL NOT experience buffer overrun
3. WHEN running the delay test, THE CollectorServer SHALL NOT crash or terminate unexpectedly
4. THE TelemetrySystem SHALL provide an automated script to execute the delay test scenario using netem

### Requirement 18: Performance Metrics Collection

**User Story:** As a performance analyst, I want comprehensive metrics collected for each test run, so that protocol efficiency can be quantified.

#### Acceptance Criteria

1. THE TelemetrySystem SHALL calculate and report the average bytes_per_report metric (total bytes including payload and header per reading)
2. THE TelemetrySystem SHALL calculate and report the packets_received count
3. THE TelemetrySystem SHALL calculate and report the duplicate_rate as a fraction of duplicate messages detected
4. THE TelemetrySystem SHALL calculate and report the sequence_gap_count as the number of missing sequences detected
5. THE TelemetrySystem SHALL calculate and report the cpu_ms_per_report metric (CPU time per reading processed)

### Requirement 19: Statistical Rigor

**User Story:** As a researcher, I want multiple measurement repetitions with statistical reporting, so that result variance can be understood.

#### Acceptance Criteria

1. THE TelemetrySystem SHALL repeat each measurement at least 5 times
2. THE TelemetrySystem SHALL report the median value for each metric
3. THE TelemetrySystem SHALL report the minimum and maximum values for each metric
4. THE TelemetrySystem SHALL include an explanation of observed variance in the results documentation

### Requirement 20: Deliverable Completeness

**User Story:** As a project stakeholder, I want all required deliverables produced, so that the project can be evaluated comprehensively.

#### Acceptance Criteria

1. THE TelemetrySystem SHALL include a Mini-RFC document (maximum 3 pages) with protocol specification
2. THE TelemetrySystem SHALL include working SensorClient and CollectorServer implementations
3. THE TelemetrySystem SHALL include automated testing scripts that produce pcap and CSV outputs
4. THE TelemetrySystem SHALL include results and plots showing bytes_per_report vs reporting_interval and duplicate_rate vs loss
5. THE TelemetrySystem SHALL include a README with build instructions, usage examples, and design rationale
