"""
TinyTelemetry v1.0 - IoT Telemetry Protocol

A lightweight, UDP-based telemetry protocol for constrained IoT sensors.
"""

__version__ = '1.0.0'
__author__ = 'TinyTelemetry Project'

from .protocol import (
    VERSION,
    MSG_TYPE_DATA,
    MSG_TYPE_HEARTBEAT,
    SENSOR_TYPE_TEMPERATURE,
    SENSOR_TYPE_HUMIDITY,
    SENSOR_TYPE_VOLTAGE,
    HEADER_SIZE,
    MAX_PAYLOAD_SIZE,
    READING_SIZE,
    MAX_BATCH_SIZE,
    SensorReading,
    TelemetryPacket,
    encode_header,
    decode_header,
    encode_data_payload,
    decode_data_payload,
)

__all__ = [
    'VERSION',
    'MSG_TYPE_DATA',
    'MSG_TYPE_HEARTBEAT',
    'SENSOR_TYPE_TEMPERATURE',
    'SENSOR_TYPE_HUMIDITY',
    'SENSOR_TYPE_VOLTAGE',
    'HEADER_SIZE',
    'MAX_PAYLOAD_SIZE',
    'READING_SIZE',
    'MAX_BATCH_SIZE',
    'SensorReading',
    'TelemetryPacket',
    'encode_header',
    'decode_header',
    'encode_data_payload',
    'decode_data_payload',
]
