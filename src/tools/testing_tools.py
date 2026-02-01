"""
Testing Tools for Refactoring Swarm
Author: Toolsmith Team
Purpose: Run pytest and collect test results
"""
import subprocess
import re
from typing import Dict, List, Optional
from pathlib import Path

class TestingTools:
    """Tools for running and analyzing unit tests"""
    
    def __init__(self, sandbox_path: str = "./sandbox"):
        """
        Initialize testing tools
        
        Args:
            sandbox_path: Base directory for operations
        """
        self.sandbox_path = Path(sandbox_path).resolve()
        print(f"🧪 TestingTools initialized")
    @staticmethod
    def run_pytest(self, target_path: str, test_file: Optional[str] = None, 
                   timeout: int = 60, verbose: bool = True) -> Dict:
        """
        Run pytest on a file or directory
        
        Args:
            target_path: Directory containing code/tests
            test_file: Specific test file to run (optional)
            timeout: Maximum execution time in seconds
            verbose: Show detailed output
            
        Returns:
            Dictionary with test_results:
            {
                'passed': int,
                'failed': int,
                'skipped': int,
                'errors': int,
                'total': int,
                'duration': float,
                'failures': List[Dict],
                'success': bool,
                'output': str,
                'status': str
            }
        """
        print(f"🧪 Running pytest on: {test_file or target_path}")
        
        try:
            # Build pytest command
            cmd = ['pytest']
            
            if verbose:
                cmd.append('-v')
            else:
                cmd.append('-q')
            
            # Add traceback style
            cmd.extend(['--tb=short'])
            
            # Target to test
            if test_file:
                cmd.append(test_file)
            else:
                cmd.append(target_path)
            
            # Run pytest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.sandbox_path)
            )
            
            # Parse output
            test_results = self._parse_pytest_output(result.stdout, result.stderr)
            test_results['return_code'] = result.returncode
            test_results['success'] = result.returncode == 0
            test_results['status'] = 'success' if result.returncode == 0 else 'failed'
            
            # Log summary
            self._log_test_summary(test_results)
            
            return test_results
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Test execution timeout (>{timeout}s)")
            return self._error_result("timeout", f"Test execution timeout after {timeout}s")
        
        except FileNotFoundError:
            print("❌ Pytest not installed")
            return self._error_result("not_installed", "Pytest not found. Run: pip install pytest")
        
        except Exception as e:
            print(f"❌ Error running pytest: {e}")
            return self._error_result("error", str(e))
    
    def _parse_pytest_output(self, stdout: str, stderr: str) -> Dict:
        """
        Parse pytest output to extract results
        
        Args:
            stdout: Pytest standard output
            stderr: Pytest standard error
            
        Returns:
            Parsed results dictionary
        """
        result = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'total': 0,
            'duration': 0.0,
            'failures': [],
            'output': stdout + "\n" + stderr
        }
        
        combined_output = stdout + "\n" + stderr
        
        # Parse summary line (e.g., "5 passed, 2 failed in 1.23s")
        # Pattern: "X passed" or "X failed" or "X skipped"
        
        passed_match = re.search(r'(\d+) passed', combined_output)
        if passed_match:
            result['passed'] = int(passed_match.group(1))
        
        failed_match = re.search(r'(\d+) failed', combined_output)
        if failed_match:
            result['failed'] = int(failed_match.group(1))
        
        skipped_match = re.search(r'(\d+) skipped', combined_output)
        if skipped_match:
            result['skipped'] = int(skipped_match.group(1))
        
        error_match = re.search(r'(\d+) error', combined_output)
        if error_match:
            result['errors'] = int(error_match.group(1))
        
        # Extract duration (e.g., "in 1.23s" or "in 0.5 seconds")
        duration_match = re.search(r'in ([\d\.]+)\s*s', combined_output)
        if duration_match:
            result['duration'] = float(duration_match.group(1))
        
        # Calculate total
        result['total'] = result['passed'] + result['failed'] + result['skipped'] + result['errors']
        
        # Extract failure details
        result['failures'] = self._extract_failures(stdout)
        
        return result
    
    def _extract_failures(self, output: str) -> List[Dict]:
        """
        Extract detailed failure information from pytest output
        
        Args:
            output: Pytest output text
            
        Returns:
            List of failure dictionaries
        """
        failures = []
        lines = output.split('\n')
        
        current_test = None
        current_error = []
        in_failure_block = False
        
        for line in lines:
            # Detect start of failure block
            if 'FAILED' in line and '::' in line:
                # Save previous failure
                if current_test and current_error:
                    failures.append({
                        'test': current_test,
                        'error': '\n'.join(current_error).strip()
                    })
                
                # Start new failure
                current_test = line.split('FAILED')[1].strip()
                current_error = []
                in_failure_block = True
            
            # Collect error lines
            elif in_failure_block:
                if line.startswith('====') or line.startswith('____') or line.startswith('==='):
                    in_failure_block = False
                else:
                    current_error.append(line)
        
        # Add last failure
        if current_test and current_error:
            failures.append({
                'test': current_test,
                'error': '\n'.join(current_error).strip()
            })
        
        return failures
    
    def _log_test_summary(self, results: Dict) -> None:
        """Print test summary"""
        print(f"✅ Tests complete:")
        print(f"   Passed: {results['passed']}")
        print(f"   Failed: {results['failed']}")
        if results['skipped'] > 0:
            print(f"   Skipped: {results['skipped']}")
        if results['errors'] > 0:
            print(f"   Errors: {results['errors']}")
        print(f"   Duration: {results['duration']:.2f}s")
    
    def _error_result(self, status: str, error_msg: str) -> Dict:
        """
        Return error result structure
        
        Args:
            status: Status code
            error_msg: Error message
            
        Returns:
            Error result dictionary
        """
        return {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'total': 0,
            'duration': 0.0,
            'failures': [],
            'success': False,
            'output': error_msg,
            'status': status,
            'error': error_msg
        }
    
    def run_specific_test(self, test_file: str, test_function: str) -> Dict:
        """
        Run a specific test function
        
        Args:
            test_file: Path to test file
            test_function: Name of test function (e.g., 'test_addition')
            
        Returns:
            Test results dictionary
        """
        test_path = f"{test_file}::{test_function}"
        print(f"🎯 Running specific test: {test_function}")
        return self.run_pytest(target_path=test_path)
    
    def discover_tests(self, directory: str) -> List[str]:
        """
        Discover all test files in a directory
        
        Args:
            directory: Directory to search
            
        Returns:
            List of test file paths
        """
        test_files = set()
        
        # Pattern 1: test_*.py
        for file_path in Path(directory).rglob("test_*.py"):
            if self._should_test(file_path):
                test_files.add(str(file_path))
        
        # Pattern 2: *_test.py
        for file_path in Path(directory).rglob("*_test.py"):
            if self._should_test(file_path):
                test_files.add(str(file_path))
        
        result = sorted(test_files)
        print(f"🔍 Discovered {len(result)} test files")
        return result
    
    def _should_test(self, file_path: Path) -> bool:
        """Check if file should be tested"""
        exclude_patterns = ['__pycache__', '.venv', 'venv', '.git', 'node_modules']
        path_str = str(file_path)
        return not any(pattern in path_str for pattern in exclude_patterns)
    
    def validate_test_file(self, file_path: str) -> bool:
        """
        Check if a file is a valid test file
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file contains test functions or classes
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_test_functions = 'def test_' in content
                has_test_classes = 'class Test' in content
                has_pytest_import = 'pytest' in content or 'unittest' in content
                
                return has_test_functions or has_test_classes
        except Exception as e:
            print(f"⚠️ Error validating test file: {e}")
            return False
    
    def get_test_coverage(self, target_path: str) -> Dict:
        """
        Run tests with coverage analysis (requires pytest-cov)
        
        Args:
            target_path: Path to analyze
            
        Returns:
            Coverage information
        """
        print(f"📊 Running coverage analysis...")
        
        try:
            result = subprocess.run(
                ['pytest', '--cov=' + target_path, '--cov-report=json', target_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Try to read coverage.json
            coverage_file = Path('coverage.json')
            if coverage_file.exists():
                import json
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    return {
                        'status': 'success',
                        'coverage': coverage_data.get('totals', {}).get('percent_covered', 0),
                        'files': coverage_data.get('files', {})
                    }
            else:
                return {'status': 'no_coverage_file', 'coverage': 0}
                
        except FileNotFoundError:
            return {'status': 'pytest_cov_not_installed', 'coverage': 0}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'coverage': 0}
    
    def is_pytest_installed(self) -> bool:
        """Check if pytest is installed"""
        try:
            subprocess.run(['pytest', '--version'], capture_output=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def create_test_report(self, results: Dict) -> str:
        """
        Create a formatted test report
        
        Args:
            results: Test results dictionary
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("TEST REPORT")
        report.append("=" * 60)
        report.append(f"Status: {'✅ PASSED' if results['success'] else '❌ FAILED'}")
        report.append(f"Total Tests: {results['total']}")
        report.append(f"  • Passed: {results['passed']}")
        report.append(f"  • Failed: {results['failed']}")
        if results['skipped'] > 0:
            report.append(f"  • Skipped: {results['skipped']}")
        report.append(f"Duration: {results['duration']:.2f}s")
        
        if results['failures']:
            report.append("\n" + "=" * 60)
            report.append("FAILURES")
            report.append("=" * 60)
            for i, failure in enumerate(results['failures'], 1):
                report.append(f"\n{i}. {failure['test']}")
                report.append(f"   {failure['error'][:200]}...")  # First 200 chars
        
        report.append("=" * 60)
        return "\n".join(report)