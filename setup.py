#!/usr/bin/env python3
"""
AutoAnalytiX Setup Script

One-liner setup and execution script for AutoAnalytiX project.
Creates virtual environment, installs dependencies, and runs the analysis.

Usage:
    python setup.py

Alternative (if made executable):
    ./setup.py

This script will:
1. Create a virtual environment in the project folder  
2. Install all required dependencies
3. Run the AutoAnalytiX analysis
4. Display results summary

ONE-LINER COMMAND:
    python setup.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class AutoAnalytiXSetup:
    """Setup and execution manager for AutoAnalytiX project"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_name = "autoanalytix_venv"
        self.venv_path = self.project_root / self.venv_name
        self.requirements_file = self.project_root / "requirements.txt"
        self.main_script = self.project_root / "main.py"
        
        # Platform-specific settings
        self.is_windows = platform.system() == "Windows"
        self.python_executable = "python" if self.is_windows else "python3"
        self.pip_executable = "pip" if self.is_windows else "pip3"
        
        if self.is_windows:
            self.venv_python = self.venv_path / "Scripts" / "python.exe"
            self.venv_pip = self.venv_path / "Scripts" / "pip.exe"
            self.activate_script = self.venv_path / "Scripts" / "activate.bat"
        else:
            self.venv_python = self.venv_path / "bin" / "python"
            self.venv_pip = self.venv_path / "bin" / "pip"
            self.activate_script = self.venv_path / "bin" / "activate"

    def print_header(self):
        """Print setup header"""
        print("=" * 80)
        print("🚛 AutoAnalytiX .0 - Automated Setup & Execution")
        print("=" * 80)
        print(f"📁 Project Directory: {self.project_root}")
        print(f"🐍 Python Executable: {self.python_executable}")
        print(f"💻 Platform: {platform.system()}")
        print("=" * 80)

    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🔍 Checking Python version...")
        
        if sys.version_info < (3, 8):
            print("❌ ERROR: Python 3.8 or higher is required!")
            print(f"   Current version: {sys.version}")
            print("   Please upgrade Python and try again.")
            sys.exit(1)
        
        print(f"✅ Python version OK: {sys.version.split()[0]}")

    def check_required_files(self):
        """Check if required files exist"""
        print("🔍 Checking required files...")
        
        required_files = [
            self.requirements_file,
            self.main_script,
            self.project_root / "core" / "__init__.py",
            self.project_root / "shared" / "__init__.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            print("❌ ERROR: Missing required files:")
            for file in missing_files:
                print(f"   - {file}")
            print("   Please ensure all AutoAnalytiX files are present.")
            sys.exit(1)
        
        print("✅ All required files found")

    def create_virtual_environment(self):
        """Create virtual environment"""
        print(f"🔧 Creating virtual environment: {self.venv_name}")
        
        if self.venv_path.exists():
            print(f"⚠️  Virtual environment already exists at {self.venv_path}")
            response = input("   Do you want to recreate it? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                print("🗑️  Removing existing virtual environment...")
                import shutil
                shutil.rmtree(self.venv_path)
            else:
                print("📦 Using existing virtual environment")
                return True
        
        try:
            result = subprocess.run([
                self.python_executable, "-m", "venv", str(self.venv_path)
            ], check=True, capture_output=True, text=True)
            
            print("✅ Virtual environment created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR: Failed to create virtual environment")
            print(f"   Command: {' '.join(e.cmd)}")
            print(f"   Error: {e.stderr}")
            return False

    def install_dependencies(self):
        """Install dependencies in virtual environment"""
        print("📦 Installing dependencies...")
        
        if not self.venv_pip.exists():
            print(f"❌ ERROR: Pip not found in virtual environment: {self.venv_pip}")
            return False
        
        try:
            # Upgrade pip first
            print("   Upgrading pip...")
            subprocess.run([
                str(self.venv_python), "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True, text=True)
            
            # Install requirements
            print("   Installing project dependencies...")
            result = subprocess.run([
                str(self.venv_pip), "install", "-r", str(self.requirements_file)
            ], check=True, capture_output=True, text=True)
            
            print("✅ Dependencies installed successfully")
            
            # Show installed packages
            print("📋 Installed packages:")
            result = subprocess.run([
                str(self.venv_pip), "list"
            ], capture_output=True, text=True)
            
            for line in result.stdout.split('\n')[:10]:  # Show first 10 packages
                if line.strip() and not line.startswith('-'):
                    print(f"   {line}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR: Failed to install dependencies")
            print(f"   Command: {' '.join(e.cmd)}")
            print(f"   Error: {e.stderr}")
            return False

    def check_data_directory(self):
        """Check if data directory exists and create if needed"""
        print("📂 Checking data directory...")
        
        data_dir = self.project_root / "data"
        if not data_dir.exists():
            print("📁 Creating data directory...")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a README for data directory
            readme_path = data_dir / "README.md"
            with open(readme_path, 'w') as f:
                f.write("# AutoAnalytiX Data Directory\n\n")
                f.write("Place your telemetry data files here:\n")
                f.write("- telemetry_1.csv\n")
                f.write("- telemetry_2.csv\n")
                f.write("- vehicle_data.csv\n\n")
                f.write("Or the system will look for Google Colab mounted drive.\n")
            
            print(f"✅ Data directory created: {data_dir}")
            print("   ℹ️  Place your CSV files in the data/ directory")
        else:
            print("✅ Data directory exists")

    def run_autoanalytix(self):
        """Run the AutoAnalytiX main application"""
        print("🚀 Running AutoAnalytiX Analysis...")
        print("=" * 60)
        
        try:
            # Change to project directory
            os.chdir(self.project_root)
            
            # Run the main script with the virtual environment Python
            result = subprocess.run([
                str(self.venv_python), str(self.main_script)
            ], cwd=str(self.project_root))
            
            print("=" * 60)
            
            if result.returncode == 0:
                print("✅ AutoAnalytiX analysis completed successfully!")
                print("📁 Check the AutoAnalytiX__Reports directory for results")
                return True
            else:
                print(f"❌ AutoAnalytiX analysis failed with exit code: {result.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: Failed to run AutoAnalytiX")
            print(f"   Error: {str(e)}")
            return False

    def print_results_summary(self):
        """Print summary of generated results"""
        print("\n" + "=" * 80)
        print("📊 AUTOANALYTIX RESULTS SUMMARY")
        print("=" * 80)
        
        reports_dir = self.project_root / "AutoAnalytiX__Reports"
        if reports_dir.exists():
            print(f"📁 Reports Directory: {reports_dir}")
            
            # Count files in different categories
            subdirs = [
                ("Plots", "📈"),
                ("Data_Exports", "📋"),
                ("Theft_Detection", "🚨"),
                ("Utilization_Analysis", "💰"),
                ("Logs", "📝")
            ]
            
            for subdir, icon in subdirs:
                subdir_path = reports_dir / subdir
                if subdir_path.exists():
                    file_count = len(list(subdir_path.rglob("*.*")))
                    print(f"{icon} {subdir}: {file_count} files")
            
            # Check for executive summary
            exec_summary = reports_dir / "Executive_Summary.txt"
            if exec_summary.exists():
                print(f"📋 Executive Summary: {exec_summary}")
            
        else:
            print("⚠️  Reports directory not found - analysis may have failed")
        
        print("=" * 80)

    def print_usage_instructions(self):
        """Print usage instructions"""
        print("\n🎯 NEXT STEPS:")
        print("-" * 40)
        print("1. 📁 Review results in AutoAnalytiX__Reports/")
        print("2. 📈 Check plots in AutoAnalytiX__Reports/Plots/")
        print("3. 📋 Read Executive_Summary.txt for key findings")
        print("4. 🚨 Review theft events in Theft_Detection/")
        print("5. 💰 Check utilization costs in Utilization_Analysis/")
        
        if self.is_windows:
            activate_cmd = f"{self.venv_path}\\Scripts\\activate"
        else:
            activate_cmd = f"source {self.venv_path}/bin/activate"
        
        print(f"\n🔧 To manually run in the future:")
        print(f"   {activate_cmd}")
        print(f"   python main.py")
        print(f"\n🚀 Or run the complete setup again:")
        print(f"   python setup.py")
        
        if not self.is_windows:
            print(f"\n💡 TIP: Make setup.py executable for even easier running:")
            print(f"   chmod +x setup.py")
            print(f"   ./setup.py")

    def run_setup(self):
        """Execute complete setup and run process"""
        try:
            self.print_header()
            self.check_python_version()
            self.check_required_files()
            
            if not self.create_virtual_environment():
                return False
            
            if not self.install_dependencies():
                return False
            
            self.check_data_directory()
            
            if not self.run_autoanalytix():
                return False
            
            self.print_results_summary()
            self.print_usage_instructions()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ SETUP FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point for setup script"""
    setup = AutoAnalytiXSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 AutoAnalytiX setup and execution completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 AutoAnalytiX setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()