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


VENV_DIR = Path(".venv")


def print_step(step_num: int, message: str) -> None:
    print("\n" + "=" * 60)
    print(f"STEP {step_num}: {message}")
    print("=" * 60 + "\n")


def create_virtual_environment() -> None:
    """Create Python virtual environment if it doesn't exist."""
    if VENV_DIR.exists():
        print("Virtual environment already exists. Skipping creation.")
        return

    print("Creating virtual environment...")
    venv.create(VENV_DIR, with_pip=True)
    print(f"Virtual environment created at: {VENV_DIR.absolute()}")


def get_python_executable() -> str:
    """Return venv python executable path."""
    if os.name == "nt":
        return str((VENV_DIR / "Scripts" / "python.exe").absolute())
    return str((VENV_DIR / "bin" / "python").absolute())


def install_requirements() -> None:
    """Upgrade pip and install requirements."""
    python = get_python_executable()

    print("Upgrading pip...")
    subprocess.run(
        [python, "-m", "pip", "install", "--upgrade", "pip"],
        check=True
    )

    print("Installing requirements (this may take a few minutes)...")
    subprocess.run(
        [python, "-m", "pip", "install", "-r", "requirements.txt"],
        check=True
    )

    print("Requirements installed successfully!")


def install_playwright() -> None:
    """Install Playwright browsers."""
    python = get_python_executable()

    print("Installing Playwright browsers...")
    subprocess.run(
        [python, "-m", "playwright", "install"],
        check=True
    )

    print("Playwright browsers installed!")


def create_directories() -> None:
    """Create project directories."""
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
    """Copy .env.example to .env if needed."""
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
        print("Warning: .env.example not found. Create .env manually.")


def print_success() -> None:
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Update .env file with your credentials")
    print("  2. Install and start Ollama")
    print("  3. Download required models (python download_models.py)")
    print("  4. Start assistant (python -m JARVIS.main)")
    print("\nTo activate the virtual environment:")

    if os.name == "nt":
        print("  .venv\\Scripts\\Activate.ps1")
    else:
        print("  source .venv/bin/activate")

    print("=" * 60 + "\n")


def main() -> None:
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
