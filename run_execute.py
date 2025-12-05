import subprocess
import sys

result = subprocess.run([sys.executable, "/Users/nicolaudev/hyperliquid-trading-bot/execute_final_actions.py"], capture_output=False)
sys.exit(result.returncode)
