"""
TinyTelemetry v1.0 Sensor Client

This module implements the SensorClient that simulates IoT sensors and transmits
telemetry data to a collector server.
"""

import socket
import time
import random
import signal
import sys
from typing import List, Optional
from dataclasses import dataclass

from .protocol import (
    VERSION, MSG_TYPE_DATA, MSG_TYPE_HEARTBEAT,
    SENSOR_TYPE_TEMPERATURE, SENSOR_TYPE_HUMIDITY, SENSOR_TYPE_VOLTAGE,
    SensorReading, encode_header, encode_data_payload
)


class SensorClient:
    """
    Sensor client that generates and transmits telemetry data.
    """
    
    def __init__(self, device_id: int, server_host: str, server_port: int,
                 interval: int, duration: int, batch_size: int = 1,
                 sensor_types: Optional[List[int]] = None):
        """
        Initialize the sensor client.
        
        Args:
            device_id: Unique sensor identifier (1-65535)
            server_host: Collector server IP address or hostname
            server_port: Collector server UDP port
            interval: Reporting interval in seconds (1, 5, or 30)
            duration: Test duration in seconds
            batch_size: Number of readings per packet (1-37, default=1)
            sensor_types: List of sensor types to simulate (default: all types)
        """
        self.device_id = device_id
        self.server_host = server_host
        self.server_port = server_port
        self.interval = interval
        self.duration = duration
        self.batch_size = batch_size
        self.sensor_types = sensor_types or [
            SENSOR_TYPE_TEMPERATURE,
            SENSOR_TYPE_HUMIDITY,
            SENSOR_TYPE_VOLTAGE
        ]
        
        # Initialize UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Initialize state
        self.sequence_number = 0
        self.reading_buffer = []
        
        # Track start time
        self.start_time = None
        self.running = True

    def generate_reading(self, sensor_type: int) -> SensorReading:
        """
        Generate a simulated sensor reading.
        
        Args:
            sensor_type: Type of sensor (SENSOR_TYPE_*)
            
        Returns:
            SensorReading object with random value in appropriate range
        """
        if sensor_type == SENSOR_TYPE_TEMPERATURE:
            # Temperature: 15-30°C
            value = random.uniform(15.0, 30.0)
        elif sensor_type == SENSOR_TYPE_HUMIDITY:
            # Humidity: 30-80%
            value = random.uniform(30.0, 80.0)
        elif sensor_type == SENSOR_TYPE_VOLTAGE:
            # Voltage: 3.0-5.0V
            value = random.uniform(3.0, 5.0)
        else:
            raise ValueError(f"Unknown sensor type: {sensor_type}")
        
        return SensorReading(sensor_type=sensor_type, value=value)
    
    def generate_readings(self) -> List[SensorReading]:
        """
        Generate readings for all configured sensor types.
        
        Returns:
            List of SensorReading objects
        """
        return [self.generate_reading(st) for st in self.sensor_types]

    def send_data(self, readings: List[SensorReading]) -> None:
        """
        Send DATA message with sensor readings.
        
        Args:
            readings: List of SensorReading objects to send
        """
        # Get current timestamp
        timestamp = int(time.time())
        
        # Encode header
        header = encode_header(
            VERSION,
            MSG_TYPE_DATA,
            self.device_id,
            self.sequence_number,
            timestamp
        )
        
        # Encode payload
        payload = encode_data_payload(readings)
        
        # Combine header and payload
        packet = header + payload
        
        # Send via UDP
        self.socket.sendto(packet, (self.server_host, self.server_port))
        
        # Log sent packet
        print(f"[DATA] seq={self.sequence_number}, timestamp={timestamp}, "
              f"readings={len(readings)}, bytes={len(packet)}")
        
        # Increment sequence number
        self.sequence_number += 1

    def send_heartbeat(self) -> None:
        """
        Send HEARTBEAT message (no payload).
        """
        # Get current timestamp
        timestamp = int(time.time())
        
        # Encode header (no payload for heartbeat)
        packet = encode_header(
            VERSION,
            MSG_TYPE_HEARTBEAT,
            self.device_id,
            self.sequence_number,
            timestamp
        )
        
        # Send via UDP
        self.socket.sendto(packet, (self.server_host, self.server_port))
        
        # Log sent heartbeat
        print(f"[HEARTBEAT] seq={self.sequence_number}, timestamp={timestamp}")
        
        # Increment sequence number
        self.sequence_number += 1

    def add_to_batch(self, readings: List[SensorReading]) -> None:
        """
        Add readings to batch buffer and send when batch size is reached.
        
        Batching reduces bandwidth overhead by grouping multiple readings into
        a single packet. This amortizes the 12-byte header cost across multiple
        readings, improving bandwidth efficiency.
        
        Example with batch_size=10:
        - Without batching: 10 packets × 18 bytes = 180 bytes
        - With batching: 1 packet × 63 bytes = 63 bytes (65% reduction)
        
        Args:
            readings: List of SensorReading objects to add to batch
        """
        # Accumulate readings in buffer
        self.reading_buffer.extend(readings)
        
        # Check if we've accumulated enough readings to send a batch
        if len(self.reading_buffer) >= self.batch_size:
            # Send exactly batch_size readings
            self.send_data(self.reading_buffer[:self.batch_size])
            # Keep any extra readings in buffer for next batch
            self.reading_buffer = self.reading_buffer[self.batch_size:]
    
    def flush_batch(self) -> None:
        """
        Flush any remaining readings in the batch buffer.
        """
        if self.reading_buffer:
            self.send_data(self.reading_buffer)
            self.reading_buffer = []

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n[INFO] Shutting down gracefully...")
        self.running = False
    
    def run(self) -> None:
        """
        Main client loop: generate and send telemetry data.
        """
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        
        print(f"[INFO] Starting sensor client (device_id={self.device_id})")
        print(f"[INFO] Server: {self.server_host}:{self.server_port}")
        print(f"[INFO] Interval: {self.interval}s, Duration: {self.duration}s, Batch: {self.batch_size}")
        print(f"[INFO] Sensor types: {self.sensor_types}")
        
        self.start_time = time.time()
        next_send_time = self.start_time
        
        try:
            while self.running:
                current_time = time.time()
                elapsed = current_time - self.start_time
                
                # Check if duration expired
                if elapsed >= self.duration:
                    print(f"[INFO] Duration {self.duration}s reached, stopping...")
                    break
                
                # Check if it's time to send
                if current_time >= next_send_time:
                    # Generate readings
                    readings = self.generate_readings()
                    
                    # Handle batching
                    if self.batch_size == 1:
                        # Non-batched mode: send immediately
                        self.send_data(readings)
                    else:
                        # Batched mode: add to buffer
                        self.add_to_batch(readings)
                    
                    # Schedule next send
                    next_send_time += self.interval
                
                # Sleep briefly to avoid busy waiting
                time.sleep(0.1)
            
            # Flush any remaining batched readings
            if self.batch_size > 1:
                self.flush_batch()
            
            print(f"[INFO] Client stopped. Total packets sent: {self.sequence_number}")
            
        except Exception as e:
            print(f"[ERROR] Client error: {e}")
            raise
        finally:
            self.socket.close()



def main():
    """
    Command-line interface for the sensor client.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='TinyTelemetry v1.0 Sensor Client',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--device-id',
        type=int,
        required=True,
        help='Unique device identifier (1-65535)'
    )
    
    parser.add_argument(
        '--server-host',
        type=str,
        default='localhost',
        help='Collector server hostname or IP address'
    )
    
    parser.add_argument(
        '--server-port',
        type=int,
        default=5000,
        help='Collector server UDP port'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        choices=[1, 5, 30],
        default=1,
        help='Reporting interval in seconds'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Test duration in seconds'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1,
        help='Number of readings per packet (1-37)'
    )
    
    parser.add_argument(
        '--sensor-types',
        type=str,
        default='temperature,humidity,voltage',
        help='Comma-separated list of sensor types (temperature, humidity, voltage)'
    )
    
    args = parser.parse_args()
    
    # Validate device_id
    if args.device_id <= 0 or args.device_id > 65535:
        parser.error("device-id must be between 1 and 65535")
    
    # Validate batch_size
    if args.batch_size < 1 or args.batch_size > 37:
        parser.error("batch-size must be between 1 and 37")
    
    # Parse sensor types
    sensor_type_map = {
        'temperature': SENSOR_TYPE_TEMPERATURE,
        'humidity': SENSOR_TYPE_HUMIDITY,
        'voltage': SENSOR_TYPE_VOLTAGE
    }
    
    sensor_types = []
    for st in args.sensor_types.split(','):
        st = st.strip().lower()
        if st not in sensor_type_map:
            parser.error(f"Unknown sensor type: {st}")
        sensor_types.append(sensor_type_map[st])
    
    # Create and run client
    try:
        client = SensorClient(
            device_id=args.device_id,
            server_host=args.server_host,
            server_port=args.server_port,
            interval=args.interval,
            duration=args.duration,
            batch_size=args.batch_size,
            sensor_types=sensor_types
        )
        client.run()
    except Exception as e:
        print(f"[ERROR] Failed to run client: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
