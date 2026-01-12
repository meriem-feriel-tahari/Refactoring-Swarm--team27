"""
Tools Package - Toolsmith's Toolkit
Provides file operations, code analysis, and testing capabilities
"""
# from .testing_tools import TestingToolsManager as TestingTools
from .file_tools import FileTools, SecurityError
from .analysis_tools import AnalysisTools
from .testing_tools import TestingTools
from .tools_manager import ToolsManager

__all__ = [
    'FileTools',
    'AnalysisTools',
    'TestingTools',
    'ToolsManager',
    'SecurityError'
]

__version__ = '1.0.0'
__author__ = 'Toolsmith Team'
