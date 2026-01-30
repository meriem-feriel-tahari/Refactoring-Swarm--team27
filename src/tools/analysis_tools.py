"""
Code Analysis Tools for Refactoring Swarm
Author: Toolsmith Team
Purpose: Run static analysis (pylint) and extract code quality metrics
"""
import subprocess
import json
import re
from typing import Dict, List, Optional
from pathlib import Path

class AnalysisTools:
    """Tools for static code analysis using pylint"""
    
    def __init__(self, sandbox_path: str = "./sandbox"):
        """
        Initialize analysis tools
        
        Args:
            sandbox_path: Base directory for file operations
        """
        self.sandbox_path = Path(sandbox_path).resolve()
        print(f"🔍 AnalysisTools initialized")
    
    def run_pylint(self, file_path: str, timeout: int = 30) -> Dict:
        """
        Run pylint on a Python file
        
        Args:
            file_path: Path to Python file to analyze
            timeout: Maximum execution time in seconds
            
        Returns:
            Dictionary with pylint results:
            {
                'score': float,
                'max_score': float,
                'errors': List[Dict],
                'warnings': List[Dict],
                'conventions': List[Dict],
                'refactors': List[Dict],
                'total_issues': int,
                'raw_output': str,
                'status': str
            }
        """
        print(f"🔍 Running pylint on: {file_path}")
        
        try:
            # Run pylint with JSON output
            result = subprocess.run(
                ['pylint', file_path, '--output-format=json', '--reports=y'],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Parse JSON output
            try:
                issues = json.loads(result.stdout) if result.stdout else []
            except json.JSONDecodeError:
                print("⚠️ Could not parse pylint JSON output")
                issues = []
            
            # Extract score from stderr (pylint prints score there)
            score, max_score = self._extract_score(result.stderr)
            
            # Categorize issues
            categorized = self._categorize_issues(issues)
            
            analysis_result = {
                'score': score,
                'max_score': max_score,
                'percentage': round((score / max_score * 100) if max_score > 0 else 0, 2),
                'errors': categorized['errors'],
                'warnings': categorized['warnings'],
                'conventions': categorized['conventions'],
                'refactors': categorized['refactors'],
                'total_issues': len(issues),
                'raw_output': result.stderr,
                'status': 'success'
            }
            
            print(f"Pylint analysis complete: Score {score}/{max_score} ({analysis_result['percentage']}%)")
            print(f" Issues found: {len(issues)} (Errors: {len(categorized['errors'])}, Warnings: {len(categorized['warnings'])})")
            
            return analysis_result
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Pylint timeout for {file_path}")
            return self._empty_result("timeout", f"Analysis timeout after {timeout}s")
        
        except FileNotFoundError:
            print("❌ Pylint not installed")
            return self._empty_result("not_installed", "Pylint not found. Run: pip install pylint")
        
        except Exception as e:
            print(f"❌ Error running pylint: {e}")
            return self._empty_result("error", str(e))
    
    def _extract_score(self, stderr_output: str) -> tuple[float, float]:
        """
        Extract pylint score from stderr output
        
        Args:
            stderr_output: Pylint stderr text
            
        Returns:
            Tuple of (score, max_score)
        """
        try:
            # Look for pattern: "Your code has been rated at 7.50/10"
            pattern = r"rated at ([\d\.]+)/([\d\.]+)"
            match = re.search(pattern, stderr_output)
            
            if match:
                score = float(match.group(1))
                max_score = float(match.group(2))
                return score, max_score
            
            # Alternative pattern: "Your code has been rated at 7.50"
            pattern2 = r"rated at ([\d\.]+)"
            match2 = re.search(pattern2, stderr_output)
            if match2:
                return float(match2.group(1)), 10.0
                
        except Exception as e:
            print(f"⚠️ Could not extract score: {e}")
        
        return 0.0, 10.0
    
    def _categorize_issues(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize pylint issues by type
        
        Args:
            issues: List of issue dictionaries from pylint
            
        Returns:
            Dictionary with categorized issues
        """
        categorized = {
            'errors': [],
            'warnings': [],
            'conventions': [],
            'refactors': []
        }
        
        for issue in issues:
            issue_type = issue.get('type', '').lower()
            
            formatted_issue = {
                'line': issue.get('line', 0),
                'column': issue.get('column', 0),
                'message': issue.get('message', ''),
                'symbol': issue.get('symbol', ''),
                'message_id': issue.get('message-id', ''),
                'obj': issue.get('obj', '')
            }
            
            if 'error' in issue_type:
                categorized['errors'].append(formatted_issue)
            elif 'warning' in issue_type:
                categorized['warnings'].append(formatted_issue)
            elif 'convention' in issue_type:
                categorized['conventions'].append(formatted_issue)
            elif 'refactor' in issue_type:
                categorized['refactors'].append(formatted_issue)
        
        return categorized
    
    def _empty_result(self, status: str, error_msg: str) -> Dict:
        """
        Return empty result structure on error
        
        Args:
            status: Status code
            error_msg: Error message
            
        Returns:
            Empty result dictionary
        """
        return {
            'score': 0.0,
            'max_score': 10.0,
            'percentage': 0.0,
            'errors': [],
            'warnings': [],
            'conventions': [],
            'refactors': [],
            'total_issues': 0,
            'raw_output': f"Error: {error_msg}",
            'status': status,
            'error': error_msg
        }
    
    def analyze_directory(self, directory: str) -> Dict[str, Dict]:
        """
        Analyze all Python files in a directory
        
        Args:
            directory: Directory path
            
        Returns:
            Dictionary mapping file paths to analysis results
        """
        results = {}
        python_files = []
        
        print(f"📁 Analyzing directory: {directory}")
        
        # Find all Python files
        for file_path in Path(directory).rglob("*.py"):
            if self._should_analyze(file_path):
                python_files.append(str(file_path))
        
        print(f"   Found {len(python_files)} Python files to analyze")
        
        # Analyze each file
        for i, file_path in enumerate(python_files, 1):
            print(f"   [{i}/{len(python_files)}] Analyzing {Path(file_path).name}...")
            results[file_path] = self.run_pylint(file_path)
        
        return results
    
    def _should_analyze(self, file_path: Path) -> bool:
        """
        Check if file should be analyzed
        
        Args:
            file_path: Path object
            
        Returns:
            True if should analyze
        """
        exclude_patterns = [
            '__pycache__',
            '.venv',
            'venv',
            '.git',
            'node_modules',
            '.backup',
            '__init__.py'  # Usually empty
        ]
        
        path_str = str(file_path)
        return not any(pattern in path_str for pattern in exclude_patterns)
    
    def get_summary(self, analysis_results: Dict[str, Dict]) -> Dict:
        """
        Get summary statistics from multiple file analyses
        
        Args:
            analysis_results: Dict mapping file paths to analysis results
            
        Returns:
            Summary dictionary
        """
        total_files = len(analysis_results)
        total_score = 0.0
        total_issues = 0
        total_errors = 0
        total_warnings = 0
        
        for result in analysis_results.values():
            total_score += result.get('score', 0)
            total_issues += result.get('total_issues', 0)
            total_errors += len(result.get('errors', []))
            total_warnings += len(result.get('warnings', []))
        
        avg_score = (total_score / total_files) if total_files > 0 else 0
        
        summary = {
            'total_files': total_files,
            'average_score': round(avg_score, 2),
            'total_issues': total_issues,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'files_analyzed': list(analysis_results.keys())
        }
        
        print(f"\n📊 Analysis Summary:")
        print(f"   Files analyzed: {total_files}")
        print(f"   Average score: {avg_score:.2f}/10")
        print(f"   Total issues: {total_issues} (Errors: {total_errors}, Warnings: {total_warnings})")
        
        return summary
    
    def compare_scores(self, before: Dict, after: Dict) -> Dict:
        """
        Compare analysis results before and after refactoring
        
        Args:
            before: Analysis result before refactoring
            after: Analysis result after refactoring
            
        Returns:
            Comparison dictionary
        """
        score_improvement = after['score'] - before['score']
        issues_reduced = before['total_issues'] - after['total_issues']
        
        comparison = {
            'score_before': before['score'],
            'score_after': after['score'],
            'score_improvement': round(score_improvement, 2),
            'percentage_improvement': round((score_improvement / 10) * 100, 2),
            'issues_before': before['total_issues'],
            'issues_after': after['total_issues'],
            'issues_reduced': issues_reduced,
            'improved': score_improvement > 0
        }
        
        print(f"\n📈 Improvement Analysis:")
        print(f"   Score: {before['score']:.2f} → {after['score']:.2f} ({'+' if score_improvement > 0 else ''}{score_improvement:.2f})")
        print(f"   Issues: {before['total_issues']} → {after['total_issues']} ({issues_reduced} reduced)")
        
        return comparison
    
    def is_pylint_installed(self) -> bool:
        """Check if pylint is installed"""
        try:
            subprocess.run(['pylint', '--version'], capture_output=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False