import argparse
import sys
import os
from dotenv import load_dotenv
from src.orcherstrateur.State import state_flow
from src.utils.logger import ActionType, log_experiment
from src.orcherstrateur.graph import app
from src.tools.file_tools import FileTools
from dotenv import load_dotenv
from src.tools.file_tools import FileTools
from src.orcherstrateur.agents.auditor import AuditorAgent
from src.orcherstrateur.agents.fixer import FixerAgent

load_dotenv()
import os
def main():
    

    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
   
    log_experiment("System","gemini-2.5-flash", ActionType.SYSTEM, f"Target: {args.target_dir}", "INFO")
    initstate=state_flow()
    fl=FileTools()
    all_files=fl.list_python_files(fl,"sandbox/")
    print(all_files)
    for file in all_files:
        print(f"processing file {file}\n")
        initstate = {
        "file_path": str(file),
        "issues": [],
        "fix_plan": None,
        "test_results": None,
        "iteration": 0,
        "max_iterations": 5,  
        "valid_judge": False,
        "backup_path": None,
        "test_path":None
    }
        finalstate=app.invoke(initstate)
        
    print("✅ MISSION_COMPLETE")
    

if __name__ == "__main__":
    main() 
    pass