import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from ...tools.file_tools import FileTools

load_dotenv()

class FixerAgent:
   def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

        self.fl = FileTools()
        self.first_prompt = self.fl.read_file(self.fl,"prompts/fixer.txt")
        # self.retry_prompt = "Fix ONLY what is needed to make the failing tests pass, without violating the refactoring plan"


   def fix(self,refactoring_plan,originalcode,filepath,test_results=None):
       prompt=self.first_prompt
       prompt+= f"""Refactoring plan (JSON):\n
           {refactoring_plan}

Original code:\n
{originalcode} \n
file:{filepath}"""

       if test_results :
           mode="retry"
       else:
           mode="first"
       if (mode=="retry"):
           prompt+=f"""
           In case of Retry:\n
PYTEST FAILURES:
{test_results["failures"]}
           """
           
               
       response = self.llm.invoke(prompt)
    #    print(f"//////prompt/////\n")
    #    print(prompt)
       print(f"//////content////////////////////////////////////////\n")
       print(response.content)
       print(f"/////////////////////////////////////////////////////\n")
       return json.loads(response.content)


