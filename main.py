import argparse
import sys
import os
from dotenv import load_dotenv

from src.utils.logger import log_experiment
from src.tools.file_tools import FileTools
from src.orcherstrateur.agents.auditor import AuditorAgent
from src.orcherstrateur.agents.fixer import FixerAgent

load_dotenv()
import os
def main():
    fl=FileTools()
    # ici il faut nmedlo path here im just trying
    auditor=AuditorAgent()
    refplan= auditor.analyse()
    backed_path=fl.backup_file("sandbox/code.py")
    fixer=FixerAgent()
    fixedcode=fixer.fix(refplan,originalcode=fl.read_file("sandbox/code.py"))
    print(fixedcode)
    newfile=fl.write_file("sandbox/code.py",fixedcode)
    #now im going to give the outpt to the fixer and the fixer will create a file and before that we nedd to backup the current file
    #so that we wont lose it 
    
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--target_dir", type=str, required=True)
    # args = parser.parse_args()

    # if not os.path.exists(args.target_dir):
    #     print(f"❌ Dossier {args.target_dir} introuvable.")
    #     sys.exit(1)

    # print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    # log_experiment("System", "STARTUP", f"Target: {args.target_dir}", "INFO")
    
    # print("✅ MISSION_COMPLETE")

if __name__ == "__main__":
    main()