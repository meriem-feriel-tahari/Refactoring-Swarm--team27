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
        self.first_prompt = self.fl.read_file("prompts/fixer.txt")
        self.retry_prompt = "Fix ONLY what is needed to make the failing tests pass, without violating the refactoring plan"


   def fix(self,refactoring_plan,originalcode,filepath,test_results=None):
       if test_results :
           mode="retry"
       else:
           mode="first"
       if (mode=="first"):
            prompt=self.first_prompt
            prompt+= f"""Refactoring plan (JSON):\n
           {refactoring_plan}

Original code:\n
{originalcode} \n
file:{filepath}

Apply the plan strictly and return the corrected code only.

        """
       else:
           prompt =self.retry_prompt
           prompt+=f"""
             REFACTORING PLAN:
{refactoring_plan}

PYTEST FAILURES:
{test_results["failures"]}

CURRENT CODE:
{originalcode}

OUTPUT:
Return ONLY the corrected code for the file.
Do NOT include explanations.
           """
           
               
       response = self.llm.invoke(prompt)
       print(response.content)
       return response.content


