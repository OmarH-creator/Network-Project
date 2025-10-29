#!/bin/bash
#
# TinyTelemetry v1.0 Packet Loss Test Script (Linux)
#
# This script runs a test with 5% packet loss using Linux netem to validate
# the protocol's loss tolerance and gap detection capabilities.
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
# - Packet loss: 5%
# - Expected: Gap detection works, duplicate_rate ≤1%

set -e  # Exit on error

# Configuration
DEVICE_ID=${1:-1001}
INTERVAL=${2:-1}
DURATION=${3:-60}
BATCH_SIZE=${4:-1}
SERVER_PORT=${5:-5000}
LOSS_PERCENT=${6:-5}
LOG_FILE="output/loss_telemetry.csv"
OUTPUT_JSON="output/loss_metrics.json"

echo "============================================================"
echo "PACKET LOSS TEST (Linux netem)"
echo "============================================================"
echo "Device ID: $DEVICE_ID"
echo "Interval: ${INTERVAL}s"
echo "Duration: ${DURATION}s"
echo "Batch size: $BATCH_SIZE"
echo "Server port: $SERVER_PORT"
echo "Packet loss: ${LOSS_PERCENT}%"
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
echo "[1/5] Applying netem packet loss (${LOSS_PERCENT}%)..."
tc qdisc add dev lo root netem loss ${LOSS_PERCENT}%

echo "[2/5] Verifying netem configuration..."
tc qdisc show dev lo

echo ""
echo "[3/5] Running baseline test with packet loss..."

# Determine pcap file name (use run number if provided via environment)
PCAP_FILE="${PCAP_FILE:-output/loss_capture.pcap}"

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

# Read metrics from JSON output
if [[ -f "$OUTPUT_JSON" ]]; then
    echo ""
    echo "============================================================"
    echo "LOSS TEST VALIDATION"
    echo "============================================================"
    
    # Extract metrics using Python
    python3 -c "
import json
import sys

with open('$OUTPUT_JSON', 'r') as f:
    data = json.load(f)

metrics = data['metrics']
gap_count = metrics['sequence_gap_count']
duplicate_rate = metrics['duplicate_rate']

print(f'Sequence gaps detected: {gap_count}')
print(f'Duplicate rate: {duplicate_rate:.4f} ({duplicate_rate*100:.2f}%)')

# Requirement 16.1: Gap detection works
if gap_count > 0:
    print('✓ PASS: Gap detection works (gaps detected)')
else:
    print('✗ FAIL: No gaps detected (expected some with 5% loss)')

# Requirement 16.3: Duplicate rate ≤1%
if duplicate_rate <= 0.01:
    print('✓ PASS: Duplicate rate ≤1%')
else:
    print(f'✗ FAIL: Duplicate rate {duplicate_rate*100:.2f}% > 1%')

print('============================================================')
"
else
    echo "[ERROR] Metrics file not found: $OUTPUT_JSON"
    exit 1
fi

echo ""
if [[ $TEST_EXIT_CODE -eq 0 ]]; then
    echo "✓ PACKET LOSS TEST COMPLETED"
else
    echo "✗ PACKET LOSS TEST FAILED"
fi

exit $TEST_EXIT_CODE
