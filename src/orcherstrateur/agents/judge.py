import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from src.tools.file_tools import FileTools
load_dotenv()

class JudgeAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
        fl=FileTools()
        self.prompt=fl.read_file(fl,"prompts/judgee.txt")

    def judge(self,current_code,filename):
        prompt=self.prompt
        prompt+=f"""
        The current code to test:\n{current_code}\n
        file name:{filename}
        """
        
        
      
        response = self.llm.invoke(prompt)
       

        return json.loads(response.content)
       