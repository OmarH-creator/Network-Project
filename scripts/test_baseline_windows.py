#!/usr/bin/env python3
"""
TinyTelemetry v1.0 Windows-Compatible Baseline Test Script

This script runs a baseline test on Windows without network impairment.
For network impairment testing on Windows, use Clumsy manually.

Clumsy Setup Instructions:
1. Download Clumsy from: https://jagt.github.io/clumsy/
2. Run Clumsy as Administrator
3. Configure filters and impairments:
   - Filter: udp and udp.DstPort == 5000
   - For packet loss: Enable "Drop" with 5% probability
   - For delay/jitter: Enable "Lag" with 100ms delay and 10ms jitter
4. Click "Start" before running this test
5. Click "Stop" after test completes

Test parameters:
- Duration: 60 seconds (configurable)
- Interval: 1 second (configurable)
- Batch size: 1 (configurable)
- Expected: ≥99% packet delivery (baseline), gap detection (with loss)
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import the baseline test function
from test_baseline import run_baseline_test, main as baseline_main


def main():
    """
    Main entry point for Windows-compatible baseline test.
    
    This is essentially a wrapper around the baseline test with
    Windows-specific documentation and path handling.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run baseline test for TinyTelemetry protocol (Windows)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="""
WINDOWS NETWORK IMPAIRMENT TESTING:

For packet loss and delay/jitter testing on Windows, use Clumsy:

1. Download Clumsy: https://jagt.github.io/clumsy/
2. Run as Administrator
3. Configure impairments:

   PACKET LOSS TEST (5%):
   - Filter: udp and udp.DstPort == 5000
   - Enable "Drop" with 5%% probability
   - Click "Start"
   - Run this script
   - Click "Stop" when done

   DELAY/JITTER TEST (100ms ±10ms):
   - Filter: udp and udp.DstPort == 5000
   - Enable "Lag" with:
     * Inbound: 100ms
     * Jitter: 10ms
   - Click "Start"
   - Run this script
   - Click "Stop" when done

PACKET CAPTURE ON WINDOWS:

Install Wireshark to enable packet capture:
1. Download: https://www.wireshark.org/download.html
2. Install with "TShark" component
3. Add Wireshark directory to PATH
4. Use --enable-pcap flag with this script

Example: python scripts/test_baseline_windows.py --enable-pcap
        """
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
        default='output/windows_baseline_telemetry.csv',
        help='Path to CSV log file'
    )
    
    parser.add_argument(
        '--output-json',
        type=str,
        default='output/windows_baseline_metrics.json',
        help='Path to output metrics JSON file'
    )
    
    parser.add_argument(
        '--enable-pcap',
        action='store_true',
        help='Enable packet capture (requires Wireshark/tshark)'
    )
    
    parser.add_argument(
        '--pcap-file',
        type=str,
        default=None,
        help='Path to packet capture file (default: output/windows_baseline_capture.pcap)'
    )
    
    parser.add_argument(
        '--scenario-name',
        type=str,
        default='windows_baseline',
        help='Test scenario name for output files'
    )
    
    args = parser.parse_args()
    
    # Ensure paths use Windows-compatible format
    log_file = Path(args.log_file)
    output_json = Path(args.output_json)
    
    if args.pcap_file:
        pcap_file = Path(args.pcap_file)
    else:
        pcap_file = None
    
    print("="*60)
    print("TINYTELEMETRY v1.0 - WINDOWS BASELINE TEST")
    print("="*60)
    print(f"Platform: Windows")
    print(f"Duration: {args.duration}s")
    print(f"Interval: {args.interval}s")
    print(f"Batch size: {args.batch_size}")
    
    if args.enable_pcap:
        print(f"Packet capture: Enabled")
        print(f"  Note: Requires Wireshark/tshark installed")
    
    print("="*60)
    print()
    print("NOTE: For network impairment testing, use Clumsy manually.")
    print("      See --help for detailed instructions.")
    print()
    
    # Run test using the baseline test function
    results = run_baseline_test(
        device_id=args.device_id,
        interval=args.interval,
        duration=args.duration,
        batch_size=args.batch_size,
        server_port=args.server_port,
        log_file=str(log_file),
        scenario_name=args.scenario_name,
        enable_pcap=args.enable_pcap,
        pcap_file=str(pcap_file) if pcap_file else None
    )
    
    if results is None:
        print("\n[ERROR] Test failed to complete")
        sys.exit(1)
    
    # Save metrics to JSON
    from metrics import save_metrics_json
    save_metrics_json(results, str(output_json))
    
    # Exit with appropriate code
    if results.get('validation', {}).get('passed', False):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
