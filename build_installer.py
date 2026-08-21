import os
import sys
import subprocess

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
    
    # Use project virtual environment python if available to avoid packing heavy global ML packages (torch, scipy, pandas)
    venv_candidates = [
        os.path.join(root_dir, ".venv", "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(root_dir, ".venv", "bin", "python"),
        os.path.join(root_dir, "venv", "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(root_dir, "venv", "bin", "python")
    ]
    py_exec = next((p for p in venv_candidates if os.path.exists(p)), sys.executable)
    
    excludes = [
        "torch", "tensorflow", "scipy", "pandas", "faiss", "faiss_cpu", 
        "onnxruntime", "pyarrow", "matplotlib", "tkinter", "lxml", 
        "PIL", "Pillow", "pdfminer", "pypdfium2", "docx"
    ]
    exclude_args = []
    for exc in excludes:
        exclude_args.extend(["--exclude-module", exc])
    
    cmd = [
        py_exec, "-m", "PyInstaller",
        "--onefile",
        "--name", binary_name,
        "--paths", src_dir,
        "--add-data", data_arg,
        "--collect-all", "crewai",
        "--collect-all", "crewai_tools",
        "--collect-all", "cryptography",
        "--collect-all", "pyjwt",
        "--collect-all", "textual",
        "--collect-all", "litellm",
        "--collect-all", "rich",
        "--collect-all", "setuptools",
        "--collect-all", "python_dotenv",
        "--collect-all", "langchain_google_genai",
        "--collect-all", "langchain_openai",
        "--collect-all", "pydantic",
        "--collect-all", "tiktoken",
        "--collect-all", "tiktoken_ext",
        "--hidden-import", "tiktoken_ext",
        "--hidden-import", "tiktoken_ext.openai_public",
        *exclude_args,
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
        if sys.platform == "darwin" and os.path.exists(out_file):
            print("Applying ad-hoc code signature for macOS compatibility...")
            subprocess.run(["codesign", "--force", "--deep", "--sign", "-", out_file])
    else:
        print("\n=== BUILD FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    build()
