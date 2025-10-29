#!/usr/bin/env python3
"""
TinyTelemetry v1.0 Baseline Test Script

This script runs a baseline test with no network impairment to validate
the protocol under ideal conditions.

Test parameters:
- Duration: 60 seconds
- Interval: 1 second
- Batch size: 1 (non-batched)
- Expected: ≥99% packet delivery, sequence numbers in order
"""

import subprocess
import time
import sys
import csv
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from metrics import MetricsCalculator, save_metrics_json


def run_baseline_test(device_id=1001, interval=1, duration=60, batch_size=1,
                     server_port=5000, log_file='output/baseline_telemetry.csv',
                     scenario_name='baseline', enable_pcap=False, pcap_file=None):
    """
    Run baseline test scenario.
    
    Args:
        device_id: Device identifier for client
        interval: Reporting interval in seconds
        duration: Test duration in seconds
        batch_size: Number of readings per packet
        server_port: Server UDP port
        log_file: Path to CSV log file
        scenario_name: Name of test scenario for metrics output
        enable_pcap: Enable packet capture (requires tcpdump/tshark)
        pcap_file: Path to pcap output file (default: output/{scenario}_capture.pcap)
        
    Returns:
        Dictionary with test results and metrics
    """
    print("="*60)
    print("BASELINE TEST")
    print("="*60)
    print(f"Device ID: {device_id}")
    print(f"Interval: {interval}s")
    print(f"Duration: {duration}s")
    print(f"Batch size: {batch_size}")
    print(f"Server port: {server_port}")
    print(f"Log file: {log_file}")
    
    if enable_pcap:
        if pcap_file is None:
            pcap_file = f"output/{scenario_name}_capture.pcap"
        print(f"Packet capture: {pcap_file}")
    
    print("="*60)
    
    # Ensure output directory exists
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Start packet capture if enabled
    pcap_process = None
    if enable_pcap:
        print("\n[0/4] Starting packet capture...")
        
        # Determine which capture tool to use
        import platform
        import shutil
        
        if platform.system() == 'Linux':
            # Use tcpdump on Linux
            if shutil.which('tcpdump'):
                pcap_cmd = [
                    'tcpdump',
                    '-i', 'lo',
                    '-w', pcap_file,
                    'udp', 'port', str(server_port)
                ]
                
                try:
                    pcap_process = subprocess.Popen(
                        pcap_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    time.sleep(0.5)  # Give tcpdump time to start
                    print(f"  Packet capture started (tcpdump)")
                except Exception as e:
                    print(f"  [WARNING] Failed to start tcpdump: {e}")
                    pcap_process = None
            else:
                print("  [WARNING] tcpdump not found, skipping packet capture")
        
        elif platform.system() == 'Windows':
            # Use tshark on Windows (Wireshark CLI)
            if shutil.which('tshark'):
                pcap_cmd = [
                    'tshark',
                    '-i', 'Loopback',
                    '-w', pcap_file,
                    '-f', f'udp port {server_port}'
                ]
                
                try:
                    pcap_process = subprocess.Popen(
                        pcap_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    time.sleep(0.5)  # Give tshark time to start
                    print(f"  Packet capture started (tshark)")
                except Exception as e:
                    print(f"  [WARNING] Failed to start tshark: {e}")
                    pcap_process = None
            else:
                print("  [WARNING] tshark not found, skipping packet capture")
                print("  [INFO] Install Wireshark to enable packet capture on Windows")
        
        else:
            print(f"  [WARNING] Packet capture not supported on {platform.system()}")
    
    # Start server in background
    step_num = 1 if not enable_pcap else 1
    print(f"\n[{step_num}/4] Starting collector server...")
    server_cmd = [
        sys.executable, '-m', 'src.server',
        '--port', str(server_port),
        '--log-file', log_file
    ]
    
    server_process = subprocess.Popen(
        server_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Wait for server to be ready
    step_num = 2 if not enable_pcap else 2
    print(f"[{step_num}/4] Waiting for server to be ready...")
    time.sleep(1)
    
    # Check if server is still running
    if server_process.poll() is not None:
        print("[ERROR] Server failed to start!")
        output, _ = server_process.communicate()
        print(output)
        
        # Stop packet capture if running
        if pcap_process:
            pcap_process.terminate()
            pcap_process.wait()
        
        return None
    
    step_num = 3 if not enable_pcap else 3
    print(f"[{step_num}/4] Starting sensor client...")
    
    # Start client
    client_cmd = [
        sys.executable, '-m', 'src.client',
        '--device-id', str(device_id),
        '--server-host', 'localhost',
        '--server-port', str(server_port),
        '--interval', str(interval),
        '--duration', str(duration),
        '--batch-size', str(batch_size)
    ]
    
    try:
        # Run client and wait for completion
        client_result = subprocess.run(
            client_cmd,
            capture_output=True,
            text=True,
            timeout=duration + 10  # Add buffer time
        )
        
        step_num = 4 if not enable_pcap else 4
        print(f"[{step_num}/4] Client completed. Stopping server...")
        
        # Stop packet capture if running
        if pcap_process:
            print("  Stopping packet capture...")
            pcap_process.terminate()
            try:
                pcap_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pcap_process.kill()
                pcap_process.wait()
            
            if Path(pcap_file).exists():
                print(f"  Packet capture saved to: {pcap_file}")
            else:
                print(f"  [WARNING] Packet capture file not found: {pcap_file}")
        
        # Stop server gracefully
        server_process.terminate()
        
        # Wait for server to finish (with timeout)
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("[WARNING] Server did not stop gracefully, forcing...")
            server_process.kill()
            server_process.wait()
        
        print("\n" + "="*60)
        print("TEST EXECUTION COMPLETE")
        print("="*60)
        
        # Calculate metrics from CSV log
        print("\nCalculating metrics...")
        
        if not Path(log_file).exists():
            print(f"[ERROR] Log file not found: {log_file}")
            return None
        
        calculator = MetricsCalculator()
        metrics = calculator.calculate_from_csv(log_file)
        
        # Verify results
        print("\n" + "="*60)
        print("METRICS")
        print("="*60)
        print(f"Bytes per report: {metrics.bytes_per_report:.2f}")
        print(f"Packets received: {metrics.packets_received}")
        print(f"Packets sent: {metrics.packets_sent}")
        print(f"Duplicate rate: {metrics.duplicate_rate:.4f} ({metrics.duplicate_rate*100:.2f}%)")
        print(f"Sequence gaps: {metrics.sequence_gap_count}")
        
        # Calculate delivery rate
        delivery_rate = metrics.packets_received / metrics.packets_sent if metrics.packets_sent > 0 else 0
        print(f"Delivery rate: {delivery_rate:.4f} ({delivery_rate*100:.2f}%)")
        
        # Verify sequence order
        print("\nVerifying sequence order...")
        sequence_in_order = verify_sequence_order(log_file, device_id)
        
        # Check test requirements
        print("\n" + "="*60)
        print("TEST VALIDATION")
        print("="*60)
        
        passed = True
        
        # Requirement 15.1: ≥99% packet delivery
        if delivery_rate >= 0.99:
            print("[PASS] Delivery rate >=99%")
        else:
            print(f"[FAIL] Delivery rate {delivery_rate*100:.2f}% < 99%")
            passed = False
        
        # Requirement 15.2: Sequence numbers in order
        if sequence_in_order:
            print("[PASS] Sequence numbers are in order")
        else:
            print("[FAIL] Sequence numbers are out of order")
            passed = False
        
        print("="*60)
        
        if passed:
            print("\n[PASS] BASELINE TEST PASSED")
        else:
            print("\n[FAIL] BASELINE TEST FAILED")
        
        # Prepare results dictionary
        results = {
            'test_scenario': scenario_name,
            'duration_seconds': duration,
            'reporting_interval': interval,
            'batch_size': batch_size,
            'metrics': {
                'bytes_per_report': metrics.bytes_per_report,
                'packets_received': metrics.packets_received,
                'packets_sent': metrics.packets_sent,
                'duplicate_rate': metrics.duplicate_rate,
                'sequence_gap_count': metrics.sequence_gap_count,
                'delivery_rate': delivery_rate
            },
            'validation': {
                'passed': passed,
                'delivery_rate_ok': delivery_rate >= 0.99,
                'sequence_order_ok': sequence_in_order
            }
        }
        
        return results
        
    except subprocess.TimeoutExpired:
        print("[ERROR] Client timed out!")
        server_process.kill()
        
        # Stop packet capture if running
        if pcap_process:
            pcap_process.kill()
        
        return None
    
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        server_process.kill()
        
        # Stop packet capture if running
        if pcap_process:
            pcap_process.kill()
        
        raise


def verify_sequence_order(csv_file, device_id):
    """
    Verify that sequence numbers are in order for non-duplicate packets.
    
    Args:
        csv_file: Path to CSV log file
        device_id: Device ID to check
        
    Returns:
        True if sequences are in order, False otherwise
    """
    sequences = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if int(row['device_id']) == device_id:
                is_duplicate = row['duplicate_flag'].lower() == 'true'
                
                if not is_duplicate:
                    seq = int(row['seq'])
                    sequences.append(seq)
    
    # Check if sequences are monotonically increasing
    for i in range(1, len(sequences)):
        if sequences[i] <= sequences[i-1]:
            print(f"  Sequence out of order: {sequences[i-1]} -> {sequences[i]}")
            return False
    
    print(f"  All {len(sequences)} sequences in order")
    return True


def main():
    """Main entry point for baseline test script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run baseline test for TinyTelemetry protocol',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--device-id',
        type=int,
        default=1001,
        help='Device identifier'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=1,
        choices=[1, 5, 30],
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
        help='Number of readings per packet'
    )
    
    parser.add_argument(
        '--server-port',
        type=int,
        default=5000,
        help='Server UDP port'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default='output/baseline_telemetry.csv',
        help='Path to CSV log file'
    )
    
    parser.add_argument(
        '--output-json',
        type=str,
        default='output/baseline_metrics.json',
        help='Path to output metrics JSON file'
    )
    
    parser.add_argument(
        '--enable-pcap',
        action='store_true',
        help='Enable packet capture (requires tcpdump on Linux or tshark on Windows)'
    )
    
    parser.add_argument(
        '--pcap-file',
        type=str,
        default=None,
        help='Path to packet capture file (default: output/baseline_capture.pcap)'
    )
    
    args = parser.parse_args()
    
    # Run test
    results = run_baseline_test(
        device_id=args.device_id,
        interval=args.interval,
        duration=args.duration,
        batch_size=args.batch_size,
        server_port=args.server_port,
        log_file=args.log_file,
        scenario_name='baseline',
        enable_pcap=args.enable_pcap,
        pcap_file=args.pcap_file
    )
    
    if results is None:
        print("\n[ERROR] Test failed to complete")
        sys.exit(1)
    
    # Save metrics to JSON
    save_metrics_json(results, args.output_json)
    
    # Exit with appropriate code
    if results['validation']['passed']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
