import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType  # ✅ Add ActionType import

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    
    # ✅ FIXED: Correct logger call with ALL required arguments
    log_experiment(
        agent_name="System",
        model_used="unknown",
        action=ActionType.ANALYSIS,  # Must be from ActionType enum
        details={
            "input_prompt": "System startup",  # ✅ REQUIRED by logger
            "output_response": f"Starting analysis on {args.target_dir}",  # ✅ REQUIRED
            "target_directory": args.target_dir
        },
        status="INFO"  # or "SUCCESS"
    )
    
    print("✅ MISSION_COMPLETE")

if __name__ == "__main__":
    main()