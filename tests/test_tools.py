"""
Unit Tests for Toolsmith's Tools
Run with: pytest tests/test_tools.py -v
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import FileTools, AnalysisTools, TestingTools, ToolsManager, SecurityError

class TestFileTools:
    """Test file operations"""
    
    def setup_method(self):
        """Setup test environment"""
        self.tools = FileTools(sandbox_path="./sandbox/test")
        self.test_file = "./sandbox/test/test_file.py"
    
    def test_write_and_read(self):
        """Test writing and reading files"""
        content = "print('Hello World')"
        
        # Write
        assert self.tools.write_file(self.test_file, content) == True
        
        # Read
        read_content = self.tools.read_file(self.test_file)
        assert read_content == content
    
    def test_security_outside_sandbox(self):
        """Test that access outside sandbox is blocked"""
        try:
            self.tools.read_file("/etc/passwd")
            assert False, "Should have raised SecurityError"
        except SecurityError:
            assert True
    
    def test_list_python_files(self):
        """Test listing Python files"""
        # Create test files
        self.tools.write_file("./sandbox/test/file1.py", "# File 1")
        self.tools.write_file("./sandbox/test/file2.py", "# File 2")
        
        files = self.tools.list_python_files("./sandbox/test")
        assert len(files) >= 2
    
    def test_backup_and_restore(self):
        """Test backup/restore functionality"""
        original = "Original content"
        modified = "Modified content"
        
        # Write original
        self.tools.write_file(self.test_file, original)
        
        # Backup
        backup = self.tools.backup_file(self.test_file)
        assert backup is not None
        
        # Modify
        self.tools.write_file(self.test_file, modified)
        assert self.tools.read_file(self.test_file) == modified
        
        # Restore
        self.tools.restore_backup(backup, self.test_file)
        assert self.tools.read_file(self.test_file) == original


class TestAnalysisTools:
    """Test code analysis"""
    
    def setup_method(self):
        """Setup"""
        self.tools = AnalysisTools()
        self.file_tools = FileTools(sandbox_path="./sandbox/test")
        self.test_file = "./sandbox/test/analyze_me.py"
    
    def test_pylint_on_good_code(self):
        """Test pylint on well-formatted code"""
        good_code = '''"""Module docstring"""

def add(a, b):
    """Add two numbers"""
    return a + b

def main():
    """Main function"""
    result = add(5, 3)
    print(result)

if __name__ == "__main__":
    main()
'''
        self.file_tools.write_file(self.test_file, good_code)
        result = self.tools.run_pylint(self.test_file)
        
        assert result['score'] > 5.0  # Should be decent score
        assert result['status'] == 'success'
    
    def test_pylint_on_bad_code(self):
        """Test pylint on poorly formatted code"""
        bad_code = '''
x=1+2
def f(a,b):
 return a+b
y=f(1,2)
'''
        self.file_tools.write_file(self.test_file, bad_code)
        result = self.tools.run_pylint(self.test_file)
        
        assert result['total_issues'] > 0
        assert result['status'] == 'success'


class TestTestingTools:
    """Test pytest integration"""
    
    def setup_method(self):
        """Setup"""
        self.tools = TestingTools(sandbox_path="./sandbox/test")
        self.file_tools = FileTools(sandbox_path="./sandbox/test")
    
    def test_discover_tests(self):
        """Test discovering test files"""
        # Create test files
        self.file_tools.write_file(
            "./sandbox/test/test_example.py",
            "def test_something():\n    assert True"
        )
        
        tests = self.tools.discover_tests("./sandbox/test")
        assert len(tests) >= 1
    
    def test_validate_test_file(self):
        """Test validation of test files"""
        self.file_tools.write_file(
            "./sandbox/test/test_valid.py",
            "def test_addition():\n    assert 1 + 1 == 2"
        )
        
        assert self.tools.validate_test_file("./sandbox/test/test_valid.py") == True


class TestToolsManager:
    """Test unified tools manager"""
    
    def setup_method(self):
        """Setup"""
        self.manager = ToolsManager(sandbox_path="./sandbox/test")
    
    def test_validate_environment(self):
        """Test environment validation"""
        result = self.manager.validate_environment()
        assert 'pylint' in result
        assert 'pytest' in result
    
    def test_full_workflow(self):
        """Test complete analysis workflow"""
        # Create test file
        self.manager.write_file(
            "./sandbox/test/workflow_test.py",
            "def test(): pass"
        )
        
        # Run workflow
        result = self.manager.full_analysis_workflow("./sandbox/test")
        
        assert 'files' in result
        assert 'analysis' in result
        assert 'summary' in result


# Helper to run tests manually
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])