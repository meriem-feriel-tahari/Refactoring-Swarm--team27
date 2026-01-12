import json
import os
import sys

LOG_FILE = "logs/experiment_data.json"

def validate_logs():
    if not os.path.exists(LOG_FILE):
        print(" Log file does not exist.")
        sys.exit(1)
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(" Log file is not valid JSON.")
            sys.exit(1)
    
    if not isinstance(data, list):
        print(" Log file should contain a list of entries.")
        sys.exit(1)
    
    required_fields = ["id", "timestamp", "agent", "model", "action", "details", "status"]
    required_details = ["input_prompt", "output_response"]
    
    errors = []
    
    for i, entry in enumerate(data):
        # Check top-level fields
        missing = [field for field in required_fields if field not in entry]
        if missing:
            errors.append(f" Entry {i} missing fields: {missing}")
        
        # Check details fields for relevant actions
        action = entry["action"]
        if action in ["CODE_ANALYSIS", "CODE_GEN", "DEBUG", "FIX"]:
            if not isinstance(entry.get("details"), dict):
                errors.append(f" Entry {i} (action={action}): details should be a dict")
            else:
                missing_details = [d for d in required_details if d not in entry["details"]]
                if missing_details:
                    errors.append(f" Entry {i} (action={action}) missing details: {missing_details}")
    
    if errors:
        for err in errors:
            print(err)
        sys.exit(1)
    
    print(f" Log validation passed. Total entries: {len(data)}")
    return True

if __name__ == "__main__":
    validate_logs()