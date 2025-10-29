#!/usr/bin/env python3
"""
TinyTelemetry v1.0 Plot Generator

This script generates visualizations from test results:
- Plot 1: bytes_per_report vs reporting_interval (line plot)
- Plot 2: duplicate_rate vs loss_percentage (line plot)

Plots are saved to the output/ directory as PNG files.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
except ImportError:
    print("[ERROR] matplotlib is required. Install with: pip install matplotlib")
    sys.exit(1)


def load_test_results(results_file: str) -> Dict[str, Any]:
    """
    Load test results from JSON file.
    
    Args:
        results_file: Path to test_results.json
        
    Returns:
        Dictionary with test results
    """
    results_path = Path(results_file)
    
    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_file}")
    
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    return data


def plot_bytes_vs_interval(data: Dict[str, Any], output_file: str):
    """
    Create plot of bytes_per_report vs reporting_interval.
    
    Args:
        data: Test results dictionary with interval-based scenarios
        output_file: Path to save PNG file
    """
    # Extract data for different intervals
    intervals = []
    bytes_median = []
    bytes_min = []
    bytes_max = []
    
    # Look for scenarios with different intervals
    if 'interval_tests' in data:
        for interval_data in data['interval_tests']:
            interval = interval_data.get('interval', 0)
            stats = interval_data.get('statistics', {}).get('bytes_per_report', {})
            
            if interval and stats:
                intervals.append(interval)
                bytes_median.append(stats.get('median', 0))
                bytes_min.append(stats.get('min', 0))
                bytes_max.append(stats.get('max', 0))
    
    if not intervals:
        print("[WARNING] No interval test data found for bytes_per_report plot")
        return
    
    # Create plot
    plt.figure(figsize=(10, 6))
    
    # Plot median line with error bars
    plt.plot(intervals, bytes_median, marker='o', linewidth=2, markersize=8, 
             label='Median', color='#2E86AB')
    
    # Add min/max as shaded region
    plt.fill_between(intervals, bytes_min, bytes_max, alpha=0.3, color='#2E86AB',
                     label='Min-Max Range')
    
    plt.xlabel('Reporting Interval (seconds)', fontsize=12)
    plt.ylabel('Bytes per Report', fontsize=12)
    plt.title('Protocol Efficiency: Bytes per Report vs Reporting Interval', 
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    
    # Set x-axis to show specific intervals
    plt.xticks(intervals)
    
    # Save plot
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Plot saved: {output_file}")


def plot_duplicate_rate_vs_loss(data: Dict[str, Any], output_file: str):
    """
    Create plot of duplicate_rate vs loss_percentage.
    
    Args:
        data: Test results dictionary with loss-based scenarios
        output_file: Path to save PNG file
    """
    # Extract data for different loss percentages
    loss_percentages = []
    dup_rate_median = []
    dup_rate_min = []
    dup_rate_max = []
    
    # Look for scenarios with different loss rates
    if 'loss_tests' in data:
        for loss_data in data['loss_tests']:
            loss_pct = loss_data.get('loss_percentage', 0)
            stats = loss_data.get('statistics', {}).get('duplicate_rate', {})
            
            if stats:
                loss_percentages.append(loss_pct)
                # Convert to percentage for display
                dup_rate_median.append(stats.get('median', 0) * 100)
                dup_rate_min.append(stats.get('min', 0) * 100)
                dup_rate_max.append(stats.get('max', 0) * 100)
    
    if not loss_percentages:
        print("[WARNING] No loss test data found for duplicate_rate plot")
        return
    
    # Create plot
    plt.figure(figsize=(10, 6))
    
    # Plot median line with error bars
    plt.plot(loss_percentages, dup_rate_median, marker='s', linewidth=2, 
             markersize=8, label='Median', color='#A23B72')
    
    # Add min/max as shaded region
    plt.fill_between(loss_percentages, dup_rate_min, dup_rate_max, 
                     alpha=0.3, color='#A23B72', label='Min-Max Range')
    
    plt.xlabel('Packet Loss Percentage (%)', fontsize=12)
    plt.ylabel('Duplicate Rate (%)', fontsize=12)
    plt.title('Duplicate Detection: Duplicate Rate vs Packet Loss', 
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    
    # Set x-axis to show specific loss percentages
    plt.xticks(loss_percentages)
    
    # Save plot
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Plot saved: {output_file}")


def main():
    """Main entry point for plot generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate plots from TinyTelemetry test results',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--results-file',
        type=str,
        default='output/test_results.json',
        help='Path to test results JSON file'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Directory to save plot PNG files'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("TINYTELEMETRY v1.0 - PLOT GENERATOR")
    print("="*60)
    
    # Load test results
    try:
        data = load_test_results(args.results_file)
        print(f"Loaded results from: {args.results_file}")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        print("\nPlease run tests first to generate data:")
        print("  python scripts/run_all_tests.py")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in results file: {e}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate plots
    print("\nGenerating plots...")
    
    # Plot 1: bytes_per_report vs reporting_interval
    plot1_file = output_dir / 'bytes_per_report_vs_interval.png'
    plot_bytes_vs_interval(data, str(plot1_file))
    
    # Plot 2: duplicate_rate vs loss_percentage
    plot2_file = output_dir / 'duplicate_rate_vs_loss.png'
    plot_duplicate_rate_vs_loss(data, str(plot2_file))
    
    print("\n" + "="*60)
    print("PLOT GENERATION COMPLETE")
    print("="*60)
    print(f"Plots saved to: {args.output_dir}/")


if __name__ == '__main__':
    main()
