#!/usr/bin/env python
"""
Installation script for NBA PrizePicks Predictor.
This script helps install all dependencies correctly, including handling
potential issues with lxml dependencies.
"""

import os
import sys
import subprocess
import platform


def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60)


def print_section(message):
    """Print a section header."""
    print(f"\n>> {message}")


def run_command(command):
    """Run a shell command and display its output."""
    print(f"Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def is_venv():
    """Check if running inside a virtual environment."""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )


def create_venv():
    """Create a virtual environment if not already in one."""
    if is_venv():
        print("Already running in a virtual environment.")
        return True
        
    print_section("Creating virtual environment")
    venv_dir = ".venv"
    
    if os.path.exists(venv_dir):
        print(f"Virtual environment directory '{venv_dir}' already exists.")
        return True
        
    return run_command([sys.executable, "-m", "venv", venv_dir])


def install_dependencies(with_scraper=True, with_tests=True):
    """Install package dependencies."""
    print_section("Installing basic dependencies")
    
    pip_command = [sys.executable, "-m", "pip", "install", "-e", "."]
    
    extras = []
    if with_scraper:
        extras.append("scraper")
    if with_tests:
        extras.append("tests")
        
    if extras:
        pip_command[4] = ".[" + ",".join(extras) + "]"
        
    return run_command(pip_command)


def fix_lxml_issues():
    """Fix issues with lxml dependencies if needed."""
    print_section("Checking for lxml issues")
    
    try:
        import lxml
        print("lxml is installed correctly.")
    except ImportError:
        print("Installing lxml...")
        if not run_command([sys.executable, "-m", "pip", "install", "lxml>=4.9.3"]):
            print("Failed to install lxml.")
            return False
            
    try:
        from lxml.html.clean import Cleaner
        print("lxml.html.clean is available.")
        return True
    except ImportError:
        print("lxml.html.clean module not found. Installing lxml_html_clean...")
        
        if not run_command([sys.executable, "-m", "pip", "install", "lxml_html_clean>=1.0.0"]):
            print("Failed to install lxml_html_clean. Web scraping may not work.")
            return False
            
    return True


def main():
    """Main installation function."""
    print_header("NBA PrizePicks Predictor Installer")
    
    # Get system information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # Create virtual environment if needed
    if not is_venv():
        if not create_venv():
            print("Failed to create virtual environment. Exiting.")
            return False
            
        # Print activation instructions
        print("\nVirtual environment created. Please activate it and run this script again:")
        if platform.system() == "Windows":
            print("    .venv\\Scripts\\activate")
        else:
            print("    source .venv/bin/activate")
        return True
        
    # Install dependencies
    if not install_dependencies():
        print("Failed to install main dependencies. Exiting.")
        return False
        
    # Fix potential lxml issues
    fix_lxml_issues()
    
    print_header("Installation Complete!")
    print("\nYou can now run the application with:")
    print("    python run.py")
    print("\nOr with live data (experimental):")
    print("    python run.py run --live")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 