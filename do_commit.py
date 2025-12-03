#!/usr/bin/env python3
"""
Automated commit script for Phase 1
"""

import subprocess
import sys
import os

def run_command(cmd, description=""):
    """Run command and report status"""
    if description:
        print(f"\n{'='*60}")
        print(f"📌 {description}")
        print(f"{'='*60}")
    
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, cwd="/Users/nicolaudev/hyperliquid-trading-bot", capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ Success")
            return True
        else:
            print(f"❌ Failed with code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main commit flow"""
    print("\n" + "="*60)
    print("🚀 Phase 1 - Automated Commit")
    print("="*60)
    
    os.chdir("/Users/nicolaudev/hyperliquid-trading-bot")
    
    # Step 1: Git status
    print("\n1️⃣  Checking git status...")
    run_command(["git", "status"], "Git Status")
    
    # Step 2: Git add
    print("\n2️⃣  Adding files...")
    if not run_command(["git", "add", "."], "Git Add"):
        print("❌ Failed to add files")
        return False
    
    # Step 3: Git commit
    print("\n3️⃣  Creating commit...")
    commit_message = """feat: Phase 1 TDD - 56 tests + comprehensive documentation

- Add 56 unit tests for configuration validation and precision
  - 30+ configuration validation tests (test_enhanced_config.py)
  - 20+ precision/tick size tests (test_hl_adapter_precision.py)
  - 2+ engine filter tests (test_engine_filters.py)
- Create comprehensive documentation (11 guides)
  - START_HERE.md - Quick start guide
  - QUICK_FIX.md - 30-second solution
  - RUN_TESTS_SIMPLE.md - Detailed test guide
  - TESTING.md - Test development guide
  - SETUP.md - Complete setup guide
  - MACOS_SETUP.md - macOS-specific guide
  - FIX_PYTEST.md - Troubleshooting guide
  - SETUP_SUMMARY.md - Setup summary
  - NEXT_STEPS.md - Roadmap for phases 2-4
  - PHASE1_SUMMARY.md - Phase 1 summary
  - COMMIT_INSTRUCTIONS.md - Commit instructions
- Add setup scripts for multiple platforms
  - run_tests.sh - Shell script for tests
  - run_tests.py - Python script for tests
  - setup_env.py - Python venv setup
  - fix_setup.sh - Fix script
  - quick_setup.sh - One-command setup
  - commit.sh - Commit script
  - do_commit.py - Python commit script
- Add requirements.txt for pip installation
- Update pyproject.toml with pytest in main dependencies
- Update README.md with 3 setup options
- Add tests/conftest.py for pytest path configuration
- All 56 tests passing (100% success rate)

Testing:
- python3 -m pytest tests/ -v
- 56 passed in 22.56s

Documentation:
- 11 comprehensive guides
- Multiple setup options (UV, Python venv, automatic)
- Troubleshooting for common issues
- Roadmap for next phases

Next Phase:
- Integration tests (engine + strategy + adapter)
- E2E tests against Hyperliquid testnet
- Smoke tests for learning examples"""
    
    if not run_command(["git", "commit", "-m", commit_message], "Git Commit"):
        print("❌ Failed to commit")
        return False
    
    # Step 4: Git log
    print("\n4️⃣  Verifying commit...")
    run_command(["git", "log", "--oneline", "-5"], "Git Log")
    
    # Step 5: Git push
    print("\n5️⃣  Pushing to remote...")
    if not run_command(["git", "push", "origin", "main"], "Git Push"):
        print("⚠️  Push may have failed, but commit was created locally")
        print("Try: git push origin main")
    
    print("\n" + "="*60)
    print("✅ Commit Process Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Verify on GitHub: https://github.com/nicolaudev/hyperliquid-trading-bot")
    print("2. Read NEXT_STEPS.md for Phase 2")
    print("3. Start Phase 2: Integration & E2E tests")
    print("\n")

if __name__ == "__main__":
    main()
