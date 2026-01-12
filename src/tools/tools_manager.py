"""
Tools Manager - Unified Interface
Author: Toolsmith Team
Purpose: Single entry point for all tools
"""
from pathlib import Path
from typing import Dict, List, Optional

from .file_tools import FileTools, SecurityError
from .analysis_tools import AnalysisTools
from .testing_tools import TestingTools

class ToolsManager:
    """
    Unified interface for all toolsmith operations
    Provides a single point of access for agents
    """
    
    def __init__(self, sandbox_path: str = "./sandbox"):
        """
        Initialize all tools
        
        Args:
            sandbox_path: Base directory for safe operations
        """
        self.sandbox_path = Path(sandbox_path).resolve()
        
        # Initialize individual tool classes
        self.files = FileTools(sandbox_path)
        self.analysis = AnalysisTools(sandbox_path)
        self.testing = TestingTools(sandbox_path)
        
        print(f"🛠️ ToolsManager initialized with sandbox: {self.sandbox_path}")
    
    # ============ FILE OPERATIONS ============
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read a file safely"""
        return self.files.read_file(file_path)
    
    def write_file(self, file_path: str, content: str) -> bool:
        """Write to a file safely"""
        return self.files.write_file(file_path, content)
    
    def list_python_files(self, directory: str) -> List[str]:
        """List all Python files in directory"""
        return self.files.list_python_files(directory)
    
    def backup_file(self, file_path: str) -> Optional[str]:
        """Create backup before modification"""
        return self.files.backup_file(file_path)
    
    def restore_backup(self, backup_path: str, original_path: str) -> bool:
        """Restore from backup"""
        return self.files.restore_backup(backup_path, original_path)
    
    # ============ CODE ANALYSIS ============
    
    def analyze_file(self, file_path: str) -> Dict:
        """Run pylint analysis on a single file"""
        return self.analysis.run_pylint(file_path)
    
    def analyze_directory(self, directory: str) -> Dict[str, Dict]:
        """Analyze all Python files in directory"""
        return self.analysis.analyze_directory(directory)
    
    def get_analysis_summary(self, analysis_results: Dict[str, Dict]) -> Dict:
        """Get summary of analysis results"""
        return self.analysis.get_summary(analysis_results)
    
    def compare_scores(self, before: Dict, after: Dict) -> Dict:
        """Compare before/after analysis"""
        return self.analysis.compare_scores(before, after)
    
    # ============ TESTING ============
    
    def run_tests(self, target_path: str, test_file: Optional[str] = None) -> Dict:
        """Run pytest on target"""
        return self.testing.run_pytest(target_path, test_file)
    
    def discover_tests(self, directory: str) -> List[str]:
        """Find all test files"""
        return self.testing.discover_tests(directory)
    
    def validate_test_file(self, file_path: str) -> bool:
        """Check if file is a valid test"""
        return self.testing.validate_test_file(file_path)
    
    def create_test_report(self, test_results: Dict) -> str:
        """Generate formatted test report"""
        return self.testing.create_test_report(test_results)
    
    # ============ WORKFLOW HELPERS ============
    
    def full_analysis_workflow(self, directory: str) -> Dict:
        """
        Complete analysis workflow for a directory
        
        Args:
            directory: Directory to analyze
            
        Returns:
            Complete analysis results
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting Full Analysis Workflow")
        print(f"{'='*60}\n")
        
        # Step 1: List files
        python_files = self.list_python_files(directory)
        print(f"📂 Found {len(python_files)} Python files\n")
        
        # Step 2: Run analysis
        analysis_results = self.analyze_directory(directory)
        
        # Step 3: Get summary
        summary = self.get_analysis_summary(analysis_results)
        
        # Step 4: Discover tests
        test_files = self.discover_tests(directory)
        print(f"\n🧪 Found {len(test_files)} test files")
        
        # Step 5: Run tests if available
        test_results = None
        if test_files:
            test_results = self.run_tests(directory)
        
        return {
            'files': python_files,
            'analysis': analysis_results,
            'summary': summary,
            'test_files': test_files,
            'test_results': test_results
        }
    
    def refactoring_cycle(self, file_path: str, fixed_content: str) -> Dict:
        """
        Execute one refactoring cycle: backup -> write -> analyze
        
        Args:
            file_path: File to refactor
            fixed_content: New content
            
        Returns:
            Results of the cycle
        """
        print(f"\n🔄 Starting Refactoring Cycle for: {Path(file_path).name}")
        
        # Step 1: Backup
        backup_path = self.backup_file(file_path)
        if not backup_path:
            return {'success': False, 'error': 'Backup failed'}
        
        # Step 2: Analyze original
        print("📊 Analyzing original code...")
        before = self.analyze_file(file_path)
        
        # Step 3: Write new content
        print("✍️ Writing refactored code...")
        if not self.write_file(file_path, fixed_content):
            return {'success': False, 'error': 'Write failed'}
        
        # Step 4: Analyze refactored
        print("📊 Analyzing refactored code...")
        after = self.analyze_file(file_path)
        
        # Step 5: Compare
        comparison = self.compare_scores(before, after)
        
        return {
            'success': True,
            'backup_path': backup_path,
            'before': before,
            'after': after,
            'comparison': comparison
        }
    
    def validate_environment(self) -> Dict:
        """
        Check if all required tools are installed
        
        Returns:
            Validation results
        """
        print("\n🔍 Validating Environment...")
        
        results = {
            'pylint': self.analysis.is_pylint_installed(),
            'pytest': self.testing.is_pytest_installed(),
            'sandbox_exists': self.sandbox_path.exists(),
            'sandbox_writable': os.access(self.sandbox_path, os.W_OK) if self.sandbox_path.exists() else False
        }
        
        print(f"  Pylint: {'✅' if results['pylint'] else '❌'}")
        print(f"  Pytest: {'✅' if results['pytest'] else '❌'}")
        print(f"  Sandbox: {'✅' if results['sandbox_exists'] else '❌'}")
        
        results['all_valid'] = all(results.values())
        
        if not results['all_valid']:
            print("\n⚠️ Some tools are missing. Install them:")
            if not results['pylint']:
                print("  pip install pylint")
            if not results['pytest']:
                print("  pip install pytest")
        
        return results
    
    def get_sandbox_info(self) -> Dict:
        """Get information about sandbox"""
        return {
            'path': str(self.sandbox_path),
            'exists': self.sandbox_path.exists(),
            'is_directory': self.sandbox_path.is_dir() if self.sandbox_path.exists() else False,
            'python_files': len(self.list_python_files(str(self.sandbox_path))) if self.sandbox_path.exists() else 0
        }
    
    # ============ ERROR HANDLING ============
    
    def safe_operation(self, operation: callable, *args, **kwargs) -> Dict:
        """
        Execute an operation with error handling
        
        Args:
            operation: Function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result with success status
        """
        try:
            result = operation(*args, **kwargs)
            return {'success': True, 'result': result}
        except SecurityError as e:
            return {'success': False, 'error': str(e), 'type': 'security_error'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'type': 'general_error'}


# Import os for access check
import os