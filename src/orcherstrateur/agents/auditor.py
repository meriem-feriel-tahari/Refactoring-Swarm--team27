import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from ...tools.file_tools import FileTools

load_dotenv()      
class AuditorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
        self.fl=FileTools()
        self.system_prompt=self.fl.read_file("prompts/auditor.txt")

    def analyse(self):
       
        prompt=self.system_prompt
        
        
        orchestre_additional_prompt= f"""
         here is the code :{self.fl.read_file("sandbox/code.py")};

        here is the path of the file :sandbox/code.py
        """
        prompt+=orchestre_additional_prompt

        response = self.llm.invoke(prompt)
        # add the log 
        print(response.content)
        return response.content



