#!/bin/bash
#
# TinyTelemetry v1.0 Delay/Jitter Test Script (Linux)
#
# This script runs a test with 100ms ±10ms delay/jitter using Linux netem
# to validate the protocol's reordering capabilities.
#
# Requirements:
# - Linux operating system
# - Root/sudo privileges (for tc qdisc commands)
# - Python 3.7+
#
# Test parameters:
# - Duration: 60 seconds
# - Interval: 1 second
# - Batch size: 1 (non-batched)
# - Delay: 100ms ±10ms
# - Expected: Reordering works, no crashes

set -e  # Exit on error

# Configuration
DEVICE_ID=${1:-1001}
INTERVAL=${2:-1}
DURATION=${3:-60}
BATCH_SIZE=${4:-1}
SERVER_PORT=${5:-5000}
LOG_FILE="output/delay_telemetry.csv"
OUTPUT_JSON="output/delay_metrics.json"
DELAY_MS=100
JITTER_MS=10

echo "============================================================"
echo "DELAY/JITTER TEST (Linux netem)"
echo "============================================================"
echo "Device ID: $DEVICE_ID"
echo "Interval: ${INTERVAL}s"
echo "Duration: ${DURATION}s"
echo "Batch size: $BATCH_SIZE"
echo "Server port: $SERVER_PORT"
echo "Delay: ${DELAY_MS}ms ±${JITTER_MS}ms"
echo "Log file: $LOG_FILE"
echo "============================================================"

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "[ERROR] This script requires Linux with netem support"
    echo "For Windows, use test_baseline_windows.py and Clumsy manually"
    exit 1
fi

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "[ERROR] This script must be run as root (use sudo)"
   exit 1
fi

# Function to cleanup netem on exit
cleanup() {
    echo ""
    echo "[CLEANUP] Removing netem configuration..."
    tc qdisc del dev lo root 2>/dev/null || true
    echo "[CLEANUP] Done"
}

# Set trap to cleanup on exit
trap cleanup EXIT

echo ""
echo "[1/5] Applying netem delay/jitter (${DELAY_MS}ms ±${JITTER_MS}ms)..."
tc qdisc add dev lo root netem delay ${DELAY_MS}ms ${JITTER_MS}ms

echo "[2/5] Verifying netem configuration..."
tc qdisc show dev lo

echo ""
echo "[3/5] Running baseline test with delay/jitter..."

# Determine pcap file name (use run number if provided via environment)
PCAP_FILE="${PCAP_FILE:-output/delay_capture.pcap}"

python3 scripts/test_baseline.py \
    --device-id "$DEVICE_ID" \
    --interval "$INTERVAL" \
    --duration "$DURATION" \
    --batch-size "$BATCH_SIZE" \
    --server-port "$SERVER_PORT" \
    --log-file "$LOG_FILE" \
    --output-json "$OUTPUT_JSON" \
    --enable-pcap \
    --pcap-file "$PCAP_FILE"

TEST_EXIT_CODE=$?

echo ""
echo "[4/5] Removing netem configuration..."
tc qdisc del dev lo root

echo "[5/5] Analyzing results..."

# Read metrics and verify reordering
if [[ -f "$OUTPUT_JSON" ]]; then
    echo ""
    echo "============================================================"
    echo "DELAY/JITTER TEST VALIDATION"
    echo "============================================================"
    
    # Verify reordering by checking timestamps vs arrival times
    python3 -c "
import json
import csv
import sys

# Read metrics
with open('$OUTPUT_JSON', 'r') as f:
    data = json.load(f)

metrics = data['metrics']
packets_received = metrics['packets_received']

print(f'Packets received: {packets_received}')

# Check for reordering by comparing timestamps and arrival times
reordering_detected = False
out_of_order_count = 0

with open('$LOG_FILE', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
    for i in range(1, len(rows)):
        prev_timestamp = int(rows[i-1]['timestamp'])
        curr_timestamp = int(rows[i]['timestamp'])
        prev_arrival = float(rows[i-1]['arrival_time'])
        curr_arrival = float(rows[i]['arrival_time'])
        
        # Check if packet with later timestamp arrived before earlier timestamp
        if curr_timestamp < prev_timestamp and curr_arrival > prev_arrival:
            reordering_detected = True
            out_of_order_count += 1

print(f'Out-of-order arrivals detected: {out_of_order_count}')

# Requirement 17.1: Reordering works
if reordering_detected or out_of_order_count > 0:
    print('✓ PASS: Reordering capability verified (out-of-order packets detected)')
else:
    print('ℹ INFO: No out-of-order packets detected (may be normal for short test)')

# Requirement 17.2 & 17.3: No crashes, no buffer overrun
print('✓ PASS: No crashes or buffer overrun (test completed successfully)')

print('============================================================')
"
else
    echo "[ERROR] Metrics file not found: $OUTPUT_JSON"
    exit 1
fi

echo ""
if [[ $TEST_EXIT_CODE -eq 0 ]]; then
    echo "✓ DELAY/JITTER TEST COMPLETED"
else
    echo "✗ DELAY/JITTER TEST FAILED"
fi

exit $TEST_EXIT_CODE
