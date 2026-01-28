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
        self.system_prompt = self.fl.read_file("prompts/fixer.txt")


   def fix(self,refactoring_plan,originalcode):
         prompt="""ROLE:
You are the FIXER agent in the "Refactoring Swarm" system.

TASK:
1. Receive a refactoring plan produced by the Auditor.
2. Apply the plan step by step to the provided Python code.
3. Produce the corrected version of the code.

CONSTRAINTS:
- Apply ONLY the changes explicitly listed in the refactoring plan.
- Follow the plan EXACTLY, step by step.
- Do NOT introduce additional changes or improvements.
- Do NOT refactor beyond the given plan.
- Do NOT invent new functions or files.
- Do NOT modify tests unless explicitly instructed.
- Preserve unrelated code exactly as-is.

OUTPUT RULES:
- Return ONLY the final corrected Python code.
- Do NOT include explanations.
- Do NOT include markdown.
- Do NOT include JSON.
- The output must be valid Python code only."""

         prompt+= f"""Refactoring plan (JSON):
           {refactoring_plan}

Original code:
{originalcode}

Apply the plan strictly and return the corrected code only.

        """
         response = self.llm.invoke(prompt)
        # add the log 
         print(response.content)
         return response.content


