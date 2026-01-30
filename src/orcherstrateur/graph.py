from tkinter import END
from pylint import run_pylint
from .State import state_flow
from .agents.auditor import AuditorAgent
from .agents.fixer import FixerAgent
from .agents.judge import JudgeAgent
from src.tools.file_tools import read_file
from src.utils.logger import ActionType, log_experiment
from src.tools.file_tools import FileTools
from src.tools.analysis_tools import AnalysisTools
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
    # all_issues = []
    # all_plans = []
    
    fl=FileTools()
    analysis=AnalysisTools()
    content = read_file(filepath)
    pylint_report = analysis.run_pylint(filepath)
    audit_result = AuditorAgent.analyze(content, filepath, pylint_report,filepath)
    log_experiment (
agent_name = "auditor",
model_used = "gemini-2.5-flash",
action = ActionType.ANALYSIS, 
details = {
"file_analyzed": filepath,
"input_prompt":fl.read_file("prompts/auditor.txt"), # MANDATORY
"output_response":f"{audit_result}",
# "issues_found": len(all_issues)
},
status="SUCCESS" )

    # all_issues.extend(audit_result.get("issues", []))
    # all_plans.extend(audit_result.get("refactoring_plan", []))
    
   
    state["fix_plan"] = audit_result.content["refactoring_plan"]
    state["issues"] = audit_result.content["issues"]
    
    # print(f"[AUDITOR] Found {len(all_issues)} issues")
    # print(f" [AUDITOR] Created {len(all_plans)} step plan")
    
  
    return state
def fixer_node(state:state_flow)->state_flow:
    #issues=gestate["issues"])
    plan=state["refactoring_plan"]
    origin_code=FileTools.read_file(state["file_path"])
    fixer=FixerAgent.fix(plan,origin_code,state["file_path"])
    log_experiment(
agent_name = "Auditor_Agent",
model_used = "gemini-2.5-flash",
action = ActionType.FIX, 
details = {
"file_analyzed": state["file_path"],
"input_prompt":FileTools.read_file("prompts/fixer.txt"),
"output_response":fixer.content,
},
status="SUCCESS" )
    return state
  
 #i add the auditor output to the state and return it 
  
def judge_node(state:state_flow)->state_flow:
    judge_response=JudgeAgent.judge()
    """if correct i will pass the value to the state and then do state[fixed]==fouad ?
    if we are at max i do backup else i continue"""
 #and call the judge
 #i add the auditor output to the state and return it
 #if the output of the judge node is valid then we move to next file or  we are done
 #if the output is not valid we need to check whetther we attended mx iteration or we can send again to fixer  
    return state
#////////////////////////////defining edges////////////

from langgraph.graph import StateGraph
def should_continue(state: state_flow) -> str:
    """
    Routing function: Decide whether to continue iterating or stop.
    
    Returns:
        "end": Stop the workflow (success or max iterations reached)
        "fixer": Loop back to fixer for another iteration
    """
    # Success case: tests passed!
    if state["test_results"]["passed"]:
        # print(f"\n{'='*60}")
        print(f"SUCCESS: Tests passed! Stopping workflow.")
        # print(f"{'='*60}")
        return "end"
    
    # Failure case: reached max iterations
    elif state["iteration"] >= state["max_iterations"]:
        # print(f"\n{'='*60}")
        print(f"Max iterations ({state['max_iterations']}) reached.")
        print(f"   Stopping workflow with failing tests.")
        # print(f"{'='*60}")
        return "end"
    
    # Retry case: go back to fixer
    else:
        # print(f"\n{'='*60}")
        print(f"Tests failed. Retrying with error feedback...")
        print(f"   Iteration {state['iteration']}/{state['max_iterations']}")
        # print(f"{'='*60}")
        return "fixer"

def build_workflow() -> StateGraph:

 graph=StateGraph(state_flow)
 graph.add_node("auditor",auditor_node)
 graph.add_node("fixer",fixer_node)
#  graph.add_node("judge",judge_node)
 graph.add_edge("auditor","fixer")
#  graph.add_edge("fixer","judge")
#i still need to add conditional
#  graph.add_conditional_edges("judge",should_continue,{
#     "fixer":"fixer",
#     "end":END
# }
                            # ) 
 graph.set_entry_point("auditor")
 return graph.compile()
app=build_workflow()