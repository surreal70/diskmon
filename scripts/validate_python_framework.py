#!/usr/bin/env python3
"""
Python Development Framework Validation Script

Engineered by Andreas Huemmer [andreas.huemmer@adminsend.de]
Copyright (C) 2025 Andreas Huemmer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Version: 1.0.0
Last Modified: 2025-12-22

Changelog:
- 2025-12-22 v1.0.0: Initial framework validation implementation
  * Python version validation (3.8+ requirement)
  * Project structure validation
  * Non-Python file detection and warnings
  * Virtual environment detection
  * Dependency management validation

This script validates that the Python development framework requirements are met.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional


class PythonFrameworkValidator:
    """Validates Python development framework requirements."""
    
    # Non-Python file extensions that should trigger warnings
    NON_PYTHON_EXTENSIONS = {
        '.cpp', '.h', '.hpp', '.c',  # C/C++
        '.java',  # Java
        '.js', '.ts',  # JavaScript/TypeScript
        '.go',  # Go
        '.rs',  # Rust
        '.cs',  # C#
        '.rb',  # Ruby
        '.php',  # PHP
        '.swift',  # Swift
        '.kt',  # Kotlin
        '.scala',  # Scala
        '.clj',  # Clojure
        '.hs',  # Haskell
        '.ml',  # OCaml
        '.r',  # R
        '.m',  # Objective-C/MATLAB
        '.pl',  # Perl
        '.sh', '.bash'  # Shell scripts
    }
    
    def __init__(self, project_root: str = "."):
        """Initialize validator with project root directory."""
        self.project_root = Path(project_root).resolve()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_python_version(self) -> bool:
        """Validate Python version is 3.8 or higher."""
        print("🐍 Validating Python version...")
        
        if sys.version_info < (3, 8):
            self.errors.append(
                f"Python 3.8+ required, got {sys.version_info.major}.{sys.version_info.minor}"
            )
            return False
            
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
        return True
        
    def detect_non_python_files(self) -> List[Tuple[str, str]]:
        """Detect non-Python source files in the project."""
        print("🔍 Scanning for non-Python source files...")
        
        non_python_files = []
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.NON_PYTHON_EXTENSIONS:
                # Skip files in common ignore directories
                if any(part in ['.git', '__pycache__', '.venv', 'venv', 'node_modules'] 
                       for part in file_path.parts):
                    continue
                    
                language = self._detect_language(file_path.suffix)
                non_python_files.append((str(file_path.relative_to(self.project_root)), language))
                
        return non_python_files
        
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            '.cpp': 'C++', '.h': 'C/C++', '.hpp': 'C++', '.c': 'C',
            '.java': 'Java',
            '.js': 'JavaScript', '.ts': 'TypeScript',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.clj': 'Clojure',
            '.hs': 'Haskell',
            '.ml': 'OCaml',
            '.r': 'R',
            '.m': 'Objective-C/MATLAB',
            '.pl': 'Perl',
            '.sh': 'Shell Script', '.bash': 'Bash Script'
        }
        return language_map.get(extension, 'Unknown')
        
    def validate_project_structure(self) -> bool:
        """Validate standardized project structure."""
        print("📁 Validating project structure...")
        
        required_files = [
            'requirements.txt',
            'pyproject.toml',
            'README.md',
            'LICENSE'
        ]
        
        required_dirs = [
            'tests'
        ]
        
        success = True
        
        # Check required files
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                self.errors.append(f"Missing required file: {file_name}")
                success = False
            else:
                print(f"✅ {file_name} - Found")
                
        # Check required directories
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                self.errors.append(f"Missing required directory: {dir_name}")
                success = False
            else:
                print(f"✅ {dir_name}/ - Found")
                
        # Check for Python package
        python_packages = list(self.project_root.glob("*/__init__.py"))
        if not python_packages:
            self.errors.append("No Python package found (missing __init__.py)")
            success = False
        else:
            package_name = python_packages[0].parent.name
            print(f"✅ Python package '{package_name}' - Found")
            
        return success
        
    def validate_virtual_environment(self) -> bool:
        """Check if virtual environment is available or recommended."""
        print("🔧 Checking virtual environment...")
        
        # Check if we're in a virtual environment
        in_venv = (
            hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        if in_venv:
            print("✅ Running in virtual environment")
            return True
        else:
            # Check if venv directory exists
            venv_paths = [
                self.project_root / 'venv',
                self.project_root / '.venv'
            ]
            
            venv_exists = any(path.exists() for path in venv_paths)
            
            if venv_exists:
                self.warnings.append(
                    "Virtual environment exists but not activated. "
                    "Run: source venv/bin/activate"
                )
                print("⚠️  Virtual environment exists but not activated")
            else:
                self.warnings.append(
                    "No virtual environment found. "
                    "Create one with: python -m venv venv"
                )
                print("⚠️  No virtual environment found")
                
            return False
            
    def validate_dependencies(self) -> bool:
        """Validate dependency management setup."""
        print("📦 Validating dependency management...")
        
        success = True
        
        # Check requirements.txt
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            print("✅ requirements.txt - Found")
            try:
                with open(req_file, 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    print(f"   📋 {len(deps)} dependencies listed")
            except Exception as e:
                self.warnings.append(f"Could not read requirements.txt: {e}")
        else:
            self.errors.append("Missing requirements.txt")
            success = False
            
        # Check pyproject.toml
        pyproject_file = self.project_root / 'pyproject.toml'
        if pyproject_file.exists():
            print("✅ pyproject.toml - Found")
        else:
            self.warnings.append("Missing pyproject.toml (recommended for modern Python projects)")
            
        return success
        
    def validate_code_quality_tools(self) -> bool:
        """Validate code quality tools configuration."""
        print("🔍 Checking code quality tools...")
        
        tools_config = {
            '.flake8': 'Flake8 linting',
            'tox.ini': 'Tox testing',
            '.pre-commit-config.yaml': 'Pre-commit hooks'
        }
        
        found_tools = 0
        for config_file, description in tools_config.items():
            if (self.project_root / config_file).exists():
                print(f"✅ {description} - Configured")
                found_tools += 1
            else:
                print(f"⚠️  {description} - Not configured")
                
        if found_tools == 0:
            self.warnings.append("No code quality tools configured")
            
        return found_tools > 0
        
    def run_validation(self) -> bool:
        """Run complete validation suite."""
        print("🚀 Starting Python Development Framework Validation")
        print("=" * 60)
        
        # Run all validations
        validations = [
            self.validate_python_version(),
            self.validate_project_structure(),
            self.validate_dependencies()
        ]
        
        # Additional checks that don't fail validation
        self.validate_virtual_environment()
        self.validate_code_quality_tools()
        
        # Check for non-Python files
        non_python_files = self.detect_non_python_files()
        if non_python_files:
            print("\n⚠️  Non-Python source files detected:")
            for file_path, language in non_python_files:
                print(f"   {file_path} ({language})")
            self.warnings.append(
                f"Found {len(non_python_files)} non-Python source files. "
                "Consider using language-specific frameworks for these files."
            )
            
        # Print results
        print("\n" + "=" * 60)
        print("📊 Validation Results")
        print("=" * 60)
        
        if all(validations):
            print("✅ All critical validations passed!")
        else:
            print("❌ Some critical validations failed!")
            
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
                
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
                
        return all(validations) and not self.errors


def main():
    """Main entry point for validation script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate Python Development Framework requirements"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    validator = PythonFrameworkValidator(args.project_root)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()