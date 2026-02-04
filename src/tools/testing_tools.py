from pathlib import Path
import re
import subprocess
import sys
from typing import Dict


class TestingTools:
    """Tools for running and analyzing unit tests"""
    
    def __init__(self, sandbox_path: str = "./sandbox"):
        self.sandbox_path = Path(sandbox_path).resolve()
        print("🧪 TestingTools initialized")

    def run_pytest(self, test_target: str, timeout: int = 60, verbose: bool = True) -> Dict:
        cmd = [sys.executable, "-m", "pytest"]

        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")

        cmd.append(test_target)

        project_root = self.sandbox_path.parent 

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(project_root)
            )

            parsed = self.parse_pytest_output(result.stdout + "\n" + result.stderr, result.returncode)
            # parsed["raw_stdout"] = result.stdout
            # parsed["raw_stderr"] = result.stderr
            parsed["return_code"] = result.returncode

            return parsed

        except subprocess.TimeoutExpired as e:
            return {
                "status": "timeout",
                "success": False,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "total": 0,
                "duration": 0.0,
                "failures": [],
                "raw_stdout": e.stdout or "",
                "raw_stderr": e.stderr or "",
                "return_code": -1
            }

        except FileNotFoundError:
            return {
                "status": "pytest_not_installed",
                "success": False,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "total": 0,
                "duration": 0.0,
                "failures": [],
                "raw_stdout": "",
                "raw_stderr": "pytest not found",
                "return_code": -1
            }

    def parse_pytest_output(self, raw_output: str, return_code: int) -> Dict:
        result = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "total": 0,
            "duration": 0.0,
            "success": return_code == 0,
            "status": "success" if return_code == 0 else "failed",
            "failures": [],
        }

        summary_match = re.search(r"=+\s*(\d+)\s+passed\s+in\s+([\d.]+)s", raw_output)
        if summary_match:
            result["passed"] = int(summary_match.group(1))
            result["duration"] = float(summary_match.group(2))

        failed_match = re.search(r"(\d+)\s+failed", raw_output)
        if failed_match:
            result["failed"] = int(failed_match.group(1))

        error_match = re.search(r"(\d+)\s+error", raw_output)
        if error_match:
            result["errors"] = int(error_match.group(1))

        skipped_match = re.search(r"(\d+)\s+skipped", raw_output)
        if skipped_match:
            result["skipped"] = int(skipped_match.group(1))

        result["total"] = (
            result["passed"]
            + result["failed"]
            + result["errors"]
            + result["skipped"]
        )

        for line in raw_output.splitlines():
            if "FAILED" in line and "::" in line:
                result["failures"].append(line.strip())

        return result
