# ==============================================================================
# FILE 1: src/orchestrator/__init__.py
# ==============================================================================
"""
Orchestrator package for the Refactoring Swarm.
Manages the multi-agent workflow with LangGraph.
"""

from .state import WorkflowState
from .agents import AuditorAgent, FixerAgent, JudgeAgent
from .graph import app

__all__ = ['WorkflowState', 'AuditorAgent', 'FixerAgent', 'JudgeAgent', 'app']


# ==============================================================================
# FILE 2: src/orchestrator/state.py
# ==============================================================================
"""
Workflow state definition.
This object flows between all agents and tracks the refactoring progress.
"""

from typing import TypedDict, List, Dict, Optional


class WorkflowState(TypedDict):
    """
    State object shared between all agents in the workflow.
    
    Attributes:
        target_dir: Directory containing Python files to refactor
        files_to_process: List of Python file paths found in target_dir
        audit_results: Dictionary mapping filepath to audit findings
        fixed_files: List of files that have been fixed
        test_results: Results from running pytest
        iteration: Current iteration number in the fix-test loop
        max_iterations: Maximum allowed iterations before giving up
        error_logs: Test error messages to guide the next fix iteration
    """
    target_dir: str
    files_to_process: List[str]
    audit_results: Optional[Dict[str, Dict]]
    fixed_files: List[str]
    test_results: Optional[Dict]
    iteration: int
    max_iterations: int
    error_logs: Optional[List[str]]


# ==============================================================================
# FILE 3: src/orchestrator/agents.py
# ==============================================================================
"""
Agent definitions for the Refactoring Swarm.
Each agent is a specialized LLM-powered component.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.logger import log_experiment, ActionType
import os
import json


class AuditorAgent:
    """
    The Auditor analyzes code to find bugs, style issues, and potential problems.
    Uses static analysis (pylint) and LLM-based code review.
    """
    
    def __init__(self):
        """Initialize the Auditor with Gemini LLM"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1  # Low temperature for consistent analysis
        )
        
        # Load system prompt from Prompt Engineer's file
        try:
            with open("src/prompts/auditor_prompt.txt", "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            # Fallback prompt if file doesn't exist yet
            self.system_prompt = """You are an expert Python code auditor.
Analyze the provided code and identify:
1. Syntax errors
2. Logic bugs
3. Missing docstrings
4. Code style violations
5. Potential runtime errors

Return your findings as a JSON object with this structure:
{
    "issues": [
        {"line": 10, "severity": "high", "description": "Missing docstring"},
        {"line": 15, "severity": "medium", "description": "Unused variable 'x'"}
    ],
    "summary": "Found 2 issues"
}"""
    
    def analyze(self, file_content: str, filename: str, pylint_report: dict = None) -> dict:
        """
        Analyze a Python file and return issues found.
        
        Args:
            file_content: The Python code to analyze
            filename: Name of the file being analyzed
            pylint_report: Optional pylint analysis results
        
        Returns:
            Dictionary containing issues found
        """
        # Build the full prompt
        context = f"File: {filename}\n\n"
        
        if pylint_report:
            context += f"Pylint Score: {pylint_report.get('score', 'N/A')}\n"
            context += f"Pylint Issues: {pylint_report.get('issues', [])}\n\n"
        
        full_prompt = f"{self.system_prompt}\n\n{context}Code to analyze:\n\n{file_content}"
        
        try:
            # Call the LLM
            response = self.llm.invoke(full_prompt)
            output = response.content
            
            # Log the interaction (MANDATORY for experiment data)
            log_experiment(
                agent_name="Auditor_Agent",
                model_used="gemini-2.0-flash-exp",
                action=ActionType.ANALYSIS,
                details={
                    "file_analyzed": filename,
                    "input_prompt": full_prompt,
                    "output_response": output,
                    "pylint_score": pylint_report.get('score') if pylint_report else None
                },
                status="SUCCESS"
            )
            
            # Parse JSON response
            try:
                issues = json.loads(output)
                return issues
            except json.JSONDecodeError:
                # Fallback if LLM didn't return valid JSON
                return {
                    "issues": [{"description": output}],
                    "summary": "Raw analysis (non-JSON response)"
                }
        
        except Exception as e:
            # Log failure
            log_experiment(
                agent_name="Auditor_Agent",
                model_used="gemini-2.0-flash-exp",
                action=ActionType.ANALYSIS,
                details={
                    "file_analyzed": filename,
                    "input_prompt": full_prompt,
                    "output_response": "",
                    "error": str(e)
                },
                status="FAILED"
            )
            raise


class FixerAgent:
    """
    The Fixer rewrites code to address issues found by the Auditor
    or to fix failing tests.
    """
    
    def __init__(self):
        """Initialize the Fixer with Gemini LLM"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.2  # Slightly higher for creative fixes
        )
        
        # Load system prompt from Prompt Engineer's file
        try:
            with open("src/prompts/fixer_prompt.txt", "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            # Fallback prompt
            self.system_prompt = """You are an expert Python code fixer.
Your job is to rewrite the provided code to fix all identified issues.

Rules:
1. Fix all bugs and errors
2. Add missing docstrings
3. Improve code style
4. Preserve the original functionality
5. Return ONLY the fixed code, no explanations

If test errors are provided, prioritize fixing those errors."""
    
    def fix_code(self, file_content: str, issues: dict, filename: str = "", error_logs: str = None) -> str:
        """
        Fix code based on audit issues or test errors.
        
        Args:
            file_content: The original Python code
            issues: Dictionary of issues from Auditor
            filename: Name of the file (for logging)
            error_logs: Optional test error messages from Judge
        
        Returns:
            Fixed Python code as a string
        """
        # Build context
        context = f"File: {filename}\n\n"
        context += f"Issues to fix:\n{json.dumps(issues, indent=2)}\n\n"
        
        if error_logs:
            context += f"Test errors that need fixing:\n{error_logs}\n\n"
        
        full_prompt = f"{self.system_prompt}\n\n{context}Original code:\n\n{file_content}\n\nFixed code:"
        
        try:
            # Call the LLM
            response = self.llm.invoke(full_prompt)
            fixed_code = response.content
            
            # Clean up the response (remove markdown code blocks if present)
            if fixed_code.startswith("```python"):
                fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
            elif fixed_code.startswith("```"):
                fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
            
            # Log the interaction
            log_experiment(
                agent_name="Fixer_Agent",
                model_used="gemini-2.0-flash-exp",
                action=ActionType.FIX,
                details={
                    "file_fixed": filename,
                    "input_prompt": full_prompt,
                    "output_response": fixed_code,
                    "issues_count": len(issues.get('issues', [])),
                    "had_test_errors": error_logs is not None
                },
                status="SUCCESS"
            )
            
            return fixed_code
        
        except Exception as e:
            # Log failure
            log_experiment(
                agent_name="Fixer_Agent",
                model_used="gemini-2.0-flash-exp",
                action=ActionType.FIX,
                details={
                    "file_fixed": filename,
                    "input_prompt": full_prompt,
                    "output_response": "",
                    "error": str(e)
                },
                status="FAILED"
            )
            raise


class JudgeAgent:
    """
    The Judge evaluates test results and determines if fixes were successful.
    Analyzes pytest output to decide if another iteration is needed.
    """
    
    def __init__(self):
        """Initialize the Judge with Gemini LLM"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.0  # Deterministic evaluation
        )
        
        # Load system prompt from Prompt Engineer's file
        try:
            with open("src/prompts/judge_prompt.txt", "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            # Fallback prompt
            self.system_prompt = """You are a test results evaluator.
Analyze the pytest output and determine if tests passed or failed.

Return a JSON object with this structure:
{
    "passed": true/false,
    "total_tests": number,
    "failed_tests": number,
    "error_summary": "brief description of failures",
    "critical_errors": ["list of critical issues"]
}"""
    
    def evaluate(self, test_output: str) -> dict:
        """
        Evaluate test results and determine pass/fail status.
        
        Args:
            test_output: Raw output from pytest
        
        Returns:
            Dictionary with evaluation results
        """
        full_prompt = f"{self.system_prompt}\n\nTest output to evaluate:\n\n{test_output}"
        
        try:
            # Call the LLM
            response = self.llm.invoke(full_prompt)
            evaluation = response.content
            
            # Log the interaction
            log_experiment(
                agent_name="Judge_Agent",
                model_used="gemini-2.0-flash-exp",
                action=ActionType.DEBUG,
                details={
                    "input_prompt": full_prompt,
                    "output_response": evaluation
                },
                status="SUCCESS"
            )
            
            # Parse JSON response
            try:
                result = json.loads(evaluation)
                return result
            except json.JSONDecodeError:
                # Fallback: simple keyword detection
                passed = "PASSED" in test_output.upper() or "OK" in test_output.upper()
                return {
                    "passed": passed and "FAILED" not in test_output.upper(),
                    "total_tests": 0,
                    "failed_tests": 0,
                    "error_summary": evaluation
                }
        
        except Exception as e:
            # Log failure
            log_experiment(
                agent_name="Judge_Agent",
                model_used="gemini-2.0-flash-exp",
                action=ActionType.DEBUG,
                details={
                    "input_prompt": full_prompt,
                    "output_response": "",
                    "error": str(e)
                },
                status="FAILED"
            )
            raise


# ==============================================================================
# FILE 4: src/orchestrator/graph.py
# ==============================================================================
"""
LangGraph workflow definition.
This is the core orchestration logic that connects all agents.
"""

from langgraph.graph import StateGraph, END
from .state import WorkflowState
from .agents import AuditorAgent, FixerAgent, JudgeAgent

# Import Toolsmith's functions
# NOTE: These imports will fail until Toolsmith creates these files!
# You can comment them out for initial testing
try:
    from src.tools.code_tools import read_file_content, write_file_content
    from src.tools.analysis_tools import run_pylint, run_pytest
    TOOLS_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: Tool functions not available yet. Using mock functions.")
    TOOLS_AVAILABLE = False
    
    # Mock functions for testing
    def read_file_content(filepath: str) -> str:
        with open(filepath, 'r') as f:
            return f.read()
    
    def write_file_content(filepath: str, content: str) -> bool:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    
    def run_pylint(filepath: str) -> dict:
        return {"score": 5.0, "issues": []}
    
    def run_pytest(directory: str) -> dict:
        return {"passed": True, "output": "All tests passed"}


# Initialize agents (created once, reused throughout workflow)
auditor = AuditorAgent()
fixer = FixerAgent()
judge = JudgeAgent()


def auditor_node(state: WorkflowState) -> WorkflowState:
    """
    Node 1: Audit all Python files in the target directory.
    
    Process:
    1. Read each file
    2. Run pylint static analysis
    3. Get LLM analysis from Auditor
    4. Compile results
    """
    print(f"\n{'='*60}")
    print(f"🔍 [AUDITOR] Starting code analysis...")
    print(f"{'='*60}")
    print(f"Files to analyze: {len(state['files_to_process'])}")
    
    audit_results = {}
    
    for filepath in state['files_to_process']:
        print(f"\n  Analyzing: {filepath}")
        
        try:
            # Read file content
            content = read_file_content(filepath)
            
            # Run pylint (static analysis)
            pylint_report = run_pylint(filepath)
            print(f"    Pylint score: {pylint_report.get('score', 'N/A')}")
            
            # Get LLM analysis
            issues = auditor.analyze(content, filepath, pylint_report)
            
            audit_results[filepath] = {
                "issues": issues,
                "pylint_score": pylint_report.get("score", 0),
                "content": content  # Store for Fixer
            }
            
            print(f"    Issues found: {len(issues.get('issues', []))}")
        
        except Exception as e:
            print(f"    ❌ Error analyzing {filepath}: {e}")
            audit_results[filepath] = {
                "issues": {"error": str(e)},
                "pylint_score": 0
            }
    
    state["audit_results"] = audit_results
    print(f"\n✅ [AUDITOR] Analysis complete!")
    print(f"   Total files analyzed: {len(audit_results)}")
    
    return state


def fixer_node(state: WorkflowState) -> WorkflowState:
    """
    Node 2: Fix code based on audit results or test errors.
    
    Process:
    1. For each file with issues
    2. Get fixed code from Fixer LLM
    3. Write fixed code back to file
    """
    print(f"\n{'='*60}")
    print(f"🔧 [FIXER] Starting code fixes...")
    print(f"{'='*60}")
    print(f"Iteration: {state['iteration'] + 1}/{state['max_iterations']}")
    
    fixed_files = []
    
    for filepath, audit_data in state["audit_results"].items():
        print(f"\n  Fixing: {filepath}")
        
        try:
            # Get original or previously fixed content
            content = audit_data.get("content", read_file_content(filepath))
            
            # Get error logs if this is a retry
            error_context = None
            if state.get("error_logs"):
                error_context = "\n".join(state["error_logs"])
            
            # Get fixed code from Fixer LLM
            fixed_code = fixer.fix_code(
                file_content=content,
                issues=audit_data["issues"],
                filename=filepath,
                error_logs=error_context
            )
            
            # Write fixed code back to file
            if write_file_content(filepath, fixed_code):
                fixed_files.append(filepath)
                print(f"    ✅ Fixed and saved")
            else:
                print(f"    ❌ Failed to save")
        
        except Exception as e:
            print(f"    ❌ Error fixing {filepath}: {e}")
    
    state["fixed_files"] = fixed_files
    state["iteration"] += 1
    
    print(f"\n✅ [FIXER] Fixes complete!")
    print(f"   Files fixed: {len(fixed_files)}/{len(state['audit_results'])}")
    
    return state


def judge_node(state: WorkflowState) -> WorkflowState:
    """
    Node 3: Run tests and evaluate results.
    
    Process:
    1. Run pytest on the target directory
    2. Get evaluation from Judge LLM
    3. Store results and error logs
    """
    print(f"\n{'='*60}")
    print(f"⚖️ [JUDGE] Running tests...")
    print(f"{'='*60}")
    
    try:
        # Run pytest on the directory
        test_output = run_pytest(state["target_dir"])
        
        # Get evaluation from Judge LLM
        evaluation = judge.evaluate(str(test_output))
        
        # Store results
        state["test_results"] = {
            "passed": evaluation.get("passed", False),
            "details": test_output,
            "evaluation": evaluation
        }
        
        # Save error logs if tests failed
        if not evaluation.get("passed"):
            state["error_logs"] = [
                evaluation.get("error_summary", "Unknown error"),
                str(test_output.get("errors", []))
            ]
            print(f"\n❌ [JUDGE] Tests FAILED")
            print(f"   Failed tests: {evaluation.get('failed_tests', 'unknown')}")
            print(f"   Error summary: {evaluation.get('error_summary', 'See logs')}")
        else:
            state["error_logs"] = None
            print(f"\n✅ [JUDGE] All tests PASSED!")
            print(f"   Total tests: {evaluation.get('total_tests', 'unknown')}")
    
    except Exception as e:
        print(f"\n❌ [JUDGE] Error running tests: {e}")
        state["test_results"] = {
            "passed": False,
            "details": {"error": str(e)},
            "evaluation": {"passed": False, "error_summary": str(e)}
        }
        state["error_logs"] = [str(e)]
    
    return state


def should_continue(state: WorkflowState) -> str:
    """
    Routing function: Decide whether to continue iterating or stop.
    
    Returns:
        "end": Stop the workflow (success or max iterations reached)
        "fixer": Loop back to fixer for another iteration
    """
    # Success case: tests passed!
    if state["test_results"]["passed"]:
        print(f"\n{'='*60}")
        print(f"🎉 SUCCESS: Tests passed! Stopping workflow.")
        print(f"{'='*60}")
        return "end"
    
    # Failure case: reached max iterations
    elif state["iteration"] >= state["max_iterations"]:
        print(f"\n{'='*60}")
        print(f"⚠️ Max iterations ({state['max_iterations']}) reached.")
        print(f"   Stopping workflow with failing tests.")
        print(f"{'='*60}")
        return "end"
    
    # Retry case: go back to fixer
    else:
        print(f"\n{'='*60}")
        print(f"🔁 Tests failed. Retrying with error feedback...")
        print(f"   Iteration {state['iteration']}/{state['max_iterations']}")
        print(f"{'='*60}")
        return "fixer"


def build_workflow() -> StateGraph:
    """
    Build and compile the LangGraph workflow.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph
    workflow = StateGraph(WorkflowState)
    
    # Add the three agent nodes
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("judge", judge_node)
    
    # Define the flow
    workflow.set_entry_point("auditor")  # Always start with auditor
    
    # Linear flow: Auditor → Fixer → Judge
    workflow.add_edge("auditor", "fixer")
    workflow.add_edge("fixer", "judge")
    
    # Conditional edge: Judge decides what's next
    workflow.add_conditional_edges(
        "judge",           # From this node
        should_continue,   # Use this function to decide
        {
            "fixer": "fixer",  # Loop back to fixer if tests failed
            "end": END         # Stop if tests passed or max iterations
        }
    )
    
    # Compile and return
    return workflow.compile()


# Create the app (this is what main.py will import)
app = build_workflow()


# ==============================================================================
# FILE 5: main.py (at project root)
# ==============================================================================
"""
Main entry point for the Refactoring Swarm.
Handles CLI arguments and launches the orchestrator workflow.
"""

import argparse
import os
import sys
from src.orchestrator.graph import app
from src.orchestrator.state import WorkflowState

# Mock function for scanning Python files (until Toolsmith provides it)
def scan_python_files(directory: str) -> list:
    """Scan directory for Python files"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
    return python_files


def main():
    """CLI entry point for the Refactoring Swarm"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Refactoring Swarm - Autonomous Multi-Agent Code Fixer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --target_dir ./sandbox/test_case
  python main.py --target_dir ./sandbox/dataset_inconnu --max-iterations 5
        """
    )
    
    parser.add_argument(
        "--target_dir",
        required=True,
        help="Directory containing Python files to refactor"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum number of fix-test iterations (default: 3)"
    )
    
    args = parser.parse_args()
    
    # Validate directory exists
    if not os.path.exists(args.target_dir):
        print(f"❌ Error: Directory '{args.target_dir}' not found.")
        sys.exit(1)
    
    if not os.path.isdir(args.target_dir):
        print(f"❌ Error: '{args.target_dir}' is not a directory.")
        sys.exit(1)
    
    # Scan for Python files
    print(f"\n{'='*60}")
    print(f"🔍 Scanning for Python files...")
    print(f"{'='*60}")
    
    files = scan_python_files(args.target_dir)
    
    if not files:
        print(f"⚠️ No Python files found in '{args.target_dir}'")
        print(f"   Make sure the directory contains .py files.")
        sys.exit(1)
    
    # Print startup information
    print(f"\n{'='*60}")
    print(f"🚀 REFACTORING SWARM STARTING")
    print(f"{'='*60}")
    print(f"📂 Target Directory: {args.target_dir}")
    print(f"📄 Python Files Found: {len(files)}")
    for f in files:
        print(f"   - {f}")
    print(f"🔄 Max Iterations: {args.max_iterations}")
    print(f"{'='*60}")
    
    # Create initial state
    initial_state = WorkflowState(
        target_dir=args.target_dir,
        files_to_process=files,
        audit_results=None,
        fixed_files=[],
        test_results=None,
        iteration=0,
        max_iterations=args.max_iterations,
        error_logs=None
    )
    
    # Run the workflow
    try:
        print(f"\n🎬 Starting workflow...\n")
        final_state = app.invoke(initial_state)
        
        # Print final results
        print(f"\n{'='*60}")
        print(f"🏁 WORKFLOW COMPLETE")
        print(f"{'='*60}")
        
        if final_state["test_results"]["passed"]:
            print(f"✅ SUCCESS: All tests passed!")
            print(f"📊 Statistics:")
            print(f"   - Files processed: {len(final_state['fixed_files'])}")
            print(f"   - Iterations used: {final_state['iteration']}/{args.max_iterations}")
            print(f"   - Final status: PASSED")
        else:
            print(f"⚠️ INCOMPLETE: Workflow ended with failing tests")
            print(f"📊 Statistics:")
            print(f"   - Files processed: {len(final_state['fixed_files'])}")
            print(f"   - Iterations used: {final_state['iteration']}/{args.max_iterations}")
            print(f"   - Final status: FAILED")
            print(f"\n💡 Suggestions:")
            print(f"   - Try increasing --max-iterations")
            print(f"   - Check the error logs in logs/experiment_data.json")
            print(f"   - Review the fixed code manually")
        
        print(f"\n📁 Results saved to: {args.target_dir}")
        print(f"📋 Experiment logs: logs/experiment_data.json")
        print(f"{'='*60}\n")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Workflow interrupted by user.")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ FATAL ERROR: Workflow crashed")
        print(f"{'='*60}")
        print(f"Error: {str(e)}")
        print(f"\nFull traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()