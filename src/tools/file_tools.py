"""
File Operations Tools for Refactoring Swarm
Author: Toolsmith Team
Purpose: Safe file reading/writing operations within sandbox
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

class SecurityError(Exception):
    """Raised when trying to access files outside sandbox"""
    pass

class FileTools:
    """Tools for safe file operations within sandbox"""
    
    def __init__(self, sandbox_path: str = "./sandbox",prompts_path:str ="./prompts"):
        """
        Initialize with sandbox directory
        
        Args:
            sandbox_path: Base directory where agents can work
        """
        self.sandbox_path = Path(sandbox_path).resolve()
        self.sandbox_path.mkdir(parents=True, exist_ok=True)
        self.prompts_path = Path(prompts_path).resolve()
        self.prompts_path.mkdir(parents=True, exist_ok=True)
      #  print(f"FileTools initialized with sandbox: {self.sandbox_path}")
    
    def _is_safe_path(self, file_path: str) -> bool:
        """
        Security check: Ensure path is within sandbox
        
        Args:
            file_path: Path to check
            
        Returns:
            True if path is safe (within sandbox)
        """
        try:
            full_path = Path(file_path).resolve()
            return str(full_path).startswith(str(self.sandbox_path)) or str(full_path).startswith(str(self.prompts_path))
        except Exception as e:
            print(f"⚠️ Path validation error: {e}")
            return False
    @staticmethod
    def read_file(self, file_path: str) -> Optional[str]:
        """
        Safely read a file from sandbox
        
        Args:
            file_path: Path to file (relative or absolute)
            
        Returns:
            File content as string, or None if error
            
        Raises:
            SecurityError: If path is outside sandbox
        """
        if not self._is_safe_path(file_path):
            raise SecurityError(f"🚫 Access denied: {file_path} is outside sandbox")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f" Read file: {file_path} ({len(content)} chars)")
            return content
        except FileNotFoundError:
            print(f" File not found: {file_path}")
            return None
        except UnicodeDecodeError:
            print(f" Cannot read file (encoding issue): {file_path}")
            return None
        except Exception as e:
            print(f" Error reading file: {e}")
            return None
    @staticmethod 
    def write_file(self, file_path: str, content: str) -> bool:
        """
        Safely write content to a file in sandbox
        
        Args:
            file_path: Path where to write
            content: Content to write
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            SecurityError: If path is outside sandbox
        """
        if not self._is_safe_path(file_path):
            raise SecurityError(f" Access denied: {file_path} is outside sandbox")
        
        try:
            print(f"hello from write file \n")
            # Create parent directories if needed
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f" Wrote file: {file_path} ({len(content)} chars)")
            return True
        except Exception as e:
            print(f" Error writing file: {e}")
            return False
    @staticmethod
    def list_python_files(self, directory: str) -> List[str]:
        """
        List all Python files in a directory
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of Python file paths
            
        Raises:
            SecurityError: If directory is outside sandbox
        """
        if not self._is_safe_path(directory):
            raise SecurityError(f" Access denied: {directory} is outside sandbox")
        
        python_files = []
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        full_path = os.path.join(root, file)
                        python_files.append(full_path)
            
            print(f" Found {len(python_files)} Python files in {directory}")
            return python_files
        except Exception as e:
            print(f" Error listing files: {e}")
            return []
    @staticmethod
    def backup_file(self, file_path: str) -> Optional[str]:
        """
        Create a backup of a file before modification
        
        Args:
            file_path: File to backup
            
        Returns:
            Path to backup file, or None if failed
            
        Raises:
            SecurityError: If path is outside sandbox
        """
        if not self._is_safe_path(file_path):
            raise SecurityError(f" Access denied: {file_path} is outside sandbox")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.backup.py"
            
            content = self.read_file(self,file_path)
            if content and self.write_file(self,backup_path, content):
                print(f" Backup created: {backup_path}")
                return backup_path
            return None
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    @staticmethod
    def restore_backup(self, backup_path: str, original_path: str) -> bool:
        """
        Restore a file from backup
        
        Args:
            backup_path: Path to backup file
            original_path: Path where to restore
            
        Returns:
            True if successful
        """
        try:
            content = self.read_file(backup_path)
            if content:
                return self.write_file(original_path, content)
            return False
        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            return False
    @staticmethod
    def delete_file(self, file_path: str) -> bool:
        """
        Safely delete a file
        
        Args:
            file_path: File to delete
            
        Returns:
            True if successful
        """
        if not self._is_safe_path(file_path):
            raise SecurityError(f"🚫 Access denied: {file_path} is outside sandbox")
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Deleted: {file_path}")
                return True
            else:
                print(f"⚠️ File doesn't exist: {file_path}")
                return False
        except Exception as e:
            print(f"❌ Error deleting file: {e}")
            return False
    
    def copy_file(self, source: str, destination: str) -> bool:
        """
        Copy a file within sandbox
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if successful
        """
        if not self._is_safe_path(source) or not self._is_safe_path(destination):
            raise SecurityError("🚫 Access denied: paths must be in sandbox")
        
        try:
            shutil.copy2(source, destination)
            print(f"📋 Copied: {source} → {destination}")
            return True
        except Exception as e:
            print(f"❌ Error copying file: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """
        Get information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info or None
        """
        if not self._is_safe_path(file_path):
            raise SecurityError(f"🚫 Access denied: {file_path} is outside sandbox")
        
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'is_file': os.path.isfile(file_path),
                'extension': Path(file_path).suffix
            }
        except Exception as e:
            print(f"❌ Error getting file info: {e}")
            return None
    
    def create_directory(self, dir_path: str) -> bool:
        """
        Create a directory in sandbox
        
        Args:
            dir_path: Directory path
            
        Returns:
            True if successful
        """
        if not self._is_safe_path(dir_path):
            raise SecurityError(f"🚫 Access denied: {dir_path} is outside sandbox")
        
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {dir_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating directory: {e}")
            return False
    
    def get_sandbox_path(self) -> str:
        """Get the sandbox path"""
        return str(self.sandbox_path)
    
    def is_empty_directory(self, dir_path: str) -> bool:
        """Check if directory is empty"""
        if not self._is_safe_path(dir_path):
            raise SecurityError(f"🚫 Access denied: {dir_path} is outside sandbox")
        
        try:
            return len(os.listdir(dir_path)) == 0
        except Exception:
            return False