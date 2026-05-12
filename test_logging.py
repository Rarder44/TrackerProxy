#!/usr/bin/env python3
"""
Test script per verificare il logging del TrackerProxy
Esegui questo script per vedere come funziona il nuovo sistema di logging
"""

import sys
import logging
from logging_config import setup_logging

# Setup logging
logger = setup_logging(log_level=logging.DEBUG)

# Test logging output
print("\n" + "="*80)
print("TEST LOGGING SYSTEM")
print("="*80 + "\n")

logger.info("[TEST] Starting logging test...")
logger.debug("[TEST] This is a DEBUG message")
logger.info("[TEST] This is an INFO message")
logger.warning("[TEST] This is a WARNING message")
logger.error("[TEST] This is an ERROR message")

print("\nLog messages have been written to:")
print("  - Console (above)")
print("  - logs/tracker_proxy.log (all levels)")
print("  - logs/tracker_proxy_errors.log (errors only)")
print("\nCheck the LOGGING_GUIDE.md file for detailed documentation.\n")

logger.info("[TEST] Logging test completed")
print("="*80)
