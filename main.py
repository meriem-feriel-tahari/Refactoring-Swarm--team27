import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment
from try_toolsmith.call import process_files

load_dotenv()
import os

path = r"notes/"  # use raw string to avoid issues with backslashes

def get_files(path):
    """
    Recursively collects all file paths in a folder and returns them as a list.
    """
    file_list = []
    print("main")

    for root, dirs, files in os.walk(path):
        for filename in files:
            file_path = os.path.normpath( os.path.join(root, filename)).replace("\\","/")
           
            
            file_list.append(file_path)
    
    return file_list

# Example usage
all_files = get_files(path)
print(all_files[0])
with open(all_files[0], "r", encoding="utf-8") as fh:
    content = fh.read()
print(content)
process_files(all_files[0]) 
print(content)


         
    
  

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--target_dir", type=str, required=True)
#     args = parser.parse_args()

#     if not os.path.exists(args.target_dir):
#         print(f"❌ Dossier {args.target_dir} introuvable.")
#         sys.exit(1)

#     print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
#     log_experiment("System", "STARTUP", f"Target: {args.target_dir}", "INFO")
    
#     print("✅ MISSION_COMPLETE")

# if __name__ == "__main__":
#     main()