#!/usr/bin/env python3
"""
TinyTelemetry v1.0 Master Test Runner

This script runs all test scenarios multiple times, collects metrics,
calculates statistical summaries, and saves aggregated results.

Test scenarios:
- Baseline (no impairment)
- Packet loss (5%, Linux only)
- Delay/jitter (100ms ±10ms, Linux only)

Each scenario is run 5 times to gather statistical data.
"""

import subprocess
import sys
import json
import platform
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from metrics import StatisticalAnalyzer, save_metrics_json


def is_linux():
    """Check if running on Linux."""
    return platform.system() == 'Linux'


def run_baseline_test(run_number: int, duration: int = 60, interval: int = 1) -> Dict[str, Any]:
    """
    Run baseline test scenario.
    
    Args:
        run_number: Test run number (1-5)
        duration: Test duration in seconds
        interval: Reporting interval in seconds (1, 5, or 30)
        
    Returns:
        Dictionary with test results
    """
    print(f"\n{'='*60}")
    print(f"BASELINE TEST - Run {run_number} (Interval: {interval}s)")
    print(f"{'='*60}")
    
    log_file = f"output/baseline_interval{interval}_run{run_number}_telemetry.csv"
    output_json = f"output/baseline_interval{interval}_run{run_number}_metrics.json"
    pcap_file = f"output/baseline_interval{interval}_run{run_number}_capture.pcap"
    
    cmd = [
        sys.executable, 'scripts/test_baseline.py',
        '--duration', str(duration),
        '--interval', str(interval),
        '--log-file', log_file,
        '--output-json', output_json
    ]
    
    # Enable packet capture for first 2 runs (requirement: at least 2 pcap files per scenario)
    # Only enable on Linux or if tshark is available on Windows
    import shutil
    enable_pcap = run_number <= 2 and (is_linux() or shutil.which('tshark') is not None)
    
    if enable_pcap:
        cmd.extend(['--enable-pcap', '--pcap-file', pcap_file])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 20)
        
        # Print output for debugging
        if result.returncode != 0:
            print(f"[ERROR] Test failed with exit code {result.returncode}")
            if result.stdout:
                print("STDOUT:", result.stdout[:500])
            if result.stderr:
                print("STDERR:", result.stderr[:500])
        
        # Read results from JSON
        if Path(output_json).exists():
            with open(output_json, 'r') as f:
                data = json.load(f)
            print(f"✓ Run {run_number} completed successfully")
            return data
        else:
            print(f"[ERROR] Output file not found: {output_json}")
            if result.stdout:
                print("Test output:", result.stdout[:500])
            return None
            
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Baseline test run {run_number} timed out")
        return None
    except Exception as e:
        print(f"[ERROR] Baseline test run {run_number} failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_loss_test(run_number: int, duration: int = 60, loss_pct: int = 5) -> Dict[str, Any]:
    """
    Run packet loss test scenario (Linux only).
    
    Args:
        run_number: Test run number (1-5)
        duration: Test duration in seconds
        loss_pct: Packet loss percentage (0, 1, 5, 10)
        
    Returns:
        Dictionary with test results
    """
    if not is_linux():
        print("[SKIP] Packet loss test requires Linux")
        return None
    
    print(f"\n{'='*60}")
    print(f"PACKET LOSS TEST - Run {run_number} (Loss: {loss_pct}%)")
    print(f"{'='*60}")
    
    log_file = f"output/loss{loss_pct}_run{run_number}_telemetry.csv"
    output_json = f"output/loss{loss_pct}_run{run_number}_metrics.json"
    pcap_file = f"output/loss{loss_pct}_run{run_number}_capture.pcap"
    
    # Set environment variable for pcap file (used by bash script)
    import os
    env = os.environ.copy()
    env['PCAP_FILE'] = pcap_file
    
    cmd = [
        'sudo', 'bash', 'scripts/test_loss.sh',
        '1001',  # device_id
        '1',     # interval
        str(duration),  # duration
        '1',     # batch_size
        '5000',  # server_port
        str(loss_pct)  # loss_percentage
    ]
    
    # Update log file and output json in the script by modifying environment
    # Since the script uses fixed paths, we'll need to move files after
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30, env=env)
        
        # Move output files to run-specific names
        if Path('output/loss_telemetry.csv').exists():
            Path('output/loss_telemetry.csv').rename(log_file)
        
        if Path('output/loss_metrics.json').exists():
            Path('output/loss_metrics.json').rename(output_json)
            
            with open(output_json, 'r') as f:
                data = json.load(f)
            return data
        else:
            print(f"[ERROR] Output file not found")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Loss test run {run_number} timed out")
        return None
    except Exception as e:
        print(f"[ERROR] Loss test run {run_number} failed: {e}")
        return None


def run_delay_test(run_number: int, duration: int = 60) -> Dict[str, Any]:
    """
    Run delay/jitter test scenario (Linux only).
    
    Args:
        run_number: Test run number (1-5)
        duration: Test duration in seconds
        
    Returns:
        Dictionary with test results
    """
    if not is_linux():
        print("[SKIP] Delay/jitter test requires Linux")
        return None
    
    print(f"\n{'='*60}")
    print(f"DELAY/JITTER TEST - Run {run_number}")
    print(f"{'='*60}")
    
    log_file = f"output/delay_run{run_number}_telemetry.csv"
    output_json = f"output/delay_run{run_number}_metrics.json"
    pcap_file = f"output/delay_run{run_number}_capture.pcap"
    
    # Set environment variable for pcap file (used by bash script)
    import os
    env = os.environ.copy()
    env['PCAP_FILE'] = pcap_file
    
    cmd = [
        'sudo', 'bash', 'scripts/test_delay.sh',
        '1001',  # device_id
        '1',     # interval
        str(duration),  # duration
        '1',     # batch_size
        '5000'   # server_port
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30, env=env)
        
        # Move output files to run-specific names
        if Path('output/delay_telemetry.csv').exists():
            Path('output/delay_telemetry.csv').rename(log_file)
        
        if Path('output/delay_metrics.json').exists():
            Path('output/delay_metrics.json').rename(output_json)
            
            with open(output_json, 'r') as f:
                data = json.load(f)
            return data
        else:
            print(f"[ERROR] Output file not found")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Delay test run {run_number} timed out")
        return None
    except Exception as e:
        print(f"[ERROR] Delay test run {run_number} failed: {e}")
        return None


def calculate_statistics(results: List[Dict[str, Any]], metric_name: str) -> Dict[str, float]:
    """
    Calculate statistical summary for a specific metric.
    
    Args:
        results: List of test result dictionaries
        metric_name: Name of metric to analyze
        
    Returns:
        Dictionary with min, median, max
    """
    values = []
    
    for result in results:
        if result and 'metrics' in result:
            if metric_name in result['metrics']:
                values.append(result['metrics'][metric_name])
    
    if not values:
        return {'min': 0, 'median': 0, 'max': 0}
    
    analyzer = StatisticalAnalyzer()
    return analyzer.calculate_statistics(values)


def print_summary_table(scenario_name: str, results: List[Dict[str, Any]]):
    """
    Print summary table for a test scenario.
    
    Args:
        scenario_name: Name of test scenario
        results: List of test result dictionaries
    """
    print(f"\n{'='*60}")
    print(f"{scenario_name.upper()} - SUMMARY")
    print(f"{'='*60}")
    
    # Filter out None results
    valid_results = [r for r in results if r is not None]
    
    if not valid_results:
        print("No valid results")
        return
    
    print(f"Valid runs: {len(valid_results)}/{len(results)}")
    
    # Calculate statistics for each metric
    metrics_to_analyze = [
        'bytes_per_report',
        'packets_received',
        'duplicate_rate',
        'sequence_gap_count'
    ]
    
    print(f"\n{'Metric':<25} {'Min':<12} {'Median':<12} {'Max':<12}")
    print("-" * 60)
    
    for metric in metrics_to_analyze:
        stats = calculate_statistics(valid_results, metric)
        
        if metric == 'duplicate_rate':
            # Format as percentage
            print(f"{metric:<25} {stats['min']*100:>10.2f}% {stats['median']*100:>10.2f}% {stats['max']*100:>10.2f}%")
        elif metric == 'bytes_per_report':
            # Format with 2 decimal places
            print(f"{metric:<25} {stats['min']:>11.2f} {stats['median']:>11.2f} {stats['max']:>11.2f}")
        else:
            # Format as integer
            print(f"{metric:<25} {int(stats['min']):>11} {int(stats['median']):>11} {int(stats['max']):>11}")


def main():
    """Main entry point for master test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run all TinyTelemetry test scenarios with statistical analysis',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--runs',
        type=int,
        default=5,
        help='Number of times to run each test scenario'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Duration of each test run in seconds'
    )
    
    parser.add_argument(
        '--baseline-only',
        action='store_true',
        help='Run only baseline tests (skip loss and delay tests)'
    )
    
    parser.add_argument(
        '--test-intervals',
        action='store_true',
        help='Test multiple reporting intervals (1s, 5s, 30s) for plotting'
    )
    
    parser.add_argument(
        '--test-loss-rates',
        action='store_true',
        help='Test multiple loss rates (0%%, 1%%, 5%%, 10%%) for plotting'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("TINYTELEMETRY v1.0 - MASTER TEST RUNNER")
    print("="*60)
    print(f"Runs per scenario: {args.runs}")
    print(f"Duration per run: {args.duration}s")
    print(f"Platform: {platform.system()}")
    
    if not is_linux() and not args.baseline_only:
        print("\n[WARNING] Loss and delay tests require Linux")
        print("[WARNING] Only baseline tests will be run")
        args.baseline_only = True
    
    # Ensure output directory exists
    Path('output').mkdir(exist_ok=True)
    
    # Determine which intervals to test
    if args.test_intervals:
        test_intervals = [1, 5, 30]
    else:
        test_intervals = [1]  # Default: only 1 second
    
    # Run baseline tests for each interval
    interval_results = []
    
    for interval in test_intervals:
        print(f"\n{'='*60}")
        print(f"RUNNING BASELINE TESTS (Interval: {interval}s)")
        print(f"{'='*60}")
        
        baseline_results = []
        for i in range(1, args.runs + 1):
            result = run_baseline_test(i, args.duration, interval)
            baseline_results.append(result)
        
        print_summary_table(f"Baseline (Interval: {interval}s)", baseline_results)
        
        # Store results with interval info
        valid_results = [r for r in baseline_results if r is not None]
        if valid_results:
            interval_results.append({
                'interval': interval,
                'runs': len(valid_results),
                'statistics': {
                    'bytes_per_report': calculate_statistics(valid_results, 'bytes_per_report'),
                    'packets_received': calculate_statistics(valid_results, 'packets_received'),
                    'duplicate_rate': calculate_statistics(valid_results, 'duplicate_rate'),
                    'sequence_gap_count': calculate_statistics(valid_results, 'sequence_gap_count')
                }
            })
    
    # Determine which loss rates to test
    if args.test_loss_rates:
        test_loss_rates = [0, 1, 5, 10]
    else:
        test_loss_rates = [5]  # Default: only 5%
    
    # Run loss tests (Linux only) for each loss rate
    loss_rate_results = []
    if not args.baseline_only:
        for loss_pct in test_loss_rates:
            print(f"\n{'='*60}")
            print(f"RUNNING PACKET LOSS TESTS (Loss: {loss_pct}%)")
            print(f"{'='*60}")
            
            loss_results = []
            for i in range(1, args.runs + 1):
                result = run_loss_test(i, args.duration, loss_pct)
                loss_results.append(result)
            
            print_summary_table(f"Packet Loss ({loss_pct}%)", loss_results)
            
            # Store results with loss percentage info
            valid_results = [r for r in loss_results if r is not None]
            if valid_results:
                loss_rate_results.append({
                    'loss_percentage': loss_pct,
                    'runs': len(valid_results),
                    'statistics': {
                        'bytes_per_report': calculate_statistics(valid_results, 'bytes_per_report'),
                        'packets_received': calculate_statistics(valid_results, 'packets_received'),
                        'duplicate_rate': calculate_statistics(valid_results, 'duplicate_rate'),
                        'sequence_gap_count': calculate_statistics(valid_results, 'sequence_gap_count')
                    }
                })
    
    # Run delay tests (Linux only)
    delay_results = []
    if not args.baseline_only:
        print(f"\n{'='*60}")
        print("RUNNING DELAY/JITTER TESTS")
        print(f"{'='*60}")
        
        for i in range(1, args.runs + 1):
            result = run_delay_test(i, args.duration)
            delay_results.append(result)
        
        print_summary_table("Delay/Jitter", delay_results)
    
    # Aggregate results
    print(f"\n{'='*60}")
    print("AGGREGATING RESULTS")
    print(f"{'='*60}")
    
    aggregated_results = {
        'test_configuration': {
            'runs_per_scenario': args.runs,
            'duration_per_run': args.duration,
            'platform': platform.system(),
            'tested_intervals': test_intervals if args.test_intervals else [1],
            'tested_loss_rates': test_loss_rates if args.test_loss_rates and not args.baseline_only else []
        },
        'scenarios': {}
    }
    
    # Add interval test results for plotting
    if interval_results:
        aggregated_results['interval_tests'] = interval_results
    
    # Add loss rate test results for plotting
    if loss_rate_results:
        aggregated_results['loss_tests'] = loss_rate_results
    
    # Add delay statistics (for backward compatibility)
    if delay_results:
        valid_delay = [r for r in delay_results if r is not None]
        if valid_delay:
            aggregated_results['scenarios']['delay_jitter'] = {
                'runs': len(valid_delay),
                'statistics': {
                    'bytes_per_report': calculate_statistics(valid_delay, 'bytes_per_report'),
                    'packets_received': calculate_statistics(valid_delay, 'packets_received'),
                    'duplicate_rate': calculate_statistics(valid_delay, 'duplicate_rate'),
                    'sequence_gap_count': calculate_statistics(valid_delay, 'sequence_gap_count')
                }
            }
    
    # Add note about plotting
    if args.test_intervals or args.test_loss_rates:
        print("\n[INFO] Test data for plotting has been generated")
        print("[INFO] Run 'python scripts/generate_plots.py' to create visualizations")
    
    # Save aggregated results
    output_file = 'output/test_results.json'
    save_metrics_json(aggregated_results, output_file)
    
    print(f"\n{'='*60}")
    print("ALL TESTS COMPLETE")
    print(f"{'='*60}")
    print(f"Aggregated results saved to: {output_file}")


if __name__ == '__main__':
    main()
