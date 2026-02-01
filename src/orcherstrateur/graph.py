import json
from pylint import run_pylint
from .State import state_flow
from .agents.auditor import AuditorAgent 
from .agents.fixer import FixerAgent
from .agents.judge import JudgeAgent
from src.utils.logger import ActionType, log_experiment
from src.tools.file_tools import FileTools
from src.tools.testing_tools import TestingTools
from src.tools.analysis_tools import AnalysisTools
#here i will generate the graph 
#i will have audit node fix node judge node
'''
to each node i will pass the statflow 
and also in this file i will create edges 
so that audit yroh le fixer apr fixer lel test and if there is error i will
go to fixer again with the output of the judge that can be as and input to the fixer 

'''
fl=FileTools()
fa=AnalysisTools()
ft=TestingTools()
auditor=AuditorAgent ()
fixer=FixerAgent()
judge_agent=JudgeAgent()
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
    
def auditor_node(state: state_flow) -> state_flow:
    path=state["file_path"]
    content = fl.read_file(fl,path)
    pylint_report = fa.run_pylint(fa,state["file_path"])
    audit_result = auditor .analyze(content,pylint_report,state["file_path"])
    # if isinstance(audit_result, str):
    #     parsed_result = json.loads(audit_result)
    # else:
    #     parsed_result = audit_result
    log_experiment (
agent_name = "auditor",
model_used = "gemini-2.5-flash",
action = ActionType.ANALYSIS, 
details = {
"file_analyzed": state["file_path"],
"input_prompt":fl.read_file(fl,"prompts/auditor.txt"), # MANDATORY
"output_response":f"{audit_result}",
# "issues_found": len(all_issues)
},
status="SUCCESS" )

    # all_issues.extend(audit_result.get("issues", []))
    # all_plans.extend(audit_result.get("refactoring_plan", []))
    
   
    state["fix_plan"] = audit_result
    state["issues"] = audit_result
    
    
    
  
    return state
def fixer_node(state:state_flow)->state_flow:
    #issues=gestate["issues"])
    plan=state["fix_plan"]
    origin_code=fl.read_file(fl,state["file_path"])
    fixer_response=fixer.fix(plan,origin_code,state["file_path"])
    log_experiment(
agent_name = "Auditor_Agent",
model_used = "gemini-2.5-flash",
action = ActionType.FIX, 
details = {
"file_analyzed": state["file_path"],
"input_prompt":fl.read_file(fl,"prompts/fixer.txt"),
"output_response":fixer_response,
},
status="SUCCESS" )
    backup_path= fl.backup_file(fl,state["file_path"])
    state["backup_path"]=backup_path
    fl.write_file(fl,state["file_path"],fixer_response["fixed_code"])
    return state
  
 #i add the auditor output to the state and return it 
  
def judge_node(state:state_flow)->state_flow:
    current_code=fl.read_file(fl,state["file_path"])
    judge_response=judge_agent.judge(current_code)
    test_path=f"""sandbox/{judge_response["test_file_name"]}"""
    fl.write_file(fl,test_path,judge_response["test_code"])
    pytest_output=ft.run_pytest(ft,".",test_path)
    state["test_results"]=pytest_output
    return state
def end_node(state):
    
    return state
#////////////////////defining edges////////////

from langgraph.graph import StateGraph,END
def should_continue(state: state_flow) -> str:
    """
    Routing function: Decide whether to continue iterating or stop.
    
    Returns:
        "end": Stop the workflow (success or max iterations reached)
        "fixer": Loop back to fixer for another iteration
    """
    # Success case: tests passed!
    if state["test_results"]["success"]:
        print(f"SUCCESS: Tests passed! Stopping workflow.")
        return "end"
    
    # Failure case: reached max iterations
    elif state["iteration"] >= state["max_iterations"]:
        print(f"Max iterations ({state['max_iterations']}) reached.")
        print(f"   Stopping workflow with failing tests.")
        return "end"
    
    # Retry case: go back to fixer
    else:
        print(f"Tests failed. Retrying ...")
        print(f"   Iteration {state['iteration']}/{state['max_iterations']}")
        return "fixer"



def build_workflow() -> StateGraph:
    graph = StateGraph(state_flow)

    # Ajouter tous les nœuds
    graph.add_node("auditor", auditor_node)
    graph.add_node("fixer", fixer_node)
    graph.add_node("judge", judge_node)
    # graph.add_node("end", end_node)

    # Arêtes simples
    graph.add_edge("auditor", "fixer")
    graph.add_edge("fixer", "judge")
    # graph.add_edge("judge", "end")

    # Arêtes conditionnelles
    graph.add_conditional_edges("judge", should_continue, {
        "fixer": "fixer",
        "end": END
    })

    # Point d'entrée
    graph.set_entry_point("auditor")

    return graph.compile()


app=build_workflow()