#!/usr/bin/env python3
"""
Setup script for Hyperliquid Trading Bot

This script helps set up the development environment without requiring UV.
It can:
1. Create a virtual environment
2. Install dependencies
3. Run tests
4. Validate configuration
"""

import subprocess
import sys
import os
import venv
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command and report status"""
    if description:
        print(f"\n📌 {description}")
    print(f"   Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def create_venv():
    """Create a Python virtual environment"""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print(f"✅ Virtual environment already exists at {venv_path}")
        return True
    
    print(f"📦 Creating virtual environment at {venv_path}...")
    try:
        venv.create(venv_path, with_pip=True)
        print(f"✅ Virtual environment created")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def get_python_executable():
    """Get the Python executable from the virtual environment"""
    venv_path = Path(".venv")
    
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    return str(python_exe)


def get_pip_executable():
    """Get the pip executable from the virtual environment"""
    venv_path = Path(".venv")
    
    if sys.platform == "win32":
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        pip_exe = venv_path / "bin" / "pip"
    
    return str(pip_exe)


def install_dependencies():
    """Install project dependencies"""
    pip_exe = get_pip_executable()
    
    print("\n📦 Installing dependencies...")
    
    deps = [
        "hyperliquid-python-sdk>=0.17.0",
        "eth-account>=0.10.0",
        "pyyaml>=6.0",
        "typing-extensions>=4.0",
        "psutil>=7.0.0",
        "httpx>=0.28.1",
        "python-dotenv>=1.1.1",
        "websockets>=15.0.1",
        "pymongo>=4.15.4",
        "redis>=7.0.1",
        "fastapi>=0.121.2",
        "uvicorn>=0.38.0",
        "numpy>=2.0.2",
        "pandas>=2.3.3",
        "scikit-learn>=1.6.1",
        "joblib>=1.5.2",
        "pytest>=7.0",
        "pytest-asyncio>=0.21",
        "pytest-mock>=3.0",
    ]
    
    for dep in deps:
        print(f"   Installing {dep}...")
        if not run_command([pip_exe, "install", dep]):
            print(f"⚠️  Warning: Failed to install {dep}, continuing...")
    
    print("✅ Dependencies installed")
    return True


def run_tests():
    """Run pytest tests"""
    python_exe = get_python_executable()
    
    print("\n🧪 Running tests...")
    
    cmd = [python_exe, "-m", "pytest", "tests/", "-v"]
    return run_command(cmd, "Running pytest")


def validate_config():
    """Validate bot configuration"""
    python_exe = get_python_executable()
    
    print("\n✔️  Validating configuration...")
    
    cmd = [python_exe, "src/run_bot.py", "--validate"]
    return run_command(cmd, "Validating bot configuration")


def main():
    """Main setup flow"""
    print("=" * 60)
    print("🤖 Hyperliquid Trading Bot - Setup Script")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "venv":
            create_venv()
        elif command == "install":
            if not create_venv():
                sys.exit(1)
            if not install_dependencies():
                sys.exit(1)
        elif command == "test":
            if not run_tests():
                sys.exit(1)
        elif command == "validate":
            if not validate_config():
                sys.exit(1)
        elif command == "all":
            if not create_venv():
                sys.exit(1)
            if not install_dependencies():
                sys.exit(1)
            if not run_tests():
                sys.exit(1)
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
            sys.exit(1)
    else:
        print_usage()
        print("\n🚀 Running full setup (venv + install + test)...")
        if not create_venv():
            sys.exit(1)
        if not install_dependencies():
            sys.exit(1)
        if not run_tests():
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)


def print_usage():
    """Print usage information"""
    print("\nUsage: python3 setup_env.py [command]")
    print("\nCommands:")
    print("  venv      - Create virtual environment")
    print("  install   - Create venv and install dependencies")
    print("  test      - Run pytest tests")
    print("  validate  - Validate bot configuration")
    print("  all       - Run all steps (default)")
    print("\nExamples:")
    print("  python3 setup_env.py              # Full setup")
    print("  python3 setup_env.py venv         # Just create venv")
    print("  python3 setup_env.py install      # Create venv and install deps")
    print("  python3 setup_env.py test         # Run tests")


if __name__ == "__main__":
    main()
