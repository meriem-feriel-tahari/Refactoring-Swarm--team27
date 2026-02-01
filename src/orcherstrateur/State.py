# In src/orcherstrateur/State.py
from typing import TypedDict, List, Optional

class state_flow(TypedDict):
    file_path: str
    issues: List[dict]
    fix_plan: Optional[dict]
    test_results: Optional[dict]
    iteration: int
    max_iterations: int
    valid_judge: bool
    backup_path: Optional[str]