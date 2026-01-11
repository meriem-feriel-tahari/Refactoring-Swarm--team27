import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
def read(filepath):
    try :
        with open('filepath','r') as f:
            content=f.read()
        print(content)
        return content
    except: FileNotFoundError
    
    print("not found")        
class AuditorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
        # self.system_prompt=read("prompts/auditor.txt")

    def analyse(self, file_content: str):
        prompt="""ROLE :
You are the AUDITOR agent in the "Refactoring Swarm" System 


Task :
1- Analyze "badly made" Python code,
2- Identify concrete issues including syntax errors, logical bugs,  missing documentation,
3- Create a Refactoring Plan that outlines specific, actionable steps to fix the code .


Constraints : 
- Do NOT modify code.
- Do NOT write fixes.
- Do NOT suggest speculative changes.
- Do NOT invent files, functions, or errors.


Inputs : 
- Python code 
- Static analysis results from "tools.analyze_file()" (optional)


Outputs: 
JSON files in the forme of 
{
  "files_analyzed": [
    {
      "file": "relative/path.py",
      "pylint_score": 0.0,
      "total_issues": 0
    }
  ],
  "issues": [
    {
      "file": "relative/path.py",
      "line": null,
      "type": "bug | style | design | test",
      "source": "code | pylint",
      "description": "Clear factual description of the issue"
    }
  ],
  "refactoring_plan": [
    {
      "step": 1,
      "file": "relative/path.py",
      "action": "High-level action to perform (no code)"
    }
  ],
  "confidence": "high | medium | low"
}


Available tools :
read_file(file_path)
list_python_files(directory)
analyze_file(file_path)
analyze_directory(directory)
get_analysis_summary(results)


Failure Behavior : 
If information is missing, Then DO NOT hallucinate AND Return empty arrays and set confidence to "low"




"""
                # here is the analysis output:{}

        orchestre_additional_prompt= f"""
        here is the code :def(A,b)return a+B;
        here is the path of the file :prompts/auditor.txt
        """
        prompt+=orchestre_additional_prompt

        response = self.llm.invoke(prompt)
        # add the log 
        print(response.content)


# Example usage
agent = AuditorAgent()
agent.analyse("def add(a,b): return a+b")
