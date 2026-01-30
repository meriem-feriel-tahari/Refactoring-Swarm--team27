#each agent has as parameter this state flow 
#knowing that each file run separatly 
import json
from typing import Dict, Optional


class state_flow:
    #directory:str
    #file:str
    file_path:str
    issues:list #issues found by auditor
    fix_plan:Optional[Dict] #fix plan provided by fix_plan
    test_results: Optional[Dict] # to know whether we are at retry or first time at fixer
    # fixer_output:str #fixed code idk if i'm going to use it
    iter:int
    max_iter:int  
    valid_judge:bool  
    
