from pylint import run_pylint
from orcherstrateur.State import state_flow
from orcherstrateur.agents.auditor import AuditorAgent
from orcherstrateur.agents.fixer import FixerAgent
from src.tools.file_tools import read_file
#here i will generate the graph 
#i will have audit node fix node judge node
'''
to each node i will pass the statflow 
and also in this file i will create edges 
so that audit yroh le fixer apr fixer lel test and if there is error i will
go to fixer again with the output of the judge that can be as and input to the fixer 

'''
def get_issues(issues: list) -> str:
    res = []
    for i, item in enumerate(issues, start=1):
        res.append(
            f"{i}. [{item['type']}] at line {item['line']}\n"
            f"   {item['description']}"
        )
    return "\n".join(res)

def get_study_plan(study_plan:list)->str:
    res=[]
    for i,item in enumerate(study_plan,start=1):
        res.append(
            f"{i} .{study_plan['action']}"
        )
    return "\n".join(res)
           
# i will use those func in order to get the issues and study plan from state passsed to fixer node
#to pass it into the prompt of the fixer    
    
def auditor_node(state: state_flow,filepath) -> state_flow:
   
    
    # Collect results from all files
    all_issues = []
    all_plans = []
    
    
    content = read_file(filepath)
    pylint_report = run_pylint(filepath)
    audit_result = AuditorAgent.analyze(content, filepath, pylint_report)
        

    all_issues.extend(audit_result.get("issues", []))
    all_plans.extend(audit_result.get("refactoring_plan", []))
    
   
    state["audit_results"] = audit_result.content["refactoring_plan"]
    
    print(f"[AUDITOR] Found {len(all_issues)} issues")
    print(f" [AUDITOR] Created {len(all_plans)} step plan")
    
  
    return state
def fixer_node(state:state_flow)->state_flow:
    issues=get_issues(state["issues"])
    plan=get_study_plan(state["refactoring_plan"])
    fixer=FixerAgent().fix()
    return state
  
 #i add the auditor output to the state and return it 
  
def judge_node(state:state_flow)->state_flow:
 #and call the judge
 #i add the auditor output to the state and return it
 #if the output of the judge node is valid then we move to next file or  we are done
 #if the output is not valid we need to check whetther we attended mx iteration or we can send again to fixer  
  return state
#////////////////////////////defining edges////////////

from langgraph.graph import StateGraph
graph=StateGraph(state_flow)
graph.add_node("auditor",auditor_node)
graph.add_node("fixer",fixer_node)
graph.add_node("judge",judge_node)
graph.add_edge("auditor","fixer")
graph.add_edge("fixer","judge")
#i still need to add conditional 
graph.set_entry_point("auditor")