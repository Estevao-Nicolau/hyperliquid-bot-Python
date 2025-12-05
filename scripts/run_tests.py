#!/usr/bin/env python3
"""
Direct test runner - bypasses UV issues
Runs tests directly using Python
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run command and show output"""
    if description:
        print(f"\n{'='*60}")
        print(f"📌 {description}")
        print(f"{'='*60}")
    
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, cwd="/Users/nicolaudev/hyperliquid-trading-bot")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("🧪 Direct Test Runner")
    print("="*60)
    
    os.chdir("/Users/nicolaudev/hyperliquid-trading-bot")
    
    print("\n1️⃣  Checking Python...")
    run_command([sys.executable, "--version"], "Python Version")
    
    print("\n2️⃣  Installing pytest if needed...")
    run_command([sys.executable, "-m", "pip", "install", "-q", "pytest", "pytest-asyncio", "pytest-mock"], "Installing Test Dependencies")
    
    print("\n3️⃣  Verifying pytest...")
    run_command([sys.executable, "-m", "pytest", "--version"], "Pytest Version")
    
    print("\n4️⃣  Running configuration tests...")
    success = run_command(
        [sys.executable, "-m", "pytest", "tests/test_enhanced_config.py", "-v", "--tb=short"],
        "Configuration Validation Tests"
    )
    
    if success:
        print("\n5️⃣  Running precision tests...")
        run_command(
            [sys.executable, "-m", "pytest", "tests/test_hl_adapter_precision.py", "-v", "--tb=short"],
            "Precision & Tick Size Tests"
        )
    
    print("\n6️⃣  Running all tests with summary...")
    run_command(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        "All Tests Summary"
    )
    
    print("\n" + "="*60)
    print("✅ Test run complete!")
    print("="*60)

if __name__ == "__main__":
    main()
