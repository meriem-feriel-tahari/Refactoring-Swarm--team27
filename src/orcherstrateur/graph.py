from orcherstrateur.State import state_flow
#here i will generate the graph 
#i will have audit node fix node judge node
'''
to each node i will pass the statflow 
and also in this file i will create edges 
so that audit yroh le fixer apr fixer lel test and if there is error i will
go to fixer again with the output of the judge that can be as and input to the fixer 

'''
def auditor_node(state:state_flow)->state_flow:
 #modify the prompt 
 #and then call the auditor
 #i add the auditor output to the state and return it
  return state
def fixer_node(state:state_flow)->state_flow:
 #modify the prompt 
 #and then call the fixer
 #i add the auditor output to the state and return it
  return state
def judge_node(state:state_flow)->state_flow:
 #modify the prompt 
 #and then call the judge
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