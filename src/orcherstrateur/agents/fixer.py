import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.logger import log_experiment, ActionType
load_dotenv()
class FixerAgent:
    def __init__(self):
        # self.llm=ChatGoogleGenerativeAI(
        #     model="Gemini_2.5_flash",
        #     api_key=os.getenv("GOOGLE_API_KEY"),
        # )
        pass 
    def fix(self,filepath):
        prompt=''
        #get the prompt of the prompt engineer
        #and modify it so i can add what i need 
        #once i get the prompt i will call the llm and after that i
        #use the log to save the state for the scientific studyy
        fixer_response=self.llm.invoke(prompt)
        # log_experiment(
        #     agent_name="Auditor",
        #     model_used="Gemini_2.5_flash",
        #     action=ActionType.ANALYSIS,
        #     details={
        #         "input_prompt":prompt,
        #         "output_response":auditor_response.content,
        #         "file proccessed":filepath
                
        #     },
        #     status="Success"
        # )
        
        