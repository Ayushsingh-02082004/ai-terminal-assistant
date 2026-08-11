import os
import sys
import subprocess
import shutil

def build():
    print("=== BUILDING CLI-AGENT STANDALONE BINARY ===")
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    entrypoint = os.path.join(backend_dir, "run.py")
    config_dir = os.path.join(backend_dir, "src", "cli_agent", "config")
    
    # Path separator for PyInstaller --add-data (';' on Windows, ':' on Unix)
    sep = ";" if sys.platform == "win32" else ":"
    data_arg = f"{config_dir}{sep}cli_agent/config"
    
    binary_name = "cli-agent"
    
    src_dir = os.path.join(backend_dir, "src")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", binary_name,
        "--paths", src_dir,
        "--add-data", data_arg,
        "--clean",
        entrypoint
    ]
    
    print(f"Running build command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=root_dir)
    
    if result.returncode == 0:
        print("\n=== BUILD SUCCESSFUL ===")
        dist_dir = os.path.join(root_dir, "dist")
        ext = ".exe" if sys.platform == "win32" else ""
        out_file = os.path.join(dist_dir, f"{binary_name}{ext}")
        print(f"Standalone executable created at: {out_file}")
    else:
        print("\n=== BUILD FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    build()
