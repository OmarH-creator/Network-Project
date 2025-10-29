"""
TinyTelemetry v1.0 Protocol Definition

This module defines the core protocol constants, data structures, and encoding/decoding
functions for the IoT telemetry protocol.
"""

from dataclasses import dataclass
from typing import List
import struct

# Protocol Constants
VERSION = 0x01  # Protocol version 1.0

# Message Types
MSG_TYPE_DATA = 0x01
MSG_TYPE_HEARTBEAT = 0x02

# Sensor Types
SENSOR_TYPE_TEMPERATURE = 0x01
SENSOR_TYPE_HUMIDITY = 0x02
SENSOR_TYPE_VOLTAGE = 0x03

# Protocol Sizes
HEADER_SIZE = 12  # bytes
MAX_PAYLOAD_SIZE = 200  # bytes (total packet including header)
READING_SIZE = 5  # bytes (1 byte sensor type + 4 bytes float value)

# Maximum batch size calculation: (MAX_PAYLOAD - HEADER - 1 byte count) / READING_SIZE
MAX_BATCH_SIZE = (MAX_PAYLOAD_SIZE - HEADER_SIZE - 1) // READING_SIZE  # 37 readings


@dataclass
class SensorReading:
    """Represents a single sensor reading."""
    sensor_type: int  # SENSOR_TYPE_* constant
    value: float  # Sensor reading value


@dataclass
class TelemetryPacket:
    """Represents a complete telemetry packet."""
    version: int
    msg_type: int  # MSG_TYPE_* constant
    device_id: int
    sequence_number: int
    timestamp: int  # Unix epoch seconds
    readings: List[SensorReading]  # Empty for HEARTBEAT messages


def encode_header(version: int, msg_type: int, device_id: int, 
                  sequence_number: int, timestamp: int) -> bytes:
    """
    Encode protocol header to binary format using network byte order.
    
    The header uses compact binary encoding to minimize bandwidth overhead.
    All multi-byte fields are encoded in big-endian (network byte order) for
    cross-platform compatibility.
    
    Struct format string: '!BBHII'
    - '!' = Network byte order (big-endian)
    - 'B' = Unsigned char (1 byte) - version
    - 'B' = Unsigned char (1 byte) - msg_type
    - 'H' = Unsigned short (2 bytes) - device_id
    - 'I' = Unsigned int (4 bytes) - sequence_number
    - 'I' = Unsigned int (4 bytes) - timestamp
    
    Total size: 1 + 1 + 2 + 4 + 4 = 12 bytes
    
    Args:
        version: Protocol version (0x01 for v1.0)
        msg_type: Message type (0x01=DATA, 0x02=HEARTBEAT)
        device_id: Unique device identifier (1-65535)
        sequence_number: Monotonic counter (0-4294967295)
        timestamp: Unix epoch time in seconds
    
    Returns:
        12-byte binary header
    """
    return struct.pack('!BBHII', version, msg_type, device_id, 
                      sequence_number, timestamp)


def decode_header(data: bytes) -> dict:
    """
    Decode protocol header from binary format.
    
    Args:
        data: Binary data (minimum 12 bytes)
        
    Returns:
        Dictionary with header fields
        
    Raises:
        struct.error: If data is too short or malformed
    """
    if len(data) < HEADER_SIZE:
        raise ValueError(f"Packet too short: {len(data)} bytes, expected at least {HEADER_SIZE}")
    
    version, msg_type, device_id, sequence_number, timestamp = struct.unpack(
        '!BBHII', data[:HEADER_SIZE]
    )
    
    return {
        'version': version,
        'msg_type': msg_type,
        'device_id': device_id,
        'sequence_number': sequence_number,
        'timestamp': timestamp
    }


def encode_data_payload(readings: List[SensorReading]) -> bytes:
    """
    Encode DATA message payload with sensor readings.
    
    Payload structure:
    - Byte 0: Reading count (1-37)
    - Bytes 1-5: First reading (1 byte type + 4 bytes float)
    - Bytes 6-10: Second reading (if present)
    - ... (up to 37 readings)
    
    Each reading is encoded as:
    - 1 byte: sensor_type (0x01=Temperature, 0x02=Humidity, 0x03=Voltage)
    - 4 bytes: value (IEEE 754 single-precision float, big-endian)
    
    Maximum batch size calculation:
    - Max payload: 200 bytes
    - Header: 12 bytes
    - Count: 1 byte
    - Available for readings: 200 - 12 - 1 = 187 bytes
    - Max readings: 187 / 5 = 37 readings
    
    Args:
        readings: List of SensorReading objects (1-37 readings)
        
    Returns:
        Encoded payload bytes (1 + N*5 bytes)
        
    Raises:
        ValueError: If readings list is empty, too large, or would exceed MAX_PAYLOAD_SIZE
    """
    if not readings:
        raise ValueError("DATA message must contain at least one reading")
    
    if len(readings) > MAX_BATCH_SIZE:
        raise ValueError(f"Too many readings: {len(readings)}, max is {MAX_BATCH_SIZE}")
    
    # Calculate total packet size to ensure we don't exceed limit
    payload_size = 1 + (len(readings) * READING_SIZE)
    total_size = HEADER_SIZE + payload_size
    
    if total_size > MAX_PAYLOAD_SIZE:
        raise ValueError(f"Packet too large: {total_size} bytes, max is {MAX_PAYLOAD_SIZE}")
    
    # Encode reading count (1 byte)
    payload = struct.pack('!B', len(readings))
    
    # Encode each reading (5 bytes each)
    # Format: '!Bf' = big-endian unsigned byte + float
    for reading in readings:
        payload += struct.pack('!Bf', reading.sensor_type, reading.value)
    
    return payload


def decode_data_payload(data: bytes) -> List[SensorReading]:
    """
    Decode DATA message payload.
    
    Args:
        data: Payload bytes (after header)
        
    Returns:
        List of SensorReading objects
        
    Raises:
        ValueError: If payload is malformed
    """
    if len(data) < 1:
        raise ValueError("DATA payload must contain reading count")
    
    # Decode reading count
    reading_count = struct.unpack('!B', data[0:1])[0]
    
    if reading_count == 0:
        raise ValueError("DATA message must contain at least one reading")
    
    # Validate payload size
    expected_size = 1 + (reading_count * READING_SIZE)
    if len(data) < expected_size:
        raise ValueError(f"Payload too short: {len(data)} bytes, expected {expected_size}")
    
    # Decode readings
    readings = []
    offset = 1
    
    for _ in range(reading_count):
        sensor_type, value = struct.unpack('!Bf', data[offset:offset + READING_SIZE])
        readings.append(SensorReading(sensor_type=sensor_type, value=value))
        offset += READING_SIZE
    
    return readings
