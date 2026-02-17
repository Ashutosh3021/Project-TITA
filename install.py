#!/usr/bin/env python3
"""
JARVIS Project Setup Script
Creates virtual environment, installs dependencies, and sets up project structure.
"""

import os
import subprocess
import sys
import venv
from pathlib import Path


def print_step(step_num: int, message: str) -> None:
    """Print a formatted step message."""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {message}")
    print(f"{'='*60}\n")


def create_virtual_environment() -> None:
    """Create Python virtual environment."""
    venv_dir = Path("venv")
    
    if venv_dir.exists():
        print("Virtual environment already exists. Skipping creation.")
        return
    
    print("Creating virtual environment...")
    venv.create(venv_dir, with_pip=True)
    print(f"Virtual environment created at: {venv_dir.absolute()}")


def get_python_executable() -> str:
    """Get the Python executable path from venv."""
    if os.name == 'nt':  # Windows
        return str(Path("venv/Scripts/python.exe").absolute())
    else:  # Linux/Mac
        return str(Path("venv/bin/python").absolute())


def get_pip_executable() -> str:
    """Get the pip executable path from venv."""
    if os.name == 'nt':  # Windows
        return str(Path("venv/Scripts/pip.exe").absolute())
    else:  # Linux/Mac
        return str(Path("venv/bin/pip").absolute())


def install_requirements() -> None:
    """Install requirements from requirements.txt."""
    pip = get_pip_executable()
    
    print("Upgrading pip...")
    subprocess.run([pip, "install", "--upgrade", "pip"], check=True)
    
    print("Installing requirements (this may take a few minutes)...")
    subprocess.run([pip, "install", "-r", "requirements.txt"], check=True)
    print("Requirements installed successfully!")


def install_playwright() -> None:
    """Install Playwright browsers."""
    python = get_python_executable()
    
    print("Installing Playwright browsers...")
    subprocess.run([python, "-m", "playwright", "install"], check=True)
    print("Playwright browsers installed!")


def create_directories() -> None:
    """Create necessary project directories."""
    directories = [
        "data/chroma_db",
        "data/models",
        "data/logs",
        "JARVIS/core",
        "JARVIS/voice",
        "JARVIS/brain",
        "JARVIS/memory",
        "JARVIS/tools",
        "JARVIS/ui",
        "tests"
    ]
    
    print("Creating project directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}")
    
    # Create __init__.py files
    init_dirs = [
        "JARVIS",
        "JARVIS/core",
        "JARVIS/voice",
        "JARVIS/brain",
        "JARVIS/memory",
        "JARVIS/tools",
        "JARVIS/ui",
        "tests"
    ]
    
    print("\nCreating __init__.py files...")
    for directory in init_dirs:
        init_file = Path(directory) / "__init__.py"
        init_file.touch(exist_ok=True)
        print(f"  Created: {init_file}")


def copy_env_example() -> None:
    """Copy .env.example to .env if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print(".env file already exists. Skipping.")
        return
    
    if env_example.exists():
        print("Creating .env from .env.example...")
        env_file.write_text(env_example.read_text())
        print(".env file created. Please update it with your credentials.")
    else:
        print("Warning: .env.example not found. Please create .env manually.")


def print_success() -> None:
    """Print success message with next steps."""
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nJARVIS project has been successfully set up!")
    print("\nNext steps:")
    print("  1. Update .env file with your API credentials")
    print("  2. Install and start Ollama (https://ollama.com)")
    print("  3. Download required models (run: python download_models.py)")
    print("  4. Start the assistant (run: python -m JARVIS.main)")
    print("\nDirectory structure:")
    print("  JARVIS/       - Core assistant modules")
    print("  data/         - Database, models, and logs")
    print("  tests/        - Unit tests")
    print("\nTo activate the virtual environment:")
    if os.name == 'nt':
        print("  venv\\Scripts\\activate")
    else:
        print("  source venv/bin/activate")
    print("="*60 + "\n")


def main() -> None:
    """Main setup function."""
    print_step(0, "JARVIS Project Setup")
    
    try:
        create_virtual_environment()
        install_requirements()
        install_playwright()
        create_directories()
        copy_env_example()
        print_success()
    except subprocess.CalledProcessError as e:
        print(f"\nError during setup: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
