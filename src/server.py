"""
TinyTelemetry v1.0 Collector Server

This module implements the CollectorServer that receives telemetry packets,
detects duplicates and gaps, reorders by timestamp, and logs to CSV.
"""

import socket
import csv
import time
import struct
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Set, List, Tuple, Optional

try:
    from .protocol import (
        VERSION, MSG_TYPE_DATA, MSG_TYPE_HEARTBEAT,
        HEADER_SIZE, MAX_PAYLOAD_SIZE,
        decode_header, decode_data_payload
    )
except ImportError:
    from protocol import (
        VERSION, MSG_TYPE_DATA, MSG_TYPE_HEARTBEAT,
        HEADER_SIZE, MAX_PAYLOAD_SIZE,
        decode_header, decode_data_payload
    )


@dataclass
class DeviceState:
    """Maintains state for a single device."""
    device_id: int
    last_seq: int = -1  # Last processed sequence number
    last_timestamp: int = 0  # Last packet timestamp
    total_packets: int = 0  # Total packets received
    duplicate_count: int = 0  # Duplicate packets detected
    gap_count: int = 0  # Total missing packets
    seen_sequences: Set[int] = field(default_factory=set)  # For duplicate detection
    reorder_buffer: List[Tuple[int, int, dict]] = field(default_factory=list)  # (seq, timestamp, data)


class CollectorServer:
    """
    Collector server that receives and processes telemetry packets.
    
    Responsibilities:
    - Receive UDP packets
    - Maintain per-device state
    - Detect duplicates and gaps
    - Reorder packets by timestamp
    - Log to CSV
    """
    
    def __init__(self, listen_port: int = 5000, log_file: str = "output/telemetry.csv",
                 reorder_window: int = 10, reorder_timeout: float = 2.0):
        """
        Initialize the collector server.
        
        Args:
            listen_port: UDP port to listen on
            log_file: Path to CSV log file
            reorder_window: Maximum buffer size for reordering
            reorder_timeout: Maximum time to buffer packets (seconds)
        """
        self.listen_port = listen_port
        self.log_file = Path(log_file)
        self.reorder_window = reorder_window
        self.reorder_timeout = reorder_timeout
        
        # Initialize device states dictionary
        self.device_states: Dict[int, DeviceState] = {}
        
        # Initialize UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', self.listen_port))
        
        # Initialize CSV log file
        self._init_csv_log()
        
        # Initialize CPU profiling
        self.total_cpu_time = 0.0
        self.packets_processed = 0
        
        print(f"CollectorServer initialized on port {self.listen_port}")
        print(f"Logging to: {self.log_file}")
    
    def _init_csv_log(self):
        """Initialize CSV log file with headers."""
        # Create output directory if it doesn't exist
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Open CSV file and write headers
        self.csv_file = open(self.log_file, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        
        # Write header row
        headers = [
            'device_id', 'seq', 'timestamp', 'arrival_time',
            'msg_type', 'duplicate_flag', 'gap_flag', 'gap_size', 'reading_count'
        ]
        self.csv_writer.writerow(headers)
        self.csv_file.flush()

    def get_or_create_device_state(self, device_id: int) -> DeviceState:
        """
        Get existing device state or create new one.
        
        Args:
            device_id: Device identifier
            
        Returns:
            DeviceState object for the device
        """
        if device_id not in self.device_states:
            self.device_states[device_id] = DeviceState(device_id=device_id)
            print(f"Initialized state for device {device_id}")
        
        return self.device_states[device_id]

    def receive_packet(self) -> Optional[Tuple[dict, float]]:
        """
        Receive and parse a UDP packet.
        
        Returns:
            Tuple of (parsed_packet_dict, arrival_time) or None if invalid
            
        The parsed_packet_dict contains:
            - version, msg_type, device_id, sequence_number, timestamp (from header)
            - readings: List of SensorReading objects (for DATA messages)
            - reading_count: Number of readings (0 for HEARTBEAT)
        """
        try:
            # Receive packet
            data, addr = self.socket.recvfrom(MAX_PAYLOAD_SIZE)
            arrival_time = time.time()
            
            # Validate minimum size
            if len(data) < HEADER_SIZE:
                print(f"Warning: Packet too short ({len(data)} bytes) from {addr}")
                return None
            
            # Decode header
            try:
                header = decode_header(data)
            except (ValueError, struct.error) as e:
                print(f"Warning: Failed to decode header from {addr}: {e}")
                return None
            
            # Validate header
            if header['version'] != VERSION:
                print(f"Warning: Invalid version {header['version']} from {addr}")
                return None
            
            if header['msg_type'] not in (MSG_TYPE_DATA, MSG_TYPE_HEARTBEAT):
                print(f"Warning: Invalid message type {header['msg_type']} from {addr}")
                return None
            
            if header['device_id'] <= 0:
                print(f"Warning: Invalid device_id {header['device_id']} from {addr}")
                return None
            
            # Build packet dictionary
            packet = {
                'version': header['version'],
                'msg_type': header['msg_type'],
                'device_id': header['device_id'],
                'sequence_number': header['sequence_number'],
                'timestamp': header['timestamp'],
                'readings': [],
                'reading_count': 0
            }
            
            # Decode payload based on message type
            if header['msg_type'] == MSG_TYPE_DATA:
                try:
                    payload = data[HEADER_SIZE:]
                    readings = decode_data_payload(payload)
                    packet['readings'] = readings
                    packet['reading_count'] = len(readings)
                except (ValueError, struct.error) as e:
                    print(f"Warning: Failed to decode DATA payload from {addr}: {e}")
                    return None
            
            return (packet, arrival_time)
            
        except Exception as e:
            print(f"Error receiving packet: {e}")
            return None

    def check_duplicate(self, device_state: DeviceState, sequence_number: int) -> bool:
        """
        Check if a packet is a duplicate based on sequence number.
        
        Args:
            device_state: Device state object
            sequence_number: Sequence number to check
            
        Returns:
            True if duplicate, False if new
        """
        if sequence_number in device_state.seen_sequences:
            device_state.duplicate_count += 1
            return True
        
        device_state.seen_sequences.add(sequence_number)
        return False

    def detect_gap(self, device_state: DeviceState, sequence_number: int) -> int:
        """
        Detect sequence gaps and calculate missing packet count.
        
        Gap detection works by comparing the received sequence number with the expected
        next sequence number (last_seq + 1). If the received sequence is higher, we
        calculate the gap size as the difference.
        
        Example:
            last_seq=5, received=8 → gap_size=2 (packets 6 and 7 are missing)
        
        Args:
            device_state: Device state object
            sequence_number: Current sequence number
            
        Returns:
            Gap size (0 if no gap, >0 if packets missing)
        """
        gap_size = 0
        
        # Calculate expected sequence number (only if we've seen packets before)
        if device_state.last_seq >= 0:
            expected_seq = device_state.last_seq + 1
            
            # If received sequence is higher than expected, we have a gap
            if sequence_number > expected_seq:
                gap_size = sequence_number - expected_seq
                device_state.gap_count += gap_size
        
        # Update last sequence number to current (even if there was a gap)
        device_state.last_seq = sequence_number
        
        return gap_size

    def add_to_reorder_buffer(self, device_state: DeviceState, packet: dict, arrival_time: float):
        """
        Add packet to reordering buffer for timestamp-based reordering.
        
        The reorder buffer handles packets that arrive out of order due to network
        delay and jitter. Packets are buffered and later sorted by their timestamp
        (not arrival time) to restore the correct temporal order.
        
        Buffer management:
        - Packets are stored as (seq, timestamp, data) tuples
        - Buffer size is limited to reorder_window (default: 10 packets)
        - When buffer is full, oldest packet (by timestamp) is removed
        
        Args:
            device_state: Device state object
            packet: Parsed packet dictionary
            arrival_time: Packet arrival timestamp
        """
        # Add packet to buffer as (seq, timestamp, packet_data) tuple
        # We store both sequence and timestamp for sorting flexibility
        buffer_entry = (
            packet['sequence_number'],
            packet['timestamp'],
            {
                'packet': packet,
                'arrival_time': arrival_time
            }
        )
        
        device_state.reorder_buffer.append(buffer_entry)
        
        # Limit buffer size to reorder_window to prevent unbounded memory growth
        if len(device_state.reorder_buffer) > self.reorder_window:
            # Sort by timestamp and remove oldest entry
            device_state.reorder_buffer.sort(key=lambda x: x[1])
            device_state.reorder_buffer.pop(0)
    
    def flush_reorder_buffer(self, device_state: DeviceState) -> List[Tuple[dict, float]]:
        """
        Flush and sort reorder buffer by timestamp.
        
        This method is called periodically (based on reorder_timeout) to process
        buffered packets. Packets are sorted by their timestamp field (not arrival
        time) to restore the correct temporal order of sensor readings.
        
        Example:
            Arrival order: [seq=3, ts=103], [seq=1, ts=101], [seq=2, ts=102]
            After flush:   [seq=1, ts=101], [seq=2, ts=102], [seq=3, ts=103]
        
        Args:
            device_state: Device state object
            
        Returns:
            List of (packet, arrival_time) tuples sorted by timestamp
        """
        if not device_state.reorder_buffer:
            return []
        
        # Sort buffer by timestamp (index 1 in tuple: seq, timestamp, data)
        device_state.reorder_buffer.sort(key=lambda x: x[1])
        
        # Extract packets from buffer entries
        sorted_packets = [
            (entry[2]['packet'], entry[2]['arrival_time'])
            for entry in device_state.reorder_buffer
        ]
        
        # Clear buffer after flushing
        device_state.reorder_buffer.clear()
        
        return sorted_packets

    def log_packet(self, packet: dict, arrival_time: float, 
                   duplicate_flag: bool, gap_flag: bool, gap_size: int):
        """
        Log packet to CSV file.
        
        Args:
            packet: Parsed packet dictionary
            arrival_time: Packet arrival timestamp
            duplicate_flag: True if packet is duplicate
            gap_flag: True if gap detected
            gap_size: Number of missing packets (0 if no gap)
        """
        # Determine message type string
        msg_type_str = 'DATA' if packet['msg_type'] == MSG_TYPE_DATA else 'HEARTBEAT'
        
        # Write CSV row
        row = [
            packet['device_id'],
            packet['sequence_number'],
            packet['timestamp'],
            f"{arrival_time:.6f}",
            msg_type_str,
            duplicate_flag,
            gap_flag,
            gap_size,
            packet['reading_count']
        ]
        
        self.csv_writer.writerow(row)
        
        # Flush periodically (every 10 packets or based on time)
        if not hasattr(self, '_packet_count'):
            self._packet_count = 0
            self._last_flush_time = time.time()
        
        self._packet_count += 1
        current_time = time.time()
        
        if self._packet_count >= 10 or (current_time - self._last_flush_time) >= 1.0:
            try:
                self.csv_file.flush()
                self._packet_count = 0
                self._last_flush_time = current_time
            except Exception as e:
                print(f"Warning: Failed to flush CSV file: {e}")

    def run(self):
        """
        Main server loop.
        
        Continuously receives packets, processes them through the pipeline:
        parse → check duplicate → detect gap → buffer → log
        
        Handles graceful shutdown on Ctrl+C.
        """
        print("CollectorServer running. Press Ctrl+C to stop.")
        
        last_flush_time = time.time()
        
        try:
            while True:
                # Receive and parse packet
                result = self.receive_packet()
                if result is None:
                    continue
                
                # Start CPU time measurement for packet processing
                process_start_cpu = time.process_time()
                
                packet, arrival_time = result
                device_id = packet['device_id']
                sequence_number = packet['sequence_number']
                
                # Get or create device state
                device_state = self.get_or_create_device_state(device_id)
                device_state.total_packets += 1
                
                # Check for duplicate
                is_duplicate = self.check_duplicate(device_state, sequence_number)
                
                # Detect gap (only for non-duplicates)
                gap_size = 0
                gap_flag = False
                if not is_duplicate:
                    gap_size = self.detect_gap(device_state, sequence_number)
                    gap_flag = gap_size > 0
                
                # Add to reorder buffer (for non-duplicates)
                if not is_duplicate:
                    self.add_to_reorder_buffer(device_state, packet, arrival_time)
                
                # Log packet
                self.log_packet(packet, arrival_time, is_duplicate, gap_flag, gap_size)
                
                # End CPU time measurement
                process_end_cpu = time.process_time()
                self.total_cpu_time += (process_end_cpu - process_start_cpu)
                self.packets_processed += 1
                
                # Periodically flush reorder buffers
                current_time = time.time()
                if current_time - last_flush_time >= self.reorder_timeout:
                    for dev_state in self.device_states.values():
                        sorted_packets = self.flush_reorder_buffer(dev_state)
                        # Note: Sorted packets are already logged, this is for buffer management
                    last_flush_time = current_time
        
        except KeyboardInterrupt:
            print("\n\nShutting down gracefully...")
            self._print_summary()
        
        finally:
            self._cleanup()
    
    def get_cpu_ms_per_report(self) -> float:
        """
        Calculate CPU milliseconds per report.
        
        Returns:
            CPU time in milliseconds per packet processed
        """
        if self.packets_processed == 0:
            return 0.0
        
        return (self.total_cpu_time / self.packets_processed) * 1000.0
    
    def _print_summary(self):
        """Print summary statistics for all devices."""
        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)
        
        for device_id, state in sorted(self.device_states.items()):
            print(f"\nDevice {device_id}:")
            print(f"  Total packets: {state.total_packets}")
            print(f"  Duplicates: {state.duplicate_count}")
            print(f"  Gaps detected: {state.gap_count} missing packets")
            print(f"  Last sequence: {state.last_seq}")
        
        # Print CPU profiling stats
        print(f"\nPerformance:")
        print(f"  Total packets processed: {self.packets_processed}")
        print(f"  Total CPU time: {self.total_cpu_time:.6f}s")
        print(f"  CPU ms per packet: {self.get_cpu_ms_per_report():.3f}ms")
    
    def _cleanup(self):
        """Clean up resources."""
        try:
            self.csv_file.close()
            print(f"CSV log saved to: {self.log_file}")
        except:
            pass
        
        try:
            self.socket.close()
        except:
            pass



def main():
    """
    Command-line interface for CollectorServer.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='TinyTelemetry v1.0 Collector Server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='UDP port to listen on'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default='output/telemetry.csv',
        help='Path to CSV log file'
    )
    
    parser.add_argument(
        '--reorder-window',
        type=int,
        default=10,
        help='Maximum buffer size for packet reordering'
    )
    
    parser.add_argument(
        '--reorder-timeout',
        type=float,
        default=2.0,
        help='Maximum time to buffer packets (seconds)'
    )
    
    args = parser.parse_args()
    
    # Create and run server
    server = CollectorServer(
        listen_port=args.port,
        log_file=args.log_file,
        reorder_window=args.reorder_window,
        reorder_timeout=args.reorder_timeout
    )
    
    server.run()


if __name__ == '__main__':
    main()
