"""
Example script demonstrating how to use the metrics module.

This script shows how to:
1. Calculate metrics from a CSV log file
2. Perform statistical analysis on multiple runs
3. Save results to JSON
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from metrics import MetricsCalculator, StatisticalAnalyzer, save_metrics_json


def analyze_single_run(csv_file: str):
    """Analyze a single test run."""
    print(f"Analyzing: {csv_file}")
    
    calculator = MetricsCalculator()
    result = calculator.calculate_from_csv(csv_file)
    
    print(f"  Bytes per report: {result.bytes_per_report:.2f}")
    print(f"  Packets received: {result.packets_received}")
    print(f"  Duplicate rate: {result.duplicate_rate:.4f}")
    print(f"  Sequence gaps: {result.sequence_gap_count}")
    
    return result


def analyze_multiple_runs(csv_files: list, output_file: str):
    """Analyze multiple test runs and calculate statistics."""
    print(f"\nAnalyzing {len(csv_files)} runs...")
    
    calculator = MetricsCalculator()
    analyzer = StatisticalAnalyzer()
    
    # Collect metrics from all runs
    bytes_per_report_values = []
    duplicate_rate_values = []
    
    for csv_file in csv_files:
        result = calculator.calculate_from_csv(csv_file)
        bytes_per_report_values.append(result.bytes_per_report)
        duplicate_rate_values.append(result.duplicate_rate)
    
    # Calculate statistics
    bytes_stats = analyzer.calculate_statistics(bytes_per_report_values)
    dup_stats = analyzer.calculate_statistics(duplicate_rate_values)
    
    # Get median run for detailed metrics
    median_result = calculator.calculate_from_csv(csv_files[len(csv_files) // 2])
    
    # Prepare output data
    metrics_data = {
        'test_scenario': 'example',
        'duration_seconds': 60,
        'reporting_interval': 1,
        'batch_size': 1,
        'num_runs': len(csv_files),
        'metrics': {
            'bytes_per_report': median_result.bytes_per_report,
            'packets_received': median_result.packets_received,
            'packets_sent': median_result.packets_sent,
            'duplicate_rate': median_result.duplicate_rate,
            'sequence_gap_count': median_result.sequence_gap_count
        },
        'statistics': {
            'bytes_per_report': bytes_stats,
            'duplicate_rate': dup_stats
        }
    }
    
    # Save to JSON
    save_metrics_json(metrics_data, output_file)
    
    print(f"\nStatistics:")
    print(f"  Bytes per report: min={bytes_stats['min']:.2f}, "
          f"median={bytes_stats['median']:.2f}, max={bytes_stats['max']:.2f}")
    print(f"  Duplicate rate: min={dup_stats['min']:.4f}, "
          f"median={dup_stats['median']:.4f}, max={dup_stats['max']:.4f}")


if __name__ == '__main__':
    # Example usage
    print("Metrics Module Usage Example")
    print("=" * 60)
    
    # Check if CSV file provided
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        analyze_single_run(csv_file)
    else:
        print("Usage: python example_metrics_usage.py <csv_file>")
        print("\nExample:")
        print("  python scripts/example_metrics_usage.py output/telemetry.csv")
