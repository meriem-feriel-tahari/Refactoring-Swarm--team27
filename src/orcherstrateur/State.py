#each agent has as parameter this state flow 
#knowing that each file run separatly 
class state_flow:
   # directory:str
    #file:str
    path:str
    issues:list #issues found by auditor
    fix_plan:list #fix plan provided by fix_plan
    fixer_output:str #fixed code idk if i'm going to use it
    iter:int
    max_iter:int  
    valid_judge:bool  
    
