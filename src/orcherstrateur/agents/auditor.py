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
        self.system_prompt=self.fl.read_file(self.fl,"prompts/auditor.txt")

    def analyze(self,content,pylint_report,filepath):
       
        prompt=self.system_prompt
        
        
        orchestre_additional_prompt= f"""
         the code :\n{content};\n
        
         the file : {filepath};\n
         the pylint_report:\n {pylint_report}\n
        """
        prompt+=orchestre_additional_prompt

        response = self.llm.invoke(prompt)
        
        print(response.content)
        return response.content



