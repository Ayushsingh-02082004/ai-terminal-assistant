import sys
import os

# Add src directory to the path so python can locate cli_agent package
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from cli_agent.main import run_cli

if __name__ == "__main__":
    run_cli()
