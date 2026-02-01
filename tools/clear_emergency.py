#!/usr/bin/env python3
"""
Emergency Stop Clearance Tool
Requires token authentication via CLEAR_EMERGENCY_HASH environment variable.
"""
import os
import sys
import argparse
import hashlib
from pathlib import Path
import json
from datetime import datetime, timezone

STATE_FILE = Path("data/state.json")
ENV_HASH = os.getenv("CLEAR_EMERGENCY_HASH")  # expected SHA256 hex digest

def sha256_hex(s: str) -> str:
    """Compute SHA256 hex digest of string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_state(path=STATE_FILE):
    """Load state from JSON file."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state, path=STATE_FILE):
    """Save state atomically with fsync."""
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def main():
    parser = argparse.ArgumentParser(
        description="Clear emergency_stop flag with token authentication"
    )
    parser.add_argument(
        "--confirm", 
        required=True, 
        help="Clear emergency token (obtain from ops lead)"
    )
    args = parser.parse_args()

    # Check environment variable is set
    if ENV_HASH is None:
        print("❌ ERROR: CLEAR_EMERGENCY_HASH not set in environment.", file=sys.stderr)
        print("   Contact your operations lead to set this environment variable.", file=sys.stderr)
        print("   Example: export CLEAR_EMERGENCY_HASH=$(echo -n 'token' | sha256sum | awk '{print $1}')", file=sys.stderr)
        sys.exit(2)

    # Verify token
    provided_hash = sha256_hex(args.confirm)
    if provided_hash != ENV_HASH:
        print("❌ ERROR: Invalid token. Emergency stop NOT cleared.", file=sys.stderr)
        print("   The provided token does not match the expected hash.", file=sys.stderr)
        sys.exit(3)

    # Load state
    try:
        state = load_state()
    except Exception as e:
        print(f"❌ ERROR: Failed to load state file: {e}", file=sys.stderr)
        sys.exit(4)

    # Check if emergency stop is set
    if not state.get("emergency_stop", False):
        print("ℹ️  Emergency stop is not currently set. Nothing to clear.")
        sys.exit(0)

    # Clear emergency stop
    state["emergency_stop"] = False
    
    # Add audit trail
    state.setdefault("audit", []).append({
        "action": "clear_emergency",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": "cli",
        "tool": "clear_emergency.py",
        "user": os.getenv("USER", "unknown")
    })
    
    # Save state
    try:
        save_state(state)
    except Exception as e:
        print(f"❌ ERROR: Failed to save state: {e}", file=sys.stderr)
        sys.exit(5)

    # Success
    print("✅ Emergency stop has been CLEARED.")
    print(f"   Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"   User: {os.getenv('USER', 'unknown')}")
    print("   Trading may resume on next cycle.")

if __name__ == "__main__":
    main()
